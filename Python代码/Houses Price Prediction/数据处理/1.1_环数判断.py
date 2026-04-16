import pandas as pd

# 读取数据
file_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.1.csv'
df = pd.read_csv(file_path)

# 定义每个环的经纬度矩形区域
# 每个区域通过左下角 (lon_min, lat_min) 和右上角 (lon_max, lat_max) 来确定
circle_bounds = {
    2: {'lon_min': 116.3579413207342, 'lat_min': 39.86899085812848, 'lon_max': 116.43709054180454, 'lat_max': 39.9482747018643},  # 二环内
    3: {'lon_min': 116.31342604161034, 'lat_min': 39.85618318401884, 'lon_max': 116.45904942341099, 'lat_max': 39.96933642927288},  # 二-三环
    4: {'lon_min': 116.27290474026552, 'lat_min': 39.832849431246736, 'lon_max': 116.48528356184147, 'lat_max': 39.98507431678133},  # 三-四环
    5: {'lon_min': 116.22063432686696, 'lat_min': 39.80137263671753, 'lon_max': 116.52576034643698, 'lat_max': 40.004521483854724}   # 四-五环
}

# 定义判断函数
def determine_circle(lon, lat):
    for circle, bounds in circle_bounds.items():
        if bounds['lon_min'] <= lon <= bounds['lon_max'] and bounds['lat_min'] <= lat <= bounds['lat_max']:
            return circle
    return 0  # 五环外

# 应用判断函数，新建一列
df['几环内'] = df.apply(lambda row: determine_circle(row['经度'], row['纬度']), axis=1)

# 保存结果
save_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.2.csv'
df.to_csv(save_path, index=False, encoding='utf-8-sig')

print('环数分类完成，结果已保存到:', save_path)
