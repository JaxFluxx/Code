import pandas as pd

# 读取原始CSV文件
df = pd.read_csv('/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.7.1.csv')

# 要删除的列名
columns_to_drop = [
    '区域', '商圈', '小区', '几环内', '地铁', '经度', '纬度', '户型结构',
    '所在楼层', '房屋朝向', '建筑类型', '建筑结构', '装修情况', '供暖方式',
    '配备电梯', '交易权属', '房屋用途', '房屋年限', '房权所属'
]

# 删除列
df_cleaned = df.drop(columns=columns_to_drop, errors='ignore')  # 如果某些列不存在也不会报错

# 保存新文件
df_cleaned.to_csv('/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.7.2.csv', index=False)

print("处理完成")
