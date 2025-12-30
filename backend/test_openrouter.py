import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

response = client.chat.completions.create(
    model="mistralai/mistral-7b-instruct",
    messages=[
        {"role": "system", "content": "You are a helpful programming tutor."},
        {"role": "user", "content": "Explain IndexError in Python for a beginner."}
    ],
)

print(response.choices[0].message.content)
