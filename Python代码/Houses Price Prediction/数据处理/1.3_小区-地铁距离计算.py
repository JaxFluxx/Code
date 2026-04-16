import pandas as pd
from geopy.distance import geodesic
from tqdm import tqdm

# 读取小区数据
house_data = pd.read_csv('/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.2.csv')

# 读取地铁站数据
subway_data = pd.read_csv('/Users/jia/Desktop/论文/数据/subway.csv')

# 定义计算两点距离的函数
def calculate_distance(house_lon, house_lat, subway_lon, subway_lat):
    return geodesic((house_lat, house_lon), (subway_lat, subway_lon)).meters

# 定义根据最近地铁站距离赋值的函数
def assign_nearby_subway(house_lon, house_lat, subway_data):
    distances = []
    for _, subway in subway_data.iterrows():
        distance = calculate_distance(house_lon, house_lat, subway['lon'], subway['lat'])
        distances.append(distance)
    min_distance = min(distances)
    if min_distance <= 250:
        return 3
    elif min_distance <= 500:
        return 2
    elif min_distance <= 800:
        return 1
    else:
        return 0

# 只对每个小区（去重后的小区）计算一次，避免重复计算
unique_communities = house_data[['小区', '经度', '纬度']].drop_duplicates()

# 新建一个字典保存小区和对应subway值
community_subway_dict = {}

# 用tqdm加进度条
for idx, row in tqdm(unique_communities.iterrows(), total=len(unique_communities), desc="Processing Communities"):
    community_name = row['小区']
    lon = row['经度']
    lat = row['纬度']
    subway_level = assign_nearby_subway(lon, lat, subway_data)
    community_subway_dict[community_name] = subway_level
    print(f"已处理小区: {community_name}，地铁等级: {subway_level}")

# 根据小区名统一赋值subway列
house_data['subway'] = house_data['小区'].map(community_subway_dict)

# 保存到新文件
house_data.to_csv('/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.3.csv', index=False)

print('✅ 完成！新的文件已经保存到 北京二手房成交_1.3.csv')
