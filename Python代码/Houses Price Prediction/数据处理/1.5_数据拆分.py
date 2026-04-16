import pandas as pd
import numpy as np
import re

# 读取数据
data = pd.read_csv('/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.4.csv')

# ===== 1. 房屋户型拆分 =====
# 提取数字
def split_house_type(house_type):
    match = re.findall(r'(\d+)室(\d+)厅(\d+)厨(\d+)卫', str(house_type))
    if match:
        return list(map(int, match[0]))
    else:
        return [np.nan, np.nan, np.nan, np.nan]

# 应用拆分
house_type_split = data['房屋户型'].apply(split_house_type)
house_type_df = pd.DataFrame(house_type_split.tolist(), columns=['n房-户型', 'n厅-户型', 'n厨-户型', 'n卫-户型'])

# 删除原列，插入新列
house_type_index = data.columns.get_loc('房屋户型')
data.drop(columns=['房屋户型'], inplace=True)
for i, col in enumerate(house_type_df.columns):
    data.insert(house_type_index + i, col, house_type_df[col])

# ===== 2. 所在楼层处理 =====
# 保留括号前的文字
def clean_floor(floor_info):
    return str(floor_info).split('(')[0] if pd.notnull(floor_info) else np.nan

# 应用
data['所在楼层'] = data['所在楼层'].apply(clean_floor)

# ===== 3. subway列重命名和处理 =====
# 重命名
data.rename(columns={'subway': '地铁'}, inplace=True)

# 规则处理
def map_subway(distance):
    if distance == 0:
        return '250米内'
    elif distance == 1:
        return '500米内'
    elif distance == 2:
        return '800米内'
    else:
        return '无'

data['地铁'] = data['地铁'].apply(map_subway)

# ===== 保存新文件 =====
data.to_csv('/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.5.csv', index=False)
print('✅ 拆分、处理、重命名完成！已保存为 北京二手房成交_1.5.csv')
