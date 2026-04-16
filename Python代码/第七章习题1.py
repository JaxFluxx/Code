# 导入Pandas库
import pandas as pd

# 1.1 读取与写入表格
# 打开CSV文件
titanic = pd.read_csv(r"D:\hello_py\pythonProject\Mzitu\titanic.csv")

# 存储Excel文件
titanic.to_excel("titanic.xlsx", sheet_name="passengers", index=False)

# 打开Excel文件
titanic = pd.read_excel("titanic.xlsx", sheet_name="passengers")

# 1.2 查看DataFrame数据及类型
print(titanic.head(8))  # 显示前8行数据
print(titanic.tail(10))  # 显示后10行数据
print(titanic.dtypes)   # 显示每列的数据类型
print(titanic.info())   # 显示DataFrame的详细信息

# 2.1 DataFrame数据选择
# 选择1列
ages = titanic["Age"]
print(ages.head())  # 显示Age列的前几行数据
print(type(titanic["Age"]))  # 显示Age列的数据类型
print(titanic["Age"].shape)  # 显示Age列的形状

# 选择多列
age_sex = titanic[["Age", "Sex"]]
print(type(age_sex))  # 显示age_sex的数据类型
print(age_sex.shape)  # 显示age_sex的形状

# 2.2 数据筛选
# 选出35岁以上的乘客的所有信息
above_35 = titanic[titanic["Age"] > 35]

# 选出级别为2级和3级所有乘客的信息
class_23 = titanic[titanic["Pclass"].isin([2, 3])]

# 选出已知年龄的乘客数据（选出年龄不为缺失值的乘客）
age_no_na = titanic[titanic["Age"].notna()]

# 只选出35岁以上乘客的姓名
above_35_names = titanic[(titanic["Age"] > 35) & ("Name" in titanic.columns)]

# 对第10到25行和第3到5列感兴趣
print(titanic.iloc[9:25, 2:5])

# 对第1到4行的第4列赋值“anonymous”
titanic.iloc[0:4, 3] = "anonymous"

# 3 创建新列
# 创建新的一列
titanic["age02"] = titanic["age"] * 1.

# 更改列标签名
titanic = titanic.rename(columns={
    "name": "Xingming",
    "room": "Fangjian",
    "sex": "Xingbie"
})

# 将列名转为小写
titanic.columns = map(str.lower, titanic.columns)

# 4 计算并总结数据
# 求某列的平均值
average_age = titanic["Age"].mean()

# 求多列的平均值
average_values = titanic[["列名1", "列名2"]].mean()

# 求平均值、中位数等信息
print(titanic.describe())  # 显示DataFrame的统计摘要

# 分组统计
# 男性和女性泰坦尼克号乘客的平均年龄
average_age_by_sex = titanic.groupby("Sex")["Age"].mean()

# 每种性别和舱位等级组合的平均票价
average_fare_by_sex_class = titanic.groupby(["Sex", "Pclass"])["Fare"].mean()

# 按类别计算记录数
passenger_count_by_class = titanic["Pclass"].value_counts()

# 5 DataFrame数据重塑布局
# 根据乘客的年龄对泰坦尼克号数据进行排序
sorted_by_age = titanic.sort_values(by="Age")

# 根据舱位等级和年龄按降序对泰坦尼克号数据进行排序
sorted_by_class_and_age = titanic.sort_values(by=['Pclass', 'Age'], ascending=False)