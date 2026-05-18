from openai import OpenAI

client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

response = client.chat.completions.create(
    model="qwen-max",
    messages=[
        {
            "role": "system",
            "content": "你是一个Python编程专家，不说废话，简单回答"
        },
        {
            "role": "user",
            "content": "输出1-10的数字，使用Python代码"
        }
    ]
)

print(response.choices[0].message.content)