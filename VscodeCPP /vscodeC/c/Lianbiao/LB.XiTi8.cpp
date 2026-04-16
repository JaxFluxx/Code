/*
设长度为n的带附加头节点的单链表的表头指针为L,元素为{a1,a2……an},设计一个算法重新连接链表元素，使得元素排列为{a1,an,a2,an-1,a3……}
*/

#include<bits/stdc++.h>

//结构体定义
typedef struct Node{
    int data;
    Node* next;
}Node,*LinkList;

//链表初始化
void InitList(LinkList &L){
    L = (Node*)malloc(sizeof(Node));
    if(L==NULL) return;

    L->next = NULL;
    return;
}

//输出链表
void ShowList(LinkList L){
    Node *p = L->next;

    printf("\n链表元素为:");
    while(p != NULL){
        printf("%d ",p->data);
        p = p->next;
    }
    return;
}

//后插元素(插入数组)
LinkList InsertNode(LinkList &L,int arr[],int arr_length){
    Node *p1, *p2 = L;

    printf("\n开始插入");
    int index = 0;
    while(index != arr_length){
        p1 = (Node*)malloc(sizeof(Node));

        p1->data = arr[index];
        p2->next = p1;
        p2 = p1;

        index++;
    }
    p1->next = NULL;

    return L;
}

//销毁链表
void DestroyList(LinkList &L){
    Node *p1 = L,*p2;
    while(p1 !=  NULL){
        p2 = p1;
        p1 = p1->next;
        free(p2);
    }
}



////////////////////////////////////////////////////////////////////////////////////////

//算法
void relink(LinkList L){
    //相当于不断将链表最后一个元素插入前面的两个元素之中，n个元素要插入 floor((n-1)/2) 次

    //计算链表长度
    Node *p = L;
    int length = 0;
    while(p->next != NULL){
        p = p->next;
        length++;
    }
    if(length <= 2)     return;

    //循环floor((lengh-1)/2)次，每一次都把p指向最后一个元素，插入到q前面(q总是指向要插入位置的后一位元素)
    int times = floor((length-1)/2), x;
    Node *q = L->next->next;    //第一次把末尾元素插入到第二个元素前面

    while(times != 0){
        Node *p1 = L->next, *p2 = L;    //定位末尾元素(p1指向末尾元素，p2指向末尾元素前一位元素)
        while(p1->next != NULL){
            p1 = p1->next;
            p2 = p2->next;
        }
        p2->next = NULL;
        
        //插入(后插)
        p1->next = q->next;
        q->next = p1;

        x = p1->data;
        p1->data = q->data;
        q->data = x;

        q = q->next->next;
        times--;
    }
}

//////////////////////////////////////////////////////////////////////////////////////////



void test(){
    int arr[] = {1,2,3,4,5,6,7,8,9,10};

    int arr_length = sizeof(arr) / sizeof(arr[0]);  //计算数组长度
    printf("\n数组长度:%d",sizeof(arr));
    printf("\n元素长度:%d",sizeof(arr[0]));
    printf("\n元素个数:%d\n",arr_length);
   
    LinkList L;
    
    InitList(L);
    InsertNode(L,arr,arr_length);
    ShowList(L);

    relink(L);
    ShowList(L);

    DestroyList(L);
}

int main(){
    test();

    system("pause");
    return 0;
}