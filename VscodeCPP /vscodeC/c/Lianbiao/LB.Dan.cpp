#include<stdio.h>
#include<stdlib.h>
using namespace std;

typedef int ElemType;

////////////////////////////////////////////////////////////////////////////////////////////////

//单链表定义
typedef struct LNode{
    ElemType data;
    struct LNode *next;
}LNode,*LinkList;       //LinkList表示一个指向struct LNode的指针

//初始化单链表
bool InitList(LinkList &L){
    L = (LNode*)malloc(sizeof(LNode));      //为头节点申请空间,头指针指向头节点
    if(L==NULL)     return false;
    L->next = NULL;     //此处头节点后暂无结点，若有应指向第一个结点
    return true;        //初始化成功
}

//判断单链表是否为空
bool Empty(LinkList L){
    if(L->next == NULL)     return true;
    else    return false;
}
////////////////////////////////////////////////////////////////////////////////////////////////

//头插建立链表
LinkList List_HeadInsert(LinkList &L){
    InitList(L);    //初始化单链表

    ElemType x;  LNode *p;
    scanf("%d",&x);
    while(x!=9999){     //输入9999停止插入
        p = (LNode*)malloc(sizeof(LNode));
        p->data = x;
        p->next = L->next;
        L->next = p;
        scanf("%d",&x);
    }
    return L;
}

//尾插建立链表
LinkList List_TailInsert(LinkList &L){
    L = (LNode*)malloc(sizeof(LNode));
    int x;
    LNode *s1 = L, *s2 = L;     //s1先走,s2后走

    scanf("%d",&x);
    while(x!=9999){
        s1 = (LNode*)malloc(sizeof(LNode));
        s1->data = x;
        
        s2->next = s1;
        s2 = s1;

        scanf("%d",&x);
    }
    s1->next = NULL;
    return L;
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//单链表插入
bool ListInsert(LinkList &L, int i, ElemType e){    //链表头指针，插入位次，插入数
    if(i<1)     return false;   //插入失败（无法插入
    LNode *p;   //指向当前扫描到的结点
    int j = 0;      //当前扫描到第几个结点
    
    p = L;      //指向头节点，头节点不存数据

    //目的是找到要插入位次的前一个结点，即第(i-1)个结点,令j=(i-1),p指向第(i-1)个结点
    while (p!=NULL && j < i-1)      
    {
        p = p->next;
        j++;        //循环结束后j = i-1
    }

    if(p==NULL)     return false;

    LNode *s = (LNode*)malloc(sizeof(LNode));
    s->data = e;
    s->next = p->next;
    p->next = s;
}

//按位删除(1)
bool ListDelete(LinkList &L, int i, ElemType &e)   //链表头指针, 删除位次， 删除结点data
{
    if(i<1)     return false;
    LNode *p = L;
    int j = 0;
    
    while(p!=NULL && j<i-1){
        p = p->next;
        j++;
    }

    if(p==NULL)     return false;

    LNode *q = p->next;
    e = q->data;
    p->next = q->next;
    free(q);
    return true;
}

//按位删除(无头指针传入)
bool DeleteNode(LNode *p){      //要删除结点的指针
    if(p==NULL)     return false;

    LNode *q = p->next;
    p->data = q->data;
    p->next = q->next;
    free(q);
    return true;
}

///////////////////////////////////////////////////////////////////////////////////////////////

//按位查找
LNode *GetElem(LinkList L, int i){
    if(i<0)     return NULL;

    LNode *p = L;
    int j = 0;

    while(p!=NULL && j<i){      //循环找到第i个结点
        p = p->next;
        j++;
    }
    return p;
}

//按值查找
LNode *LocaceElem(LinkList L, ElemType e){
    LNode *p = L;

    while(p!=NULL && e!=p->data){       //p!=NULL 指 查找到表尾了(找不到该值)
            p = p->next;
    }
    return p;
}

//求表长度
int Length(LinkList L){
    int len = 0;
    LNode *p = L;
    
    while(p!=NULL){
        len++;
        p = p->next;
    }
    return len;
}

///////////////////////////////////////////////////////////////////////////////////////////////
int main(){
    LinkList L;     //定义一个头指针
    InitList(L);    //初始化链表
    system("pause");
    return 0;
}