"""
Google Trends Integration - Lấy từ khóa trending từ Google Trends.

Sử dụng RSS feed công khai của Google Trends để lấy các từ khóa
đang thịnh hành tại Việt Nam, sau đó dùng các từ khóa này để tìm
bài viết trên Threads.

Flow:
1. Lấy trending keywords từ Google Trends RSS (geo=VN)
2. Dùng Playwright tìm bài viết trên Threads theo từ khóa
3. Trả về danh sách bài viết phù hợp
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from urllib.parse import quote_plus

import requests
from playwright.sync_api import (
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)

from utils.console import print_step, print_substep

# Google Trends daily trending RSS endpoint
_GOOGLE_TRENDS_RSS_URL = "https://trends.google.com/trends/trendingsearches/daily/rss"
_RSS_REQUEST_TIMEOUT = 15

# Playwright settings (reuse from trending.py)
_PAGE_LOAD_TIMEOUT_MS = 30_000
_CONTENT_WAIT_MS = 3_000
_SCROLL_ITERATIONS = 3

_BROWSER_VIEWPORT = {"width": 1280, "height": 900}
_BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)
_BROWSER_LOCALE = "vi-VN"

# Threads search URL template
_THREADS_SEARCH_URL = "https://www.threads.net/search?q={query}&serp_type=default"


class GoogleTrendsError(Exception):
    """Lỗi khi lấy dữ liệu từ Google Trends."""


def get_google_trending_keywords(
    geo: str = "VN",
    limit: int = 10,
) -> List[Dict[str, str]]:
    """Lấy danh sách từ khóa trending từ Google Trends RSS feed.

    Args:
        geo: Mã quốc gia (mặc định: VN cho Việt Nam).
        limit: Số từ khóa tối đa cần lấy.

    Returns:
        Danh sách dict chứa ``{title, traffic, news_url}``.

    Raises:
        GoogleTrendsError: Nếu không thể lấy dữ liệu từ Google Trends.
    """
    print_substep(
        f"🔍 Đang lấy từ khóa trending từ Google Trends (geo={geo})...",
        style="bold blue",
    )

    url = f"{_GOOGLE_TRENDS_RSS_URL}?geo={geo}"
    try:
        response = requests.get(url, timeout=_RSS_REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise GoogleTrendsError(
            f"Không thể kết nối Google Trends RSS: {exc}"
        ) from exc

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as exc:
        raise GoogleTrendsError(
            f"Không thể parse Google Trends RSS XML: {exc}"
        ) from exc

    # RSS structure: <rss><channel><item>...</item></channel></rss>
    # Google Trends uses ht: namespace for traffic data
    namespaces = {"ht": "https://trends.google.com/trends/trendingsearches/daily"}

    keywords: List[Dict[str, str]] = []
    for item in root.iter("item"):
        if len(keywords) >= limit:
            break

        title_elem = item.find("title")
        title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
        if not title:
            continue

        # Approximate traffic (e.g., "200,000+")
        traffic_elem = item.find("ht:approx_traffic", namespaces)
        traffic = traffic_elem.text.strip() if traffic_elem is not None and traffic_elem.text else ""

        # News item URL (optional)
        news_url = ""
        news_item = item.find("ht:news_item", namespaces)
        if news_item is not None:
            news_url_elem = news_item.find("ht:news_item_url", namespaces)
            news_url = (
                news_url_elem.text.strip()
                if news_url_elem is not None and news_url_elem.text
                else ""
            )

        keywords.append({
            "title": title,
            "traffic": traffic,
            "news_url": news_url,
        })

    if not keywords:
        raise GoogleTrendsError(
            f"Không tìm thấy từ khóa trending nào từ Google Trends (geo={geo})."
        )

    kw_preview = ", ".join(k["title"][:30] for k in keywords[:5])
    suffix = "..." if len(keywords) > 5 else ""
    print_substep(
        f"✅ Tìm thấy {len(keywords)} từ khóa trending: {kw_preview}{suffix}",
        style="bold green",
    )
    return keywords


def search_threads_by_query(
    query: str,
    max_threads: int = 10,
) -> List[Dict[str, str]]:
    """Tìm bài viết trên Threads theo từ khóa bằng Playwright.

    Mở trang tìm kiếm Threads và trích xuất bài viết từ kết quả.

    Args:
        query: Từ khóa tìm kiếm.
        max_threads: Số bài viết tối đa cần lấy.

    Returns:
        Danh sách thread dicts: ``{text, username, permalink, shortcode, keyword}``.
    """
    import re

    search_url = _THREADS_SEARCH_URL.format(query=quote_plus(query))
    threads: List[Dict[str, str]] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport=_BROWSER_VIEWPORT,
            user_agent=_BROWSER_USER_AGENT,
            locale=_BROWSER_LOCALE,
        )
        page = context.new_page()

        try:
            page.goto(search_url, timeout=_PAGE_LOAD_TIMEOUT_MS)
            page.wait_for_load_state("domcontentloaded", timeout=_PAGE_LOAD_TIMEOUT_MS)
            page.wait_for_timeout(_CONTENT_WAIT_MS)

            # Scroll to load more content
            for _ in range(_SCROLL_ITERATIONS):
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                page.wait_for_timeout(1000)

            # Extract posts from search results
            seen_shortcodes: set = set()
            post_links = page.query_selector_all('a[href*="/post/"]')

            for link in post_links:
                if len(threads) >= max_threads:
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

                    # Username from URL: /@username/post/...
                    user_match = re.search(r"/@([^/]+)/post/", href)
                    username = user_match.group(1) if user_match else "unknown"

                    # Get post text from parent container
                    text = _get_post_text_from_link(link)
                    if not text or len(text) < 10:
                        continue

                    permalink = (
                        f"https://www.threads.net{href}"
                        if href.startswith("/")
                        else href
                    )
                    threads.append({
                        "text": text,
                        "username": username,
                        "permalink": permalink,
                        "shortcode": shortcode,
                        "keyword": query,
                    })
                except Exception:
                    continue

        except PlaywrightTimeoutError:
            print_substep(
                f"⚠️ Timeout khi tìm kiếm Threads cho từ khóa: {query}",
                style="bold yellow",
            )
        except Exception as exc:
            print_substep(
                f"⚠️ Lỗi tìm kiếm Threads cho '{query}': {exc}",
                style="bold yellow",
            )
        finally:
            browser.close()

    return threads


def _get_post_text_from_link(link_handle) -> str:
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
                return el.parentElement
                    ? el.parentElement.parentElement || el.parentElement
                    : el;
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


def get_threads_from_google_trends(
    geo: str = "VN",
    max_keywords: int = 5,
    max_threads_per_keyword: int = 10,
) -> List[Dict[str, str]]:
    """Lấy bài viết Threads dựa trên từ khóa trending từ Google Trends.

    Kết hợp Google Trends + Threads search:
    1. Lấy từ khóa trending từ Google Trends
    2. Tìm bài viết trên Threads theo từng từ khóa

    Args:
        geo: Mã quốc gia cho Google Trends.
        max_keywords: Số từ khóa tối đa cần duyệt.
        max_threads_per_keyword: Số bài viết tối đa từ mỗi từ khóa.

    Returns:
        Danh sách thread dicts.

    Raises:
        GoogleTrendsError: Nếu không lấy được từ khóa từ Google Trends.
    """
    print_step("🌐 Đang lấy bài viết từ Threads dựa trên Google Trends...")

    keywords = get_google_trending_keywords(geo=geo, limit=max_keywords)
    all_threads: List[Dict[str, str]] = []

    for kw in keywords:
        keyword_title = kw["title"]
        print_substep(
            f"  🔎 Đang tìm trên Threads: '{keyword_title}'...",
            style="bold blue",
        )
        found = search_threads_by_query(
            query=keyword_title,
            max_threads=max_threads_per_keyword,
        )
        all_threads.extend(found)
        print_substep(
            f"  📝 '{keyword_title}': {len(found)} bài viết",
            style="bold blue",
        )

        # Stop early if we have enough threads
        if len(all_threads) >= max_threads_per_keyword * 2:
            break

    print_substep(
        f"✅ Tổng cộng {len(all_threads)} bài viết từ Google Trends keywords",
        style="bold green",
    )
    return all_threads
