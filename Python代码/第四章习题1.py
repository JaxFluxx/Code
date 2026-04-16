# 例  输入年月，求该月的天数。
# 分析：用year、month分别表示年和月，day表示每月的天数。考虑到以下两点。
# （1）每年的1、3、5、7、8、10、12月，每月有31天；4、6、9、11月，每月有30天；闰年2月有29天，平年2月有28天。
# （2）年份能被4整除，但不能被100整除，或者能被400整除的年均是闰年。
# 输入年月

year = int(input("请输入年份: "))
month = int(input("请输入月份: "))

# 判断该月的天数
if month in [1, 3, 5, 7, 8, 10, 12]:
    day = 31
elif month in [4, 6, 9, 11]:
    day = 30
elif month == 2:
    # 判断是否是闰年
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        day = 29
    else:
        day = 28
else:
    print("输入的月份无效。")
    day = None

# 输出该月的天数
if day is not None:
    print(f"{year}年{month}月的天数为: {day}天")
