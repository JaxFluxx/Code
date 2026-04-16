# 导入必要的库
import pandas as pd
import os  # 加这一行，用来处理路径

# 读取数据
df = pd.read_csv('/Users/jia/Desktop/学习 /科研/独立论文部分/数据/北京二手房成交_1.csv')

# 1. 保留成交年份为2022和2023的数据
df = df[df['成交年份'].isin([2022, 2023])]

# 2. 选出需要的列，并按照指定顺序排列
columns_needed = [
    '区域',     # 行政区
    '商圈',
    '小区',
    '经度',
    '纬度',
    '建筑面积（㎡）',  # 面积
    '房屋户型',       # 户型
    '户型结构',
    '所在楼层',       # 楼层
    '房屋朝向',       # 朝向
    '建筑类型',
    '建筑结构',
    '建成年代',       # 年代
    '装修情况',       # 装修
    '供暖方式',       # 供暖
    '配备电梯',       # 电梯
    '交易权属',       # 交易权属
    '房屋用途',       # 房屋用途
    '房屋年限',       # 房屋年限
    '房权所属',       # 房权所属
    '挂牌价格（万）'   # 价格
]

# 3. 只保留上述列
df = df[columns_needed]

# 4. 把价格列转成数值型
df['挂牌价格（万）'] = pd.to_numeric(df['挂牌价格（万）'], errors='coerce')

# 5. 重命名“挂牌价格（万）”为“价格”
df = df.rename(columns={'挂牌价格（万）': '价格'})

# 6. 查看处理结果
print(df.head())

# 7. 保存处理后的数据为 CSV 文件

# 指定保存路径
save_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.1.csv'

# 检查目录是否存在，如果不存在就创建
save_dir = os.path.dirname(save_path)
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# 保存文件
df.to_csv(save_path, index=False, encoding='utf-8-sig')
print('数据处理完成，已保存至', save_path)
