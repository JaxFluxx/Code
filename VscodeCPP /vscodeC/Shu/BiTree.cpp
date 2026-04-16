#include<stdio.h>
#include<stdlib.h>
#include<algorithm>
using namespace std;

//结构体定义
typedef struct Node{
    int val;
    Node *left, *right;
}Node, *Root;


//创建节点函数
Node* createNode(int val){
    Node* newNode = (Node*)malloc(sizeof(Node));

    newNode->val = val;
    newNode->left = NULL;
    newNode->right = NULL;

    return newNode;
}

//构造二叉树(递归)
Node* buildTree(){
    int val;
    printf("请输入节点的值:(-1为空节点)\n");
    scanf("%d",&val);

    if(val == -1)   return NULL;

    Node* newNode = createNode(val);
    printf("构建节点 %d 的左子数:\n",val);
    newNode->left = buildTree();
    printf("构建节点 %d 的右子数:\n",val);
    newNode->right = buildTree();
    return newNode;
}

//打印树(先序)
void Traverse(Root T){
    if(T == NULL)   return;
    else{
        printf("%d ",T->val);
        Traverse(T->left);
        Traverse(T->right);
    }
}


//销毁树
void DestroyTree(Root T){
    if(T == NULL)   return;

    DestroyTree(T->left);
    DestroyTree(T->right);
    free(T);
}

int main(){
    Root T = buildTree();
    printf("二叉树遍历结果（先序遍历）:\n");
    Traverse(T);
    printf("\n");
    DestroyTree(T);

    free(T);
    T = NULL;
    
    system("pause");
    return 0;
}