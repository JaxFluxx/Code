import ollama

stream = ollama.chat(
    model="qwen3.6:latest",
    messages=[
        {"role": "user", "content": "你好，请用中文介绍一下你自己"}
    ],
    stream=True
)

for chunk in stream:
    print(chunk["message"]["content"], end="", flush=True)