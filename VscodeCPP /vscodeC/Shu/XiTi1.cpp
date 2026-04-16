// 2!
//https://pintia.cn/problem-sets/1736956456751456256/exam/problems/1736956500321890304?type=7&page=0
//以字符串的形式定义一棵二叉树的先序序列，若字符是‘#’, 表示该二叉树是空树，否则该字符是相应结点的数据元素。读入相应先序序列，建立二叉树，然后按层次遍历该二叉树并输出结点数据。
#include<bits/stdc++.h>
using namespace std;

static int _index = 0;

//结构体定义
typedef struct Node{
    char val;
    Node *left, *right;
}Node, *Root;


//创建节点函数
Node* createNode(char val){
    Node* newNode = (Node*)malloc(sizeof(Node));

    newNode->val = val;
    newNode->left = NULL;
    newNode->right = NULL;

    return newNode;
}

//构造二叉树(递归)
Node* buildTree(char str[]){
    
    if(str[_index] == '#'){
        _index++;
        return NULL;
    }   

    Node* newNode = createNode(str[_index]);
    _index++;

    //printf("构建节点 %c 的左子数:\n",str[_index-1]);
    newNode->left = buildTree(str);
    //printf("构建节点 %c 的右子数:\n",str[_index-1]);
    newNode->right = buildTree(str);
    return newNode;
}

//打印树(先序)
void Traverse(Root T){
    if(T == NULL)   return;
    else{
        printf("%c ",T->val);
        Traverse(T->left);
        Traverse(T->right);
    }
}

// 层次遍历以打印树函数
void printTree(Root root) {
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
            printf("%c",node->val);   //每出队一个节点就打印此节点，并在下面将此节点左右子女入队

            if (node->left) { 
                q.push(node->left);
            }
            if (node->right) {
                q.push(node->right);
            }
        }
        //cout << endl;  // 在每一层的末尾换行打印
    }
    return;
}


//销毁树
void DestroyTree(Root T){
    if(T == NULL)   return;

    DestroyTree(T->left);
    DestroyTree(T->right);
    free(T);
}

int main(){
    string a;
    cin >> a;

    //把string类型a转化为char型arr
    const char *str = a.c_str();
    
    //调用buildTree函数时，传入的参数str是一个指向常量的指针。在C++中，常量指针不能被修改，因此不能直接将其传递给需要修改指针的函数。
    Root T = buildTree(const_cast<char*>(str));
    printTree(T);
    //printf("\n");
    //DestroyTree(T);
    //free(T);
    T = NULL;

    system("pause");
    return 0;
}