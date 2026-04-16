from openai import OpenAI

key = "你刚刚重新生成的那把新key"

print("前缀是否正常：", key.startswith("sk-"))
print("有没有空格：", " " in key)
print("首尾是否有多余空白：", key != key.strip())
print("长度：", len(key))

client = OpenAI(api_key=key)

response = client.responses.create(
    model="gpt-5.4",
    input="你好，测试一下。"
)

print(response.output_text)