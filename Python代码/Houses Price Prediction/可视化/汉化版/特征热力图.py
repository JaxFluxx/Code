import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 1. 读取数据
df = pd.read_csv(r'/Users/jia/Desktop/学习 /论文/数据/数据处理/北京二手房成交_1.8.csv')

# 2. 删除第一列（id列），不进行分析
df = df.drop(columns=['id'], errors='ignore')

# 3. 定义中英文映射关系
col_map = {
    "Region": "地区",
    " Business district": "商业区",
    "Community": "小区",
    "Area": "面积",
    "Longitude": "经度",
    "Latitude": "纬度",
    "bedroom_Layout": "卧室_户型",
    "living room_Layout": "客厅_户型",
    "kitchen_Layout": "厨房_户型",
    "bathroom_Layout": "浴室_户型",
    "Layout": "户型",
    "Floor": "楼层",
    "Orientation": "房屋朝向",
    "Building type": "建筑类型",
    "Structure type": "结构类型",
    "Year": "建成年代",
    "Decoration status": "装修状况",
    "Heating method": "供暖方式",
    "Elevator": "电梯",
    "Transaction ownership": "交易权属",
    "Usage": "房屋用途",
    "Years of holding": "房屋年限",
    "Ownership": "房权所属",
    "Price": "价格",
    "City ring zone": "所在环区",
    "Subway": "地铁"
}

# 4. 计算相关性矩阵
correlation_matrix = df.corr()

# 5. 替换行列索引为中文
correlation_matrix.rename(index=col_map, columns=col_map, inplace=True)

# 6. 绘制热力图（中文输出）
plt.figure(figsize=(16, 12))
sns.heatmap(
    correlation_matrix,
    annot=True,
    cmap='coolwarm',
    cbar=True,
    linewidths=0.5,
    annot_kws={"size": 10}
)

plt.title('特征相关性热力图', fontsize=24, fontweight='bold')
plt.xticks(fontsize=14, rotation=45, ha='right')
plt.yticks(fontsize=14, rotation=0)
plt.tight_layout()
plt.show()
