import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap

# 读取数据
file_path = r"C:\Users\何嘉\Desktop\朝阳二手房数据_清洗后.xlsx"
df = pd.read_excel(file_path)

# 过滤年代数据
df = df[(df['建成年代'] >= 1980) & (df['建成年代'] <= 2024)]

# 价格分布
print("Price distribution:")
print("Average price:", df['价格(万元)'].mean())
print("Median price:", df['价格(万元)'].median())
print("Price range (quantiles):", df['价格(万元)'].quantile(q=[0.25, 0.5, 0.75]))

# 价格分布图
plt.figure(figsize=(10, 6))
sns.histplot(df['价格(万元)'], bins=20, kde=True)
plt.title('Second-hand house price distribution')
plt.xlabel('Price (ten thousand yuan)')
plt.ylabel('Count')
plt.show()

# 建成年代与价格的关系
plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='建成年代', y='价格(万元)')
plt.title('Relationship between construction year and price')
plt.xlabel('Construction year')
plt.ylabel('Price (ten thousand yuan)')
plt.show()

# 区域分析
region_prices = df.groupby('区域+小区')['价格(万元)'].mean()
print("Regional price analysis:")
print(region_prices)

# 单价分析
print("Unit price analysis:")
print(df['单价(元/平米)'].describe())

# 单价分布图
plt.figure(figsize=(10, 6))
sns.histplot(df['单价(元/平米)'], bins=20, kde=True)
plt.title('Unit price distribution')
plt.xlabel('Unit price (yuan/square meter)')
plt.ylabel('Count')
plt.show()

# 热力图分析
lons = df['经度'].values
lats = df['纬度'].values
prices = df['价格(万元)'].values

map_obj = folium.Map(location=[39.92, 116.46], zoom_start=11)
HeatMap(data=[(lat, lon, price) for lat, lon, price in zip(lats, lons, prices)],
        radius=50, blur=30, max_zoom=16).add_to(map_obj)

map_obj.save(r"C:\Users\何嘉\Desktop\house_price_heatmap.html")
