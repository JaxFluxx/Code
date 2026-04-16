#include<stdio.h>
#include<stdlib.h>

const int Size = 100;

typedef struct{
    int data;
    int parent;
}Node;

//全局声明
Node set[Size];

//初始化集合
void Initialize(int n){     //n为集合大小
    for(int i=0;i<n;i++){
        //数据域
        set[i].data = i;
        set[i].parent = -1;
    }
}

//查找根节点(传入子节点下标)
int find(int x){
    while(set[x].parent != -1)  //如果不是根节点，将当前节点父节点下标赋值给x
        x = set[x].parent;
    return x;
}

//合并集合(分别传入两个集合的其中一个子节点)
void unify(int x, int y){
    int rootx = find(x);
    int rooty = find(y);
    set[rooty].parent = rootx;
}

int main(){
    int n = 10; //10个元素
    Initialize(n);

//创建两个集合，元素分别是1,2和3，5
    unify(1,2);
    unify(3,5);

// 输出每个元素的父节点
    printf("Element:\n");
    for (int i = 0; i < n; i++) {
         printf("%d ", set[i].parent);
    }

//合并这两个集合
    printf("\n");
    unify(2,5);
// 输出每个元素的父节点
    printf("Element:\n");
    for (int i = 0; i < n; i++) {
         printf("%d ", set[i].parent);
    }


    system("pause");
    return 0;
}