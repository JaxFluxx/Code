#include<stdio.h>
#include<stdlib.h>
#include<algorithm>
#include<queue>
#include<iostream>
using namespace std;

const int Size = 1000;

//结构体定义(链式存储)
typedef struct Node{
    int val;
    struct Node *left, *right;
}Node, *Tree;



//创造节点
Node* CreatTNode(int val){
    Node *newNode =  (Node*)malloc(sizeof(Node));

    newNode->val = val;
    newNode->left = NULL;
    newNode->right = NULL;
    return newNode;
}

//递归方式构建二叉树
Node* buildTree(int a[], int index){
    /*
    int val;
    printf("输入节点的值(输入-1表示空节点)\n");
    scanf("%d",&val);
    */

    if(a[index] == -1  || index >= Size)   return NULL;    //空节点
    else{
        Node *newNode = CreatTNode(a[index]);
        printf("构建节点 %d 的左子数:\n",a[index]);
        newNode->left = buildTree(a,index*2);
        printf("构建节点 %d 的右子数:\n",a[index]);
        newNode->right = buildTree(a,index*2+1);

        return newNode;
    }
}

//打印先序遍历二叉树
void printTraverse(Node* root){
    if(root == NULL)    return;

    printf(" %d", root->val);
    printTraverse(root->left);
    printTraverse(root->right);
}

// 层次遍历以打印树函数
void printTree(Tree root) {
    if (root == nullptr) {
        return;
    }

    queue<Node*> q;
    q.push(root);   //头节点入队

    while (!q.empty()) {    //一次循环是树的一层
        int size = q.size();    //当前层有多少个节点
        for (int i = 0; i < size; i++) {
            Node* node = q.front();
            q.pop();
            printf("%-3d",node->val);   //每出队一个节点就打印此节点，并在下面将此节点左右子女入队

            if (node->left) { 
                q.push(node->left);
            }
            if (node->right) {
                q.push(node->right);
            }
        }
        cout << endl;  // 在每一层的末尾换行打印
    }
}

//释放二叉树内存
void FreeTree(Node *root){
    if(root == NULL)    return;
    
    FreeTree(root->left);
    FreeTree(root->right);
    free(root);
}

//求树的深度(递归)
int Tree_Depth(Tree T){
    if(T == NULL)   return 0;
    else{
        int l = Tree_Depth(T->left);
        int r = Tree_Depth(T->right);

        //树的深度=max(左子树深度，右子树深度)+1
        return max(l,r)+1;
    }
}

//找到x及其父节点并输出两者地址
bool find_Node(Tree &T, int x){
    if(T == NULL)   return false;
    else{
        if(T->val == x){
            printf("找到x的地址为: %p\n",&T->val);
            return true;
        }
        find_Node(T->left,x);
        find_Node(T->right,x);
    }
    return false;
}

//数组的初始化
void InitArr(int a[]){
    for(int i=0;i<Size;i++)     a[i] = -1;
    printf("要往二叉树中插入多少个数(最大值为 %d ):\n",Size-1);
    int num;
    scanf("%d",&num);

    for(int i=0;i<=num;i++)  a[i] = i;
}

int main(){
    int a[Size];
    InitArr(a);

    Tree T;
    T = buildTree(a,1);
    system("pause");
    printf("二叉树遍历结果（先序遍历）:\n");
    //printTraverse(T);
    printTree(T);

    //功能1：返回值为x的节点的地址
    printf("\n");
    find_Node(T,5);

    FreeTree(T);
    free(T);
    T = NULL;

    system("pause");
    return 0;
}