// ！
//寻找结点路径

//https://blog.csdn.net/zhanshenjiu9/article/details/133300638

#include<bits/stdc++.h>
using namespace std;

static int _index = 0;
static int _stack_index = 0;
static char _stack[10000] = {0};


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

//打印根结点到x结点的路径
   //函数功能为根据子结点，找到父结点并更新num.调用递归
void Find_num(Root T, char &num, char _stack[]){
    if(T == NULL){
            //printf("空");
            return;
    }     
    //遍历树找到这个数，并压入栈
    //printf("T %c index %d\n num %c\n",T->val,_stack_index,num);
    //printf("\n");

    //栈中最后一个数必为整棵树的根节点
    if(num == T->val){
        _stack[_stack_index] = T ->val;
        return;
    }

    else{
        if(T->left != NULL){
            if(T->left->val == num){
                _stack[_stack_index] = T->val;
                num = T->val;
                //printf("num%c",num);
                _stack_index++;
                return;
            }
        }
        if(T->right != NULL){
            if(T->right->val == num){
                _stack[_stack_index] = T->val;
                num = T->val;
                //printf("num%c",num);
                _stack_index++;
                return;
            }
        }
        
        Find_num(T->left,num,_stack);
        Find_num(T->right,num,_stack);
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

    char num;
    cin >> num;


    //把string类型a转化为char型arr
    const char *str = a.c_str();

    
    //调用buildTree函数时，传入的参数str是一个指向常量的指针。在C++中，常量指针不能被修改，因此不能直接将其传递给需要修改指针的函数。
    Root T = buildTree(const_cast<char*>(str));
    //printTree(T);

    //先把第一个数压入栈
    _stack[_stack_index] = num;
    _stack_index++;

    for(;_stack[_stack_index] != T -> val;)
        Find_num(T,num,_stack);

    _stack_index--;
    for(;_stack_index >= 0; _stack_index--)
        printf("%c ",_stack[_stack_index]);


    //printf("\n");
    //DestroyTree(T);
    //free(T);
    T = NULL;

    system("pause");
    return 0;
}