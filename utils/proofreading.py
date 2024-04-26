import time
import google
import google.generativeai as genai
from utils import settings


genai.configure(api_key=settings.config["ai"]["gemini_api_key"])
model = genai.GenerativeModel('gemini-pro')

prompt = """Can you please proof read this text while keeping the context the same.
Only respond with the proofread text.
If any part of the text wasn't human understandable remove it.
Here it is:
"""


def proofread_post(post):
    proofread_post = []
    for post_part in post:
        try:
            proofread_post_part = model.generate_content(prompt + post_part)
        except google.api_core.exceptions.ResourceExhausted:
            print("Resource Exhausted when proofreading the post. Sleeping for a few seconds.")
            time.sleep(62)
            proofread_post_part = model.generate_content(prompt + post_part)
        
        try:
            proofread_post_part = proofread_post_part.text
            print("Text:", proofread_post_part)
        except:
            print("Data:", proofread_post_part.prompt_feedback)
            proofread_post_part = post_part
            print("Original Text:", proofread_post_part)
        proofread_post.append(proofread_post_part)
    return proofread_post