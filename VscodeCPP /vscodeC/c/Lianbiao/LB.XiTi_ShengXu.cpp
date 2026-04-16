//输入两个链表，-1结束，生成升序新链表
#include<bits/stdc++.h>
using namespace std;

//单链表定义
typedef struct LNode{
    int data;
    struct LNode *next;
}LNode,*LinkList;

//初始化单链表
bool InitList(LinkList &L){
    L = (LNode*)malloc(sizeof(LNode));
    if(L == NULL)   return false;
    L->next = NULL;
    return true;
}

//判断链表是否为空
bool Empty(LinkList L){
    if(L->next == NULL) return true;
    else    return false;
}

// 输出表
void ShowList(LinkList &L) {
    if(Empty(L)){
        printf("NULL");
        return;
    }

    LNode* s = L->next;
    for (;s->next != NULL; s = s->next) {
        printf("%d ", s->data);
    }
    printf("%d",s->data);
}

//尾插建立单链表
LinkList TailInsert(LinkList &L){
    int x;  //输入x=-1时候停止输入
    LNode *s1 = L, *s2 = L;     //s1先走，s2后走
    
    //输入
    scanf("%d",&x);
    while(x != -1){
        s1 = (LNode*)malloc(sizeof(LNode));
        s1->data = x;

        s2->next = s1;
        s2 = s1;

        scanf("%d",&x);
    }

    s1->next = NULL;
    return L;
}

//生成升序新链表
void SortList(LinkList &L1,LinkList &L2,LinkList &L3){
    LNode *s1 = L1->next,*s2 = L2->next, *s3_1 = L3;

    while(s2 != NULL && s1 != NULL){
        if(s1->data <= s2->data){
            LNode *s3_2 = (LNode*)malloc(sizeof(LNode));
            s3_2->data = s1->data;

            s3_1->next = s3_2;
            s3_1 = s3_2;
            s1 = s1->next;
        }
        else if(s1->data > s2->data){
            LNode *s3_2 = (LNode*)malloc(sizeof(LNode));
            s3_2->data = s2->data;

            s3_1->next = s3_2;
            s3_1 = s3_2;
            s2 = s2->next;
        }
    }
    if(s1 == NULL){
        s3_1->next = s2;
    }else if(s2 == NULL){
        s3_1->next = s1;
    }
}

int main()
{
    LinkList L1;
    InitList(L1);
    LinkList L2;
    InitList(L2);

    TailInsert(L1);
    TailInsert(L2);

    //ShowList(L1);
    //ShowList(L2);


    LinkList L3;
    InitList(L3);

    SortList(L1,L2,L3);
    ShowList(L3);

    system("pause");
    return 0;
}