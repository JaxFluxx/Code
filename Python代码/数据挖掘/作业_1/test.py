def heapify(array, length, i):
    largest = i  # 初始化最大值为根节点
    left = 2 * i + 1  # 左子节点
    right = 2 * i + 2  # 右子节点

    # 如果左子节点更大
    if left < length and array[left] > array[largest]:
        largest = left

    # 如果右子节点更大
    if right < length and array[right] > array[largest]:
        largest = right

    # 如果最大值不是根节点
    if largest != i:
        array[i], array[largest] = array[largest], array[i]  # 交换

        # 递归地堆化受影响的子树
        heapify(array, length, largest)

def heap_sort(array):
    length = len(array)

    # 构建最大堆
    for i in range(length // 2 - 1, -1, -1):
        heapify(array, length, i)

    # 一个个取出元素
    for j in range(length - 1, 0, -1):
        array[0], array[j] = array[j], array[0]  # 交换
        heapify(array, j, 0)

if __name__ == '__main__':
    arr = [10, 2, 2, 4, 5, 1, 7, 8, 9]
    heap_sort(arr)
    print(arr)
