import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

SYSTEM_PROMPT = """
تو MyGPT هستی؛ یک دستیار هوش مصنوعی حرفه‌ای داخل تلگرام.

قوانین:
- فارسی را طبیعی و دوستانه صحبت کن.
- اگر کاربر انگلیسی صحبت کرد، انگلیسی پاسخ بده.
- پاسخ‌ها را واضح و مرتب ارائه کن.
- برای آموزش‌ها مرحله‌به‌مرحله توضیح بده.
- اگر چیزی را نمی‌دانی، حدس نزن.
- از اطلاعات ساختگی خودداری کن.
"""


def ask_ai(history):
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    messages.extend(history)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content
