# 例   从键盘输入几个数字，用逗号分隔，求这些数字之和。
# 分析：输入的数字当作一个字符串来处理，首先分离出数字串，再转换成数值，这样就能求和。
# 也可以使用正则表达式来实现。


# 输入数字，用逗号分隔
numbers_str = input("请输入几个数字，用逗号分隔: ")

# 分离出数字串
numbers_list = numbers_str.split(',')

# 转换成数值并求和
sum_of_numbers = sum(map(float, numbers_list))

# 输出结果
print(f"这些数字的和为: {sum_of_numbers}")
