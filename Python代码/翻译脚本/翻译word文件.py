from docx import Document
import argostranslate.package
import argostranslate.translate

# 加载已经安装的语言包
argostranslate.translate.load_installed_packages()

# 获取源语言（英文）和目标语言（中文）
from_lang = argostranslate.translate.get_languages()[1]  # English
to_lang = argostranslate.translate.get_languages()[0]    # Chinese

# 获取翻译对象
translation = from_lang.get_translation(to_lang)

# 读取Word文档
input_file = r"/Users/jia/Desktop/学习/科研/独立论文部分/Paper_House price prediction.docx"  # 使用原始字符串避免路径问题
output_file = r"/Users/jia/Desktop/学习/科研/独立论文部分/Paper_House price prediction111.docx"

doc = Document(input_file)

# 翻译每一段文本
for para in doc.paragraphs:
    if para.text.strip():  # 只翻译非空的段落
        translated_text = translation.translate(para.text)  # 翻译文本
        para.text = translated_text  # 替换为翻译后的文本

# 保存翻译后的文档
doc.save(output_file)

print(f"文档已保存为：{output_file}")
