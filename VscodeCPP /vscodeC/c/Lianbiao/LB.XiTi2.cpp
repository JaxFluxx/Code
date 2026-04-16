#include<stdio.h>
#include<stdlib.h>

//结构体定义
typedef struct LNode{
    int data;
    struct LNode *next;
}LNode, *LinkList;

//头节点初始化
bool InitList(LinkList &L){
    L = (LNode*)malloc(sizeof(LNode));
    if(L==NULL)     return false;

    L->next = NULL;
    return true;
}


//显示单链表
void ShowList(LinkList L){
    LNode *p = L->next;
    printf("\n");
    while(p!=NULL){
        printf("%d ",p->data);
        p = p->next;
    }
    return;
}

//插入（头插）
LinkList HeadInsert(LinkList &L){
    int n, x;   LNode *p;
    printf("输入要插入多少个数:\n");
    scanf("%d",&n);

    while(n--){
        p = (LNode*)malloc(sizeof(LNode));
        scanf("%d",&x);

        p->data = x;
        p->next = L->next;
        L->next = p;
    }
    return L;
}

//插入（尾插）
LinkList TailInsert(LinkList &L){
    int n, x;   LNode *p1 = L, *p2 = L;
    printf("输入要插入多少个数:\n");
    scanf("%d",&n);

    while(n--){
        scanf("%d",&x);
        p1 = (LNode*)malloc(sizeof(LNode));

        p1->data = x;
        p2->next = p1;
        p2 = p1;
    }
    p1->next = NULL;

    return L;
}

//连接（把L2连接到L1后面）
void Connect(LinkList &L1, LinkList &L2){
    LNode *p = L1;
    while(p->next!=NULL)    //找到L1链表最后一个结点
        p = p->next;
    p->next = L2->next;

    L2 = NULL;
    return;
}

//升序单链表(冒泡排序)
void BubbleSortList(LinkList& L) {
    int count = 0;
    LNode* p1, * p2, * p3;

    // 计算结点个数
    p1 = L->next;
    while (p1 != NULL) {
        count++;
        p1 = p1->next;
    }

    // 冒泡排序
    for (int i = 0; i < count; i++) {
        p3 = L;
        p2 = L->next;
        p1 = p2->next;

        for (int num = count - 1 - i; num > 0; num--) {
            if (p2->data > p1->data) {
                // 交换结点数据
                p3->next = p1;
                p2->next = p1->next;
                p1->next = p2;
                // 更新三个指针的位置
                LNode* temp = p2;
                p2 = p1;
                p1 = temp;
            }
            // 后移指针
            p3 = p3->next;
            p2 = p2->next;
            p1 = p1->next;
        }
    }
    return;
}

//删除重复数
void DelRepeatList(LinkList &L){
    // 定义一个与链表长度相同的数组
    // 扫描过的结点data先与数组中所有数进行比较
    // 若有相同，则在链表中跳过该结点；若无相同，则将该数录入数组，并继续扫描下一个结点
    LNode *p = L->next;
    int length = 0;
    while(p != NULL){
        p = p->next;
        length++;   
    }
    printf("\n链表长度为:%d\n",length);

    int arr[length], arrLength = 0;
    p = L->next;
    //开始扫描
    while(p != NULL){
        bool isRepeat = false;
        int currentData = p->data;

        //对当前结点进行比较
        for(int i = 0; i < arrLength; i++){
            if(currentData == arr[i]){
                isRepeat = true;
                break;
            }       
        }

        if(isRepeat){   //重复，跳过该节点
            LNode *q = p->next;

            //p是要删除的结点！！！
            p->data = q->data;
            p->next = q->next;
            free(q);
            length--;
        }else{  //没有重复，录入该结点
            arr[arrLength] = currentData;
            arrLength++;
            p = p->next;
        }
    }
    printf("删除后链表长度为:%d\n",length);
    return;
}

//范围保留（删除值小于min和值大于max的元素）
void List_RangePreservation(LinkList &L){
    printf("\n要保留结点值的最小值和最大值分别为:\n");
    int max, min;
    scanf("%d %d",&min, &max);
    if(max < min){
        printf("输入值有误！");
        return;
    }

    //开始扫描
    LNode *p = L;
    p = L;
    while(p!=NULL && p->next != NULL){
        if((p->next->data<min || p->next->data>max) && (p!=NULL && p->next!=NULL)){     //普适情况
            p->next = p->next->next;
        }else{
            p = p->next;
        }
    }
    return;
}

int main(){
    LinkList L1, L2;
    InitList(L1);
    //InitList(L2);
    TailInsert(L1);
    //TailInsert(L2);
    //Connect(L1,L2);
    ShowList(L1);

    DelRepeatList(L1);
    ShowList(L1);

    BubbleSortList(L1);
    ShowList(L1);

    List_RangePreservation(L1);
    ShowList(L1);
    free(L1);
    free(L2);   
    return 0;
}