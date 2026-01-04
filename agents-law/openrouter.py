from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

response = client.chat.completions.create(
    model="xiaomi/mimo-v2-flash:free",
    messages=[
        {"role": "user", "content": "Hello, how are you?"},
    ],
)

print(response.choices[0].message.content)
