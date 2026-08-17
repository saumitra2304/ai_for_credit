import sys
from openai import OpenAI

# Force UTF-8 encoding for console output on Windows
sys.stdout.reconfigure(encoding='utf-8')

# Connect to your local vLLM instance
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY"  # No key needed locally
)
response = client.chat.completions.create(
    model="neuralmagic/gemma-2-2b-it-FP8",
    messages=[
        {"role": "user", "content": "You are a helpful assistant.\n\nWhat is the capital of France?"}
    ],
    temperature=0.7
)
print(response.choices[0].message.content)
