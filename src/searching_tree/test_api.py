import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env file")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

completion = client.chat.completions.create(
    extra_headers={
        # Optional: add your site info for rankings
        # "HTTP-Referer": "<YOUR_SITE_URL>",
        # "X-Title": "<YOUR_SITE_NAME>",
    },
    extra_body={},
    model="deepseek/deepseek-chat-v3-0324:free",
    messages=[
        {
            "role": "user",
            "content": "What is the meaning of life?"
        }
    ]
)
print(completion.choices[0].message.content)