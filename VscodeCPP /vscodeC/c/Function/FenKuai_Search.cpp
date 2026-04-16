#include <iostream>
#include <vector>
#include <cmath>

// 分块查找
int BlockSearch(const std::vector<int>& arr, int key, int blockSize) {
    int n = arr.size();  // 数组的大小
    int blockNum = ceil((double)n / blockSize);  // 块的数量  (ceil——向上取整)

     //           printf("\n%d\n",blockNum);

    // 找到目标元素所在的块
    int blockIndex = -1;
    for (int i = 0; i < blockNum; i++) {
        //            printf("\n\n%d",arr[i*blockSize]);

        //最后一个块的元素是不会满足if条件的，最后blockIndex = -1;
        if (arr[i * blockSize] > key) {     //与每个块第一个元素比较    
            blockIndex = i - 1;
            break;
        }
    }

    //        printf("\n%d\n",blockIndex);
    // 在目标块内进行顺序查找
    if (blockIndex != -1) {
        int start = blockIndex * blockSize;
        int end = std::min((blockIndex + 1) * blockSize, n);

        for (int i = start; i < end; i++) {
            if (arr[i] == key) {
                return i;
            }
        }
    } else {
        // 如果目标元素在最后一个块中
        int start = (blockNum - 1) * blockSize;
        int end = n;

        for (int i = start; i < end; i++) {
            if (arr[i] == key) {
                return i;
            }
        }
    }

    return -1;  // 没有找到目标元素
}

int main() {
    std::vector<int> arr = {3, 6, 8,    10, 12, 15,    18, 21, 24,    27, 30};
    int blockSize = 3;
    int key = 30;

    int index = BlockSearch(arr, key, blockSize);

    if (index != -1) {
        std::cout << "元素 " << key << " 在数组中的下标为：" << index << std::endl;
    } else {
        std::cout << "元素 " << key << " 未在数组中找到" << std::endl;
    }

    system("pause");
    return 0;
}