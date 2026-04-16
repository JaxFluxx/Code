#include<stdio.h>
#include<stdlib.h>

typedef struct Node{
    int val;
    struct Node *left, *right;
}Node, *Tree;

// 创建节点
Node* BST_createNode(int val){
    Node* newNode = (Node*)malloc(sizeof(Node));
    
    newNode->val = val;
    newNode->left = NULL;
    newNode->right = NULL;

    return newNode;
}


// 插入节点
Node* BST_Insert(Tree T, int val){
    if(T == NULL)   // 为空表明已经查找到叶子节点下一层
        return BST_createNode(val);
    else if(val < T->val)   
        T->left = BST_Insert(T->left,val);
    else if(val > T->val)   
        T->right = BST_Insert(T->right,val);

    return T;
}

// 构建BST树
Tree BST_build(Tree T, int arr[], int arr_length){      //第一个插入的数是树的根节点
    for(int i = 0; i < arr_length; i++){
        T = BST_Insert(T, arr[i]);
    }
    return T;
}

// 中序打印
void inorderTraversal(Tree T){
    if(T != NULL){
        inorderTraversal(T->left);
        printf("%d ",T->val);
        inorderTraversal(T->right);
    }
}

// 搜索节点
Node* BST_searchNode(Tree T, int val){
    if(T == NULL || T->val == val)  // 包含查找成功和失败两种情况
        return T;
    else if(val < T->val)
        return BST_searchNode(T->left, val);
    else if(val > T->val)
        return BST_searchNode(T->right, val);
}

// 释放空间
void freeBST(Tree T){
    if(T != NULL){
        freeBST(T->left);
        freeBST(T->right);
        free(T);
    }
}

/////////////////////////////////////////////////////////////

/*
为了删除二叉搜索树中的节点，您可以按照以下步骤编写删除节点的函数：

首先，需要找到要删除的节点。根据二叉搜索树的性质，如果要删除的节点值小于当前节点的值，那么应该在当前节点的左子树中继续查找；如果要删除的节点值大于当前节点的值，那么应该在当前节点的右子树中继续查找；如果要删除的节点值等于当前节点的值，那么当前节点就是要删除的节点。

找到要删除的节点后，需要处理三种情况：
(a) 如果要删除的节点是叶子节点（没有子节点），可以直接删除该节点。
(b) 如果要删除的节点只有一个子节点（左子节点或右子节点），可以用子节点替换该节点。
? 如果要删除的节点有两个子节点，需要找到该节点的后继节点或前驱节点来替换它。后继节点可以定义为在排序顺序中紧随给定节点的节点，前驱节点可以定义为在排序顺序中紧靠给定节点之前的节点。

找到要删除节点的后继节点或前驱节点后，可以使用后继节点或前驱节点的值来替换要删除的节点的值，然后将问题转化为删除后继节点或前驱节点的情况。

重复步骤2和步骤3，直到找到要删除的节点是叶子节点的情况。
*/

//找到后继节点(右子树里中最左下角的数)
Node* findSuccessor(Node* node){
    while(node->left != NULL)
        node = node->left;
    return node;
}

//删除节点
Node* BST_Delete(Tree T, int val){
    if(T == NULL)
        return T;

    if(val < T->val)
        T->left = BST_Delete(T->left,val);
    else if(val > T->val)
        T->right = BST_Delete(T->right,val);
    else{
        //找到了要删除的节点
        
            //1.删除叶子节点
        if(T->left == NULL && T->right == NULL){
            free(T);
            T = NULL;
        }

            //2.有一个子节点的
                //有左节点
        else if(T->right == NULL){
            Node* temp = T;
            T = T->left;
            free(temp);
        }
                //有右节点
        else if(T->left == NULL){
            Node* temp = T;
            T = T->right;
            free(temp);
        }

            //3.有两个子节点
        else{
            Node* successor = findSuccessor(T->right);
            T->val = successor->val;    //替换
            T->right = BST_Delete(T->right, successor->val);    //在右子树删除这个节点
        }
    }
    return T;
}

/////////////////////////////////////////////////////////////

void test(){
    int arr[] = {1, 3, 5, 7, 9, 2, 4, 6, 8, 10};
    int arr_length = sizeof(arr) / sizeof(arr[0]);

    Tree T = NULL;
    T = BST_build(T, arr, arr_length);

    // 中序遍历并打印二叉搜索树的结点值
    printf("中序遍历结果：");
    inorderTraversal(T);
    printf("\n");

    // 在二叉搜索树中查找结点
    int searchKey = 6;
    Node* searchResult = BST_searchNode(T, searchKey);
    if (searchResult != NULL) {
        printf("在二叉搜索树中找到了结点值为 %d 的结点\n", searchKey);
    } else {
        printf("在二叉搜索树中未找到结点值为 %d 的结点\n", searchKey);
    }

    // 删除节点
    int deleteKey = 4;
    T = BST_Delete(T, deleteKey);

    // 打印删除节点后的中序遍历结果
    printf("删除节点后的中序遍历结果：");
    inorderTraversal(T);
    printf("\n");

    // 释放二叉搜索树的内存
    freeBST(T);
}

int main(){
    test();

    system("pause");
    return 0;
}