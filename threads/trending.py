"""
Threads Trending Scraper - Lấy bài viết từ mục "Trending now" trên Threads.

Threads API chính thức không cung cấp endpoint cho trending topics.
Module này sử dụng Playwright để scrape nội dung trending từ giao diện web Threads.

Flow:
1. Mở trang tìm kiếm Threads (https://www.threads.net/search)
2. Trích xuất trending topic links
3. Truy cập từng topic để lấy danh sách bài viết
4. Truy cập bài viết để lấy replies (nếu cần)
"""

import re
from typing import Dict, List, Optional, Tuple

from playwright.sync_api import (
    Page,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)

from utils.console import print_step, print_substep

THREADS_SEARCH_URL = "https://www.threads.net/search"
_PAGE_LOAD_TIMEOUT_MS = 30_000
_CONTENT_WAIT_MS = 3_000


class TrendingScrapeError(Exception):
    """Lỗi khi scrape trending content từ Threads."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_topic_links(page: Page, limit: int) -> List[Dict[str, str]]:
    """Extract trending topic links from the search page DOM."""
    topics: List[Dict[str, str]] = []
    elements = page.query_selector_all('a[href*="/search?q="]')
    for elem in elements:
        if len(topics) >= limit:
            break
        try:
            href = elem.get_attribute("href") or ""
            text = elem.inner_text().strip()
            if not text or not href:
                continue
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            title = lines[0] if lines else ""
            if not title:
                continue
            url = f"https://www.threads.net{href}" if href.startswith("/") else href
            topics.append({"title": title, "url": url})
        except Exception:
            continue
    return topics


def _extract_post_links(page: Page, limit: int) -> List[Dict[str, str]]:
    """Extract thread post data from a page containing post links."""
    threads: List[Dict[str, str]] = []
    seen_shortcodes: set = set()

    post_links = page.query_selector_all('a[href*="/post/"]')
    for link in post_links:
        if len(threads) >= limit:
            break
        try:
            href = link.get_attribute("href") or ""
            sc_match = re.search(r"/post/([A-Za-z0-9_-]+)", href)
            if not sc_match:
                continue
            shortcode = sc_match.group(1)
            if shortcode in seen_shortcodes:
                continue
            seen_shortcodes.add(shortcode)

            # Username from URL  /@username/post/...
            user_match = re.search(r"/@([^/]+)/post/", href)
            username = user_match.group(1) if user_match else "unknown"

            # Walk up the DOM to find a container with the post text
            text = _get_post_text(link)
            if not text or len(text) < 10:
                continue

            permalink = (
                f"https://www.threads.net{href}" if href.startswith("/") else href
            )
            threads.append(
                {
                    "text": text,
                    "username": username,
                    "permalink": permalink,
                    "shortcode": shortcode,
                }
            )
        except Exception:
            continue
    return threads


def _get_post_text(link_handle) -> str:
    """Walk up the DOM from a link element to extract post text content."""
    try:
        container = link_handle.evaluate_handle(
            """el => {
                let node = el;
                for (let i = 0; i < 10; i++) {
                    node = node.parentElement;
                    if (!node) return el.parentElement || el;
                    const text = node.innerText || '';
                    if (text.length > 30 && (
                        node.getAttribute('role') === 'article' ||
                        node.tagName === 'ARTICLE' ||
                        node.dataset && node.dataset.testid
                    )) {
                        return node;
                    }
                }
                return el.parentElement ? el.parentElement.parentElement || el.parentElement : el;
            }"""
        )
        raw = container.inner_text().strip() if container else ""
    except Exception:
        return ""

    if not raw:
        return ""

    # Clean: remove short metadata lines (timestamps, UI buttons, etc.)
    _skip = {"Trả lời", "Thích", "Chia sẻ", "Repost", "Quote", "...", "•"}
    cleaned_lines: list = []
    for line in raw.split("\n"):
        line = line.strip()
        if not line or len(line) < 3:
            continue
        if line in _skip:
            continue
        # Skip standalone @username lines
        if line.startswith("@") and " " not in line and len(line) < 30:
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def _extract_replies(page: Page, limit: int) -> List[Dict[str, str]]:
    """Extract replies from a thread detail page."""
    replies: List[Dict[str, str]] = []

    # Scroll to load more replies
    for _ in range(5):
        page.evaluate("window.scrollBy(0, window.innerHeight)")
        page.wait_for_timeout(1000)

    articles = page.query_selector_all('div[role="article"], article')
    for idx, article in enumerate(articles):
        if idx == 0:
            continue  # Skip main post
        if len(replies) >= limit:
            break
        try:
            text = article.inner_text().strip()
            if not text or len(text) < 5:
                continue

            # Username
            username_link = article.query_selector('a[href^="/@"]')
            username = "unknown"
            if username_link:
                href = username_link.get_attribute("href") or ""
                match = re.match(r"/@([^/]+)", href)
                username = match.group(1) if match else "unknown"

            # Clean text
            _skip = {"Trả lời", "Thích", "Chia sẻ", "Repost", "...", "•"}
            lines = [
                l.strip()
                for l in text.split("\n")
                if l.strip() and len(l.strip()) > 3 and l.strip() not in _skip
            ]
            clean_text = "\n".join(lines)
            if clean_text:
                replies.append({"text": clean_text, "username": username})
        except Exception:
            continue
    return replies


def _scroll_page(page: Page, times: int = 2) -> None:
    """Scroll down to trigger lazy-loading content."""
    for _ in range(times):
        page.evaluate("window.scrollBy(0, window.innerHeight)")
        page.wait_for_timeout(1000)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_trending_threads(
    max_topics: int = 5,
    max_threads_per_topic: int = 10,
) -> List[Dict[str, str]]:
    """Lấy danh sách threads từ các trending topics trên Threads.

    Mở một phiên Playwright duy nhất, duyệt qua trending topics
    và trích xuất bài viết từ mỗi topic.

    Args:
        max_topics: Số trending topics tối đa cần duyệt.
        max_threads_per_topic: Số bài viết tối đa từ mỗi topic.

    Returns:
        Danh sách thread dicts: ``{text, username, permalink, shortcode, topic_title}``.

    Raises:
        TrendingScrapeError: Nếu không thể scrape trending.
    """
    print_step("🔥 Đang lấy bài viết từ Trending now trên Threads...")

    all_threads: List[Dict[str, str]] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            locale="vi-VN",
        )
        page = context.new_page()

        try:
            # Step 1: Navigate to search page
            page.goto(THREADS_SEARCH_URL, timeout=_PAGE_LOAD_TIMEOUT_MS)
            page.wait_for_load_state(
                "domcontentloaded", timeout=_PAGE_LOAD_TIMEOUT_MS
            )
            page.wait_for_timeout(_CONTENT_WAIT_MS)

            # Step 2: Extract trending topics
            topics = _extract_topic_links(page, limit=max_topics)
            if not topics:
                raise TrendingScrapeError(
                    "Không tìm thấy trending topics trên Threads. "
                    "Có thể Threads đã thay đổi giao diện hoặc yêu cầu đăng nhập."
                )

            topic_names = ", ".join(t["title"][:30] for t in topics[:3])
            suffix = "..." if len(topics) > 3 else ""
            print_substep(
                f"🔥 Tìm thấy {len(topics)} trending topics: {topic_names}{suffix}",
                style="bold blue",
            )

            # Step 3: Visit each topic and extract threads
            for topic in topics:
                try:
                    page.goto(topic["url"], timeout=_PAGE_LOAD_TIMEOUT_MS)
                    page.wait_for_load_state(
                        "domcontentloaded", timeout=_PAGE_LOAD_TIMEOUT_MS
                    )
                    page.wait_for_timeout(_CONTENT_WAIT_MS)
                    _scroll_page(page, times=2)

                    threads = _extract_post_links(
                        page, limit=max_threads_per_topic
                    )
                    for t in threads:
                        t["topic_title"] = topic["title"]
                    all_threads.extend(threads)

                    print_substep(
                        f"  📝 Topic '{topic['title'][:30]}': "
                        f"{len(threads)} bài viết",
                        style="bold blue",
                    )
                except PlaywrightTimeoutError:
                    print_substep(
                        f"  ⚠️ Timeout topic '{topic['title'][:30]}'",
                        style="bold yellow",
                    )
                except Exception as exc:
                    print_substep(
                        f"  ⚠️ Lỗi topic '{topic['title'][:30]}': {exc}",
                        style="bold yellow",
                    )

        except TrendingScrapeError:
            raise
        except PlaywrightTimeoutError as exc:
            raise TrendingScrapeError(
                "Timeout khi tải trang Threads. Kiểm tra kết nối mạng."
            ) from exc
        except Exception as exc:
            raise TrendingScrapeError(
                f"Lỗi khi scrape trending: {exc}"
            ) from exc
        finally:
            browser.close()

    print_substep(
        f"✅ Tổng cộng {len(all_threads)} bài viết từ trending",
        style="bold green",
    )
    return all_threads


def scrape_thread_replies(
    thread_url: str, limit: int = 50
) -> List[Dict[str, str]]:
    """Lấy replies của một thread bằng cách scrape trang web.

    Sử dụng khi không thể dùng Threads API chính thức
    (ví dụ thread không thuộc user đã xác thực).

    Args:
        thread_url: URL của thread trên Threads.
        limit: Số replies tối đa.

    Returns:
        Danh sách reply dicts: ``{text, username}``.
    """
    print_substep(f"💬 Đang lấy replies từ: {thread_url[:60]}...")

    replies: List[Dict[str, str]] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            locale="vi-VN",
        )
        page = context.new_page()

        try:
            page.goto(thread_url, timeout=_PAGE_LOAD_TIMEOUT_MS)
            page.wait_for_load_state(
                "domcontentloaded", timeout=_PAGE_LOAD_TIMEOUT_MS
            )
            page.wait_for_timeout(_CONTENT_WAIT_MS)

            replies = _extract_replies(page, limit=limit)
        except PlaywrightTimeoutError:
            print_substep(
                "⚠️ Timeout khi tải thread", style="bold yellow"
            )
        except Exception as exc:
            print_substep(
                f"⚠️ Lỗi lấy replies: {exc}", style="bold yellow"
            )
        finally:
            browser.close()

    print_substep(f"💬 Đã lấy {len(replies)} replies", style="bold blue")
    return replies
