import pandas as pd
from datetime import datetime

# 1. 读取原始文件
file_path = r'/Users/jia/Desktop/学习 /机器学习/数据/1.2.csv'
df = pd.read_csv(file_path)

# 2. 拆分日期和时间
df[['Date', 'Time']] = df['Trip End Timestamp'].str.split(' ', n=1, expand=True)

# 3. 去除年份，只保留“月/日”
df['Date'] = df['Date'].apply(lambda x: '/'.join(x.split('/')[:2]))

# 4. 将时间转换为24小时制的小时数（含分钟）
def time_to_decimal_hours(t_str):
    try:
        t = datetime.strptime(t_str.strip(), "%I:%M:%S %p")  # 12小时制时间解析
        return round(t.hour + t.minute / 60, 2)
    except:
        return None

df['Hour'] = df['Time'].apply(time_to_decimal_hours)

# 5. 删除不需要的列
df.drop(columns=['Trip End Timestamp', 'Time'], inplace=True)

# 6. 保存新文件
output_path = r'/Users/jia/Desktop/学习 /机器学习/数据/1.3.csv'
df.to_csv(output_path, index=False)

print("✅ 已处理完毕，保存新文件为 1.3.csv（已删除原始时间列）")
