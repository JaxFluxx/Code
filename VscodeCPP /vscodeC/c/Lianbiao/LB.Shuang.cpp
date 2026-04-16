#include<stdio.h>
#include<stdlib.h>
using namespace std;

typedef int ElemType;

//结点定义
typedef struct DNode{
    ElemType data;
    struct DNode *prior, *next;
}DNode, *DLinkList;

//初始化双链表
bool InitDLinkList(DLinkList &L){
    L = (DNode*)malloc(sizeof(DNode));
    //判断分配内存是否成功
    if(L==NULL)     return false;

    L->prior = NULL;
    L->next  = NULL;
    return true;
}

int main(){
    DLinkList L;     //定义一个头指针
    InitDLinkList(L);    //初始化链表
    system("pause");
    return 0;
}