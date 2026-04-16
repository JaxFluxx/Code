import pandas as pd
import numpy as np
from tqdm import tqdm

# 读取数据
data = pd.read_csv('/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.3.csv')

# 用tqdm初始化
tqdm.pandas(desc="🏗️ 处理中：建成年代填充")

# -----------------------
# 1. 替换'未知'为NaN，并用小区中位数填补建成年代
data['建成年代'] = data['建成年代'].replace('未知', np.nan)
data['建成年代'] = pd.to_numeric(data['建成年代'], errors='coerce')
data['建成年代'] = data.groupby('小区')['建成年代'].transform(lambda x: x.fillna(x.median()))

# 删除无法填补的建成年代
before_drop = len(data)
data = data.dropna(subset=['建成年代'])
after_drop = len(data)
print(f'🚮 已删除无法填补建成年代的记录数：{before_drop - after_drop}')

# -----------------------
# 2. 户型结构处理
before_drop2 = len(data)
data = data[data['户型结构'] != '暂无数据']
after_drop2 = len(data)
print(f'🚮 已删除户型结构为"暂无数据"的记录数：{before_drop2 - after_drop2}')

# -----------------------
# 3. 删除建筑类型为"暂无数据"的行
data = data[data['建筑类型'] != '暂无数据']

# 4. 删除建筑结构为"未知结构"的行
data = data[data['建筑结构'] != '未知结构']

# 5. 删除供暖方式为"暂无数据"的行
data = data[data['供暖方式'] != '暂无数据']

# 6. 删除房屋年限为"暂无数据"的行
before_drop3 = len(data)
data = data[data['房屋年限'] != '暂无数据']
after_drop3 = len(data)
print(f'🚮 已删除房屋年限为"暂无数据"的记录数：{before_drop3 - after_drop3}')

# -----------------------
# 7. 配备电梯列处理
# 将"暂无数据"替换为NaN
data['配备电梯'] = data['配备电梯'].replace('暂无数据', np.nan)

# 按小区填充配备电梯
def fill_elevator(group):
    if group['配备电梯'].notna().any():
        mode_val = group['配备电梯'].mode()[0]  # 用小区内出现最多的值填充
        group['配备电梯'] = group['配备电梯'].fillna(mode_val)
    return group

data = data.groupby('小区', group_keys=False).apply(fill_elevator)

# 删除没有填补的行（如果某小区内所有配备电梯数据都是NaN）
data = data.dropna(subset=['配备电梯'])

# -----------------------
# 保存文件
data.to_csv('/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.4.csv', index=False)
print('✅ 完成！清洗后的数据保存为 北京二手房成交_1.4.csv')
