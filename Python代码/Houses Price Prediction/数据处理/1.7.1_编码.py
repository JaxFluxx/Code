import pandas as pd
from tqdm import tqdm

# === 读取原始数据 ===
file_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.6.csv'
df = pd.read_csv(file_path)

# === 读取商圈编码表，并映射到主数据 ===
商圈编码表 = pd.read_csv('/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.7.0_商圈映射表.csv')
商圈编码 = dict(zip(商圈编码表['商圈'], 商圈编码表['编码']))

# 插入新列函数，自动在原列后插入 _code 列
def insert_encoded_column(df, original_col, new_series, suffix='_code'):
    new_col_name = original_col + suffix
    if new_col_name in df.columns:
        df.drop(columns=[new_col_name], inplace=True)
    col_index = df.columns.get_loc(original_col) + 1
    df.insert(col_index, new_col_name, new_series)

# === 映射编码列 ===
insert_encoded_column(df, '商圈', df['商圈'].map(商圈编码))

区域编码 = {
    '东城': 1, '西城': 2, '海淀': 3, '朝阳': 4, '丰台': 5, '石景山': 5,
    '通州': 6, '大兴': 6, '昌平': 7, '房山': 7, '顺义': 8, '门头沟': 8,
    '亦庄开发区': 9, '怀柔': 10, '密云': 10, '延庆': 10, '平谷': 10
}
insert_encoded_column(df, '区域', df['区域'].map(区域编码))

tqdm.pandas(desc="编码字段")

insert_encoded_column(df, '几环内', df['几环内'])  # 无映射，原值复制

insert_encoded_column(df, '地铁', df['地铁'].map({'250米内': 3, '500米内': 2, '800米内': 1, '无': 0}))
insert_encoded_column(df, '户型结构', df['户型结构'].map({'平层': 0, '复式': 1, '跃层': 2, '错层': 3}))
insert_encoded_column(df, '所在楼层', df['所在楼层'].map({'地下室': 0, '底层': 1, '低楼层': 2, '中楼层': 3, '高楼层': 4, '顶层': 5}))
insert_encoded_column(df, '房屋朝向', df['房屋朝向'].apply(lambda x: 1 if '南' in str(x) else 0))
insert_encoded_column(df, '建筑类型', pd.Categorical(df['建筑类型']).codes + 1)
insert_encoded_column(df, '建筑结构', pd.Categorical(df['建筑结构']).codes + 1)
insert_encoded_column(df, '装修情况', pd.Categorical(df['装修情况']).codes + 1)
insert_encoded_column(df, '供暖方式', df['供暖方式'].map({'集中供暖': 1, '自供暖': 0}))
insert_encoded_column(df, '配备电梯', df['配备电梯'].map({'有': 1, '无': 0}))
insert_encoded_column(df, '交易权属', df['交易权属'].map({
    '商品房': 0, '已购公房': 1, '限价商品房': 2, '二类经济适用房': 3,
    '一类经济适用房': 4, '私产': 5, '央产房': 6, '定向安置房': 7
}))
insert_encoded_column(df, '房屋用途', df['房屋用途'].map({
    '普通住宅': 0, '商业办公': 1, '公寓': 2, '酒店式公寓': 3,
    '别墅': 4
}))
insert_encoded_column(df, '房屋年限', df['房屋年限'].map({'满五年': 2, '满两年': 1}))
insert_encoded_column(df, '房权所属', df['房权所属'].map({'非共有': 0, '共有': 1}))

# === 长度一致性检查 ===
print("\n[校验] 正在检查所有列是否长度一致...")
lengths = df.apply(len)
unique_lengths = lengths.unique()

if len(unique_lengths) != 1:
    print("[错误] 检测到列长度不一致！不同长度如下：")
    print(lengths.value_counts())
    for col in df.columns:
        if len(df[col]) != len(df):
            print(f"列 `{col}` 长度不一致: {len(df[col])} != {len(df)}")
    raise ValueError("所有列的长度不一致，无法保存为 CSV 文件。")
else:
    print("[通过] 所有列长度一致，可安全保存。")

# === 输出处理后的主数据 ===
output_file_path = '/Users/jia/Desktop/论文/数据/数据处理/北京二手房成交_1.7.1.csv'
df.to_csv(output_file_path, index=False)

# 小区唯一值表（不编码，仅为信息参考）
小区列表表 = pd.DataFrame({'小区': df['小区'].dropna().unique()})

print("\n✅ 编码后的主文件已保存至：", output_file_path)
