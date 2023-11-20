from openai import OpenAI
from utils import settings
from utils.console import print_step, print_substep
from utils.posttextparser import posttextparser
from utils.timeout import timeout
# import math
import sys
import tiktoken


def is_valid_ai_response(string: str) -> bool:
    lower_string = string.lower()
    return not (
        lower_string.startswith('i can\'t') or 
        lower_string.startswith("i cannot") or 
        lower_string.startswith("i can not") or
        lower_string.startswith("sorry") or
        lower_string.startswith("i\'m sorry") or
        lower_string.startswith("i am sorry") or
        lower_string.startswith("i apologize")
    ) and len(lower_string) > 150

def remove_ai_extras(string: str) -> str:
    lines=string.splitlines()
    first_line=lines[0].lower().strip()
    if "here" in first_line and first_line.endswith('story:'):
        return "\n".join(lines[1:]).strip()
    return string

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def ai_rewrite_story(story_text):
    MAX_RETRIES=int(settings.config['ai']['openai_rewrite_retries'])
    MAX_PART_REWORD_TOKENS=int(settings.config['ai']['openai_rewrite_chunk_max_tokens'])
    longer_or_shorter = "longer" if float(settings.config['ai']['openai_rewrite_length']) > 1.0 else "shorter"
    print_step(
        f"Using OpenAI {settings.config['ai']['openai_model']} to rewrite the content..."
    )
    client = OpenAI(
        base_url=settings.config["ai"]["openai_api_base"],
        api_key=settings.config["ai"]["openai_api_key"],
        timeout=90
    )
    model_name = settings.config["ai"]["openai_model"]
    ai_system_message = f"The user will present you with a story. You must rewrite the story in first person. Rewrite the story to the same or {longer_or_shorter} length, keeping the same details, but make it extremely addictive to listen to, with many cliffhangers. Use language and words that the average social media user can understand. Avoid using swear words and words that may be unallowed, like: gun, drug, shoot, kill, suicide, etc."
    ai_user_message = "Rewrite this story to be more addictive. Your output will be published, so make sure to only output the new story."
    ai_assistant_message = "Sure! What is the story?"
    base_tokens = num_tokens_from_string(ai_system_message+ai_user_message+ai_assistant_message, model_name)
    parts=posttextparser(story_text)
    rewritten_parts=[]
    while len(parts) > 0:
        tmp_part_list=[]
        tmp_tokens = base_tokens
        while tmp_tokens < MAX_PART_REWORD_TOKENS and len(parts) > 0:
            next_part=parts.pop(0)
            tmp_tokens+=num_tokens_from_string(next_part, model_name)
            tmp_part_list.append(next_part)
        if len(tmp_part_list) > 0:
            joined_part_list=" ".join(tmp_part_list)
            part_chat_history = [
                {"role":"system", "content":ai_system_message},
                {"role":"user", "content":ai_user_message},
                {"role":"assistant", "content":ai_assistant_message},
                {"role":"user", "content":joined_part_list}
            ]
            joined_part_list_tokens=num_tokens_from_string(joined_part_list, model_name) * float(settings.config['ai']['openai_rewrite_length'])
            ai_part_message=''
            part_retry_num=0
            while part_retry_num <= MAX_RETRIES and num_tokens_from_string(ai_part_message, model_name) < joined_part_list_tokens:
                part_retry_text = '' if part_retry_num <= 0 else f"[Retry #{part_retry_num}]"
                try:
                    with timeout(seconds=60):
                        part_log_message = f"{part_retry_text} Making request to OpenAI to make the portion of the story longer...".strip() if ai_part_message != '' else f"{part_retry_text} Making request to OpenAI to reword a portion of the story...".strip()
                        print_substep(part_log_message)
                        # print(part_chat_history)
                        ai_part_response = client.chat.completions.create(
                            model=model_name,
                            messages=part_chat_history,
                            temperature=0.9, # very creative
                            timeout=60
                            # max_tokens=math.ceil(num_tokens_from_string(ai_selftext, model_name)*2.5) # 2.5 because it counts all the messages in history
                        )
                        ai_part_message_updated=remove_ai_extras(ai_part_response.choices[0].message.content)
                        old_part_tokens = num_tokens_from_string(ai_part_message, model_name)
                        new_part_tokens = num_tokens_from_string(ai_part_message_updated, model_name)
                        if new_part_tokens > old_part_tokens and is_valid_ai_response(ai_part_message_updated):
                            ai_part_message = ai_part_message_updated
                            print_substep(f"Got AI response: {ai_part_message}")
                            part_chat_history.append({"role":"assistant", "content":ai_part_message})
                            part_chat_history.append({"role":"user", "content":"Make the story longer/more detailed"})
                except KeyboardInterrupt:
                    sys.exit(1)
                except Exception as e:
                    print_substep(str(e), style="bold red")
                    pass
                part_retry_num+=1
            if not bool(ai_part_message):
                if bool(settings.config['ai']['openai_retry_fail_error']):
                    raise ValueError('AI rewrite failed')
                else:
                    ai_part_message = joined_part_list
            rewritten_parts.append(ai_part_message)
            tmp_part_list.clear()
    try:
        joined_rewritten_parts=" ".join(rewritten_parts)
        chat_history=[
            {"role":"system", "content":"The user will present you with a story. You must output the same story with any issues fixed, and possibly expand the story to be longer. Your goal is to output a story that can be read to an audience. This story must make sense and have a lot of cliffhangers, to keep the audience interested. Keep the same story details and possibly add more. Avoid using swear words and words that may be unallowed, like: gun, drug, shoot, kill, suicide, etc. Make your story about 5 minutes in spoken length."},
            {"role":"user", "content":"I have a story for you to review. Your output will be published, so make sure to only output the story. Do NOT include any extra information in your response besides the story."},
            {"role":"assistant", "content":ai_assistant_message},
            {"role":"user", "content":" ".join(rewritten_parts)}
        ]
        joined_rewritten_parts_tokens=num_tokens_from_string(joined_rewritten_parts, model_name)
        ai_message=''
        retry_num=0
        while retry_num <= MAX_RETRIES and num_tokens_from_string(ai_message, model_name) < joined_rewritten_parts_tokens:
            retry_text = '' if retry_num <= 0 else f"[Retry #{retry_num}]"
            try:
                with timeout(seconds=90):
                    log_message = f"{retry_text} Making request to OpenAI to make the whole story longer...".strip() if ai_message != '' else f"{retry_text} Making request to OpenAI to finalize the whole story...".strip()
                    print_substep(log_message)
                    # print(chat_history)
                    ai_response = client.chat.completions.create(
                        model=model_name,
                        messages=chat_history,
                        temperature=0.9, # very creative
                        timeout=90
                        # max_tokens=math.ceil(num_tokens_from_string(ai_selftext, model_name)*2.5) # 2.5 because it counts all the messages in history
                    )
                    ai_message_updated=remove_ai_extras(ai_response.choices[0].message.content)
                    old_tokens = num_tokens_from_string(ai_message, model_name)
                    new_tokens = num_tokens_from_string(ai_message_updated, model_name)
                    if new_tokens > old_tokens and is_valid_ai_response(ai_message_updated):
                        ai_message = ai_message_updated
                        print_substep(f"Got AI response: {ai_message}")
                        chat_history.append({"role":"assistant", "content":ai_message})
                        chat_history.append({"role":"user", "content":"Make the story longer/more detailed"})
            except KeyboardInterrupt:
                sys.exit(1)
            except Exception as e:
                print_substep(str(e), style="bold red")
                pass
            retry_num+=1
        return ai_message if ai_message else joined_rewritten_parts
    except:
        return " ".join(rewritten_parts)
    