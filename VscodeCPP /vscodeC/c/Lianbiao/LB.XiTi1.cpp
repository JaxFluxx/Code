#include<stdio.h>
#include<stdlib.h>

const int MaxSize = 8;

typedef struct {
    int* data;
    int length;
    int MaxSize;
} SeqList;

// 顺序表初始化
void InitList(SeqList& L) {
    L.data = (int*)malloc(sizeof(int) * MaxSize);
    L.MaxSize = MaxSize;
    L.length = 0;
}

// 插入数
void InsertList(SeqList& L) {
    printf("插入%d位数\n", MaxSize);
    for (int i = 0; i < L.MaxSize; i++) {
        scanf("%d", &L.data[i]);
        L.length++;
    }
}

// 输出表
void ShowList(SeqList L) {
    printf("顺序表为:\n");
    for (int i = 0; i < L.length; i++) {
        printf("%d ", L.data[i]);
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// 倒序表
void UpsidedownList(SeqList& L) {
    int* p;
    p = (int*)malloc(sizeof(int) * MaxSize);
    if (p == NULL) {
        printf("失败！");
        return;
    }

    for (int i = 0; i < L.length; i++) {
        p[i] = L.data[L.length - i - 1];
    }

    free(L.data);
    L.data = p;
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// 删除顺序表中重复的数（保留第一个）
void DelNum(SeqList& L) {
    SeqList L1;
    InitList(L1);

    // 接收第一个数
    L1.data[0] = L.data[0];
    L1.length = 1;

    // 循环接收数
    for (int i = 1; i < L.length; i++) {
        int test = 0;

        // 逐一与新表中比对
        for (int j = 0; j < L1.length; j++) {
            if (L.data[i] == L1.data[j]) {
                test = 1;
                break;
            }
        }

        // test=0,则证明新表中没有该数,需要移动到新表
        if (test == 0) {
            L1.data[L1.length] = L.data[i];
            L1.length++;
        }
    }

    free(L.data);
    L.length = L1.length;
    L.data = L1.data;
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


int main() {
    SeqList L;
    InitList(L);
    InsertList(L);
    DelNum(L);
    ShowList(L);
    system("pause");
    return 0;
}