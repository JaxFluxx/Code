#include<stdio.h>
#include<stdlib.h>

const int MaxSize = 10;
typedef struct Node{
    int data;
    int next;
}Node,SLinkList[MaxSize];

///////////////////////////////////////////////////////////////////////////////////////////////
//链表命名区别测试

void test(){
    Node x;
    printf("size x = %d\n",sizeof(x));

    Node y[MaxSize];
    printf("size y = %d\n",sizeof(y));

    SLinkList z;
    printf("size z = %d\n",sizeof(z));
}

///////////////////////////////////////////////////////////////////////////////////////////////

int main(){
    test();
    system("pause");
    return 0;
}