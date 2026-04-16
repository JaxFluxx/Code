# Lab3_1_2
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.metrics import confusion_matrix

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] #苹果系统显示中文字体

data = fetch_20newsgroups()
data.target_names

# 1）选择四个特定的类别
特定类别 = ['talk.religion.misc', 'soc.religion.christian', 'sci.space', 'comp.graphics']
训练数据集 = fetch_20newsgroups(subset='train', categories=特定类别)
测试数据集 = fetch_20newsgroups(subset='test', categories=特定类别)

# 显示训练集中的第6个文本样本
print("第6个文本样本：")
print(训练数据集.data[5])

# 2）使用make_pipeline创建流水线
流水线模型 = make_pipeline(TfidfVectorizer(), MultinomialNB())
流水线模型.fit(训练数据集.data, 训练数据集.target)

# 3）生成混淆矩阵
真实标签 = 测试数据集.target
预测标签 = 流水线模型.predict(测试数据集.data)

混淆矩阵结果 = confusion_matrix(真实标签, 预测标签)

# 绘制混淆矩阵的热力图
plt.figure(figsize=(10, 7))
sns.heatmap(混淆矩阵结果, annot=True, fmt='d', cmap='Reds',
            xticklabels=训练数据集.target_names, yticklabels=训练数据集.target_names)
plt.xlabel('预测标签')
plt.ylabel('真实标签')
plt.title('混淆矩阵')
plt.show()

# 4）定义predict_category函数
def predict_category(文本):
    类别索引 = 流水线模型.predict([文本])[0]   #预测文本类别的下标
    return 训练数据集.target_names[类别索引]

# 预测以下3句话的分类
预测结果1 = predict_category('sending a payload to the ISS')
预测结果2 = predict_category('discussing islam vs atheism')
预测结果3 = predict_category('determining the screen resolution')

print(f"预测句子1: '{预测结果1}'")
print(f"预测句子2: '{预测结果2}'")
print(f"预测句子3: '{预测结果3}'")
