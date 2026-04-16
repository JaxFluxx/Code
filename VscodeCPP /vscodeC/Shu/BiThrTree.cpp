#include<stdio.h>
#include<stdlib.h>
using namespace std;

//节点定义
typedef struct BiThrNode{
    int val;
    struct BiThrNode *left, *right;
    int ltag, rtag;
}Node, *Tree;

Node *pre = NULL;   //全局变量

//创建节点
Node* createNode(int val){
    Node *newNode = (Node*)malloc(sizeof(Node));

    newNode->val = val;
    newNode->left = NULL;
    newNode->right = NULL;
    newNode->ltag = 0;
    newNode->rtag = 0;

    return newNode;
}

//递归构造二叉树
Node* buildTree(){
    int val;
    printf("输入该节点的值(-1为空):\n");
    scanf("%d",&val);

    if(val == -1) return NULL;
    else{
        Node *newNode = createNode(val);
        printf("构建 %d 的左子树：\n",val);
        newNode->left = buildTree();
        printf("构建 %d 的右子树：\n",val);
        newNode->right = buildTree();
        return newNode;
    }
}

//销毁二叉树
void freeTree(Tree &T){
    if(T == NULL)   return;

    freeTree(T->left);
    freeTree(T->right);
    free(T);
}

//打印二叉树
void printTree(Tree T){
    if(T == NULL)   return;
    else{
        printf("%d ",T->val);
        printTree(T->left);
        printTree(T->right);
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////

//线索化树(createTree函数的子函数)
void InThread(Tree &T){
    if(T!=NULL){
        //线索化左子树
        InThread(T->left);

        //线索化本节点
        if(T->left == NULL){    //建立前驱
            T->left = pre;
            T->ltag = 1;
        }
        if(pre->right == NULL){   //建立后继
            pre->right = T;
            pre->ltag = 1;
        }
        pre = T;    //更新节点前驱

        //线索化右子树
        InThread(T->right); 
    }
}

//线索化树(中序)
void createThrTree(Tree &T){
    pre = NULL;

    if(T == NULL){
        printf("树空,无法线索化！");
        return;
    }else{
        InThread(T);

        //处理最后一个节点
        pre->right = NULL;
        pre->rtag = 1;
    }
}

////////////////////////////////////正向中序遍历树////////////////////////////////////////////////

//找到中序第一个数
Node* firstNode(Node* p){
    //找到p为根最左下角的数
    while(p->ltag != 0)  p = p->left;
    return p;
}

//找到中序后继
Node* nextNode(Node* p){
    //若非叶子节点
    if(p->rtag == 0)    return firstNode(p->right);
    //若为叶子节点
    else    return p->right;
}

//操作函数
void test1_visit(Node* p){
    printf("%d ",p->val);
}

//框架
void Inorder(Node* T){
    printf("\n中序打印树:\n");
    for(Node *p = firstNode(T); p != NULL; p = nextNode(p)){
        test1_visit(p);
    }
}

///////////////////////////////////////////逆向中序遍历树/////////////////////////////////////////

//找到中序最后一个数
Node* lastNode(Node *p){
    while(p->rtag == 0)     p = p->right;
    return p;
}

//找到中序前驱
Node* preNode(Node *p){
    //若非叶子节点
    if(p->ltag == 0)    return lastNode(p->left);
    //若是叶子节点
    else    return p->left;
}

void test2_visit(Node *p){
    printf("%d ",p->val);
}

//框架
void RevInorder(Tree T){
    printf("\n中序打印树(逆序)\n");
    for(Node *p = lastNode(T); p != NULL; p = preNode(p)){
        test2_visit(p);
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////

int main(){
    Tree T = buildTree();
    printf("二叉树为(先序)\n");
    printTree(T);
    printf("\n");

    Inorder(T);

    freeTree(T);
    free(T);
    T = NULL;

    system("pause");
    return 0;
}