from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Setup Exa client
client = OpenAI(
    base_url="https://api.exa.ai",
    api_key=os.getenv("EXA_API_KEY"),
)

# Simple test
completion = client.chat.completions.create(
    model="exa-pro",
    messages=[
        {"role": "system", "content": "give explanation"},
        {"role": "user", "content": "What is the national game of India"}
    ],
    stream=True
)

# Print streaming response
for chunk in completion:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")

print()  # New line at end