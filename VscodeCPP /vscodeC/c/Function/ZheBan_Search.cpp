#include<bits/stdc++.h>
using namespace std;

typedef int ElemType;

//表的数据结构(顺序表)
typedef struct{
    ElemType *elem;
    int length;     //表的长度
}SSTable;

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//折半查找(返回key在顺序表中的下标)
int Binary_Search(SSTable L,ElemType key){
    //low指头，high指尾
    int low = 0, high = L.length-1, mid;
    while(low <= high){
        mid = (low + high) / 2;
        if(mid == key)  //找到了
            return mid;
        else if(L.elem[mid] > key)
            high = mid - 1;
        else if(L.elem[mid] < key)
            low = mid + 1;
    }

    //没有找到
    return -1;
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

int main() {
    // 创建顺序表
    SSTable table;
    table.length = 10;  // 表的长度为10
    table.elem = new ElemType[table.length];

    // 给表赋值
    for (int i = 0; i < table.length; i++) {
        table.elem[i] = i + 1;
    }

    // 要查找的元素
    ElemType key = 7;

    // 调用折半查找函数
    int index = Binary_Search(table, key);

    // 输出结果
    if (index != -1) {
        cout << "元素 " << key << " 在顺序表中的下标为：" << index << endl;
    } else {
        cout << "元素 " << key << " 未在顺序表中找到" << endl;
    }

    // 释放内存
    delete[] table.elem;

    system("pause");
    return 0;
}