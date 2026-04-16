//一段只能插入，一段只能删除的线性表    逻辑结构可以看作环形表
//特点：先进先出（FIFO）
#include<stdio.h>
#include<stdlib.h>
#include<math.h>
using namespace std;


const int MaxSize = 10;

//定义
typedef struct{
    int data[MaxSize];
    int front, rear;    //front指向第一个元素，rear指向最后一个元素的后一个位置
}SeqQueue;

//初始化
bool InitQueue(SeqQueue &Q){
    Q.front = 0;
    Q.rear  = 0;
    return true;
}

//判空
bool EmptyQueue(SeqQueue Q){
    if(Q.front == Q.rear)  return true;
    else    return false;
}

//判满
bool FullQueue(SeqQueue Q){
    if(Q.front == (Q.rear+1) % MaxSize) return true;    //求余是防止Q.rear在Q.data[MaxSize-1]处，即Q.data分配的内存尾部
    else return false;
}

//输出队
void ShowQueue(SeqQueue Q){
    if(Q.front == Q.rear){
        printf("队空!\n");
        return;
    }

    printf("当前队列为：\n");
    for(int i=Q.front;i!=Q.rear;i++){
        i = i % MaxSize;

        printf("%d ",Q.data[i]);
    }
    return;
}

//入队
bool InsertQueue(SeqQueue &Q){
    if(FullQueue(Q)){
        printf("队满！无法入队\n");
        return false;
    }

    printf("要插入几个数：(最多插入%d个):",MaxSize-1-abs((Q.rear-Q.front)));  //-1是因为要留出一个空位
    int num;
    scanf("%d",&num);
    if(num > MaxSize-1-abs((Q.rear-Q.front))){
        printf("你插个蛋\n");
        return false;
    }

    while(num--){
        int x;
        scanf("%d",&x);
        Q.data[Q.rear] = x;
        Q.rear = (Q.rear+1) % MaxSize;
    }

    ShowQueue(Q);
    return true;
}

//出队
bool DelQueue(SeqQueue &Q){
    if(EmptyQueue(Q)){
        printf("队空！无法出队\n");
        return false;
    }

    printf("要删除几个数(最多删除%d个):",abs(Q.rear - Q.front));
    int num;
    scanf("%d",&num);
    if(num > abs(Q.rear - Q.front)){
        printf("你删个蛋\n");
        return false;
    }

    while(num--){
        //队头指针后移
        Q.front = (Q.front+1) % MaxSize;
    }

    ShowQueue(Q);
    return true;
}

int main(){
    SeqQueue Q;
    InitQueue(Q);
    ShowQueue(Q);

    InsertQueue(Q);
    DelQueue(Q);

    system("pause");
    return 0;
}