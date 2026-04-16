# 例   利用冒泡排序法，将n个数按从小到大顺序排列后输出。
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]

# 输入n个数
n = int(input("请输入数字的个数: "))
numbers = []
for i in range(n):
    num = float(input(f"请输入第 {i+1} 个数字: "))
    numbers.append(num)

# 使用冒泡排序法排序
bubble_sort(numbers)

# 输出排序后的结果
print("排序后的数字为:")
for num in numbers:
    print(num)
