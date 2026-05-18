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
            "role": "assistant",
            "content": "好的，我是编程专家，并且话非常多，你要问什么？"
        },
        {
            "role": "user",
            "content": "输出1-10的数字，使用Python代码"
        }
    ],
    stream = True #流式输出

)

#print(response.choices[0].message.content)
for chunk in response:
    print(
        chunk.choices[0].delta.content,
        end = "",
        flush = True
    )
