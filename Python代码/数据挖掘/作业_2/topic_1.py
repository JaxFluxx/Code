# 第一题——简单的关联模式挖掘：apriori
# 把#pass替换为你自己的代码

# 需导入的包
import pandas as pd  # 导入pandas库
from mlxtend.preprocessing import TransactionEncoder  # 导入TransactionEncoder用于数据预处理
from mlxtend.frequent_patterns import apriori  # 导入apriori算法模块
from mlxtend.frequent_patterns import association_rules  # 导入association_rules模块用于生成关联规则
# from IPython.display import display  # 不再使用display模块
pd.set_option('expand_frame_repr', False)  # 设置pandas显示的选项

# 使用的数据
dataset = [['Milk', 'Onion', 'Nutmeg', 'Kidney Beans', 'Eggs', 'Yogurt'],  # 第一个交易
           ['Dill', 'Onion', 'Nutmeg', 'Kidney Beans', 'Eggs', 'Yogurt'],  # 第二个交易
           ['Milk', 'Apple', 'Kidney Beans', 'Eggs'],  # 第三个交易
           ['Milk', 'Unicorn', 'Corn', 'Kidney Beans', 'Yogurt'],  # 第四个交易
           ['Corn', 'Onion', 'Onion', 'Kidney Beans', 'Ice cream', 'Eggs']]  # 第五个交易

# 1）输出支持度至少为60%的项目和项目集

# TransactionEncoder用于将交易数据集转换为one-hot编码格式
te = TransactionEncoder()  # 创建TransactionEncoder对象
# 调用fit_transform方法对数据进行one-hot编码
te_array = te.fit(dataset).transform(dataset)  # 进行one-hot编码
# 将编码后的数据转换为pandas DataFrame
df = pd.DataFrame(te_array, columns=te.columns_)  # 创建DataFrame对象
# 使用apriori算法找到支持度至少为60%的频繁项集
frequent_itemsets = apriori(df, min_support=0.6, use_colnames=True)  # 进行apriori运算

# 2）满足规定的频繁项集
print(frequent_itemsets)  # 输出频繁项集

# 3）满足规定的频繁项集
frequent_itemsets['size'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))  # 计算每个项集的大小
# 筛选出大小为2且支持度至少为60%的项集
size_2_itemsets = frequent_itemsets[frequent_itemsets['size'] == 2]  # 筛选大小为2的项集
print(f"大小为2且支持度至少为60%的项集：\n")  # 输出提示信息
print(size_2_itemsets)  # 输出大小为2的频繁项集

# 筛选出包含'Kidney Beans'和'Eggs'的频繁项集
kidney_beans_eggs_itemsets = frequent_itemsets[frequent_itemsets['itemsets'].apply(lambda x: 'Kidney Beans' in x and 'Eggs' in x)]  # 筛选指定项集
print(f"包含'Kidney Beans', 'Eggs'的频繁项集：\n")  # 输出提示信息
print(kidney_beans_eggs_itemsets)  # 输出包含'Kidney Beans'和'Eggs'的频繁项集

# 4）输出所有关联规则
# 使用association_rules函数从频繁项集中生成关联规则
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.1)  # 生成关联规则
print(f"所有关联规则：\n")  # 输出提示信息
print(rules)  # 输出所有关联规则

# 5）输出置信度至少为0.8的关联规则
high_confidence_rules = rules[rules['confidence'] >= 0.8]  # 筛选置信度>=0.8的规则
print(f"置信度至少为0.8的关联规则：\n")  # 输出提示信息
print(high_confidence_rules)  # 输出置信度>=0.8的规则

# 6）输出满足条件的关联规则
rules['antecedents_size'] = rules['antecedents'].apply(lambda x: len(x))  # 计算前项的大小
# 筛选出满足条件的关联规则：前项大小大于等于2，置信度大于等于0.7，提升度大于等于1.2
selected_rules = rules[(rules['antecedents_size'] >= 2) & (rules['confidence'] >= 0.7) & (rules['lift'] >= 1.2)]  # 筛选规则
print(f"满足条件的关联规则：\n")  # 输出提示信息
print(selected_rules)  # 输出满足条件的关联规则
