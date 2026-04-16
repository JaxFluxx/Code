//题目：洛谷P1827

/*思路：通过前序“根左右”的特点，标记根节点（即前序字符串第一个），不断将中序、前序切割为左右两个子树
    找到根节点后，在前序字符串中删除本次根节点，因为后续用不到了
    利用递归思想调用自身两次，分别传入左前、左中和右前、右中
    函数最后写上打印语句，打印根节点
*/

//后序递归形式：自身函数（左子树）；自身函数（右子树）；操作语句（操作对象都是root）；
//https://zhuanlan.zhihu.com/p/73438175
#include<cstring>
#include<string>
#include<iostream>
#include<stdio.h>

using namespace std;

string pre, in;

void test(string pre,string in){
    //判空
    if(pre.empty() || in.empty())
        return;
    
    //通过根节点切割左右字数
    char root = pre[0];         //标记根节点
    int index = in.find(root);  //在中序找到根节点下标
    pre.erase(pre.begin());

    //左、右子树的中序遍历
    string left_in = in.substr(0,index);    //从第0位开始截取k位
    string right_in = in.substr(index+1);   //从[index+1]截取到末尾l

    //左、右子树的前序遍历
    //此时前序根节点已被删除
    string left_pre = pre.substr(0,index);    //前序中前index位是左子树
    string right_pre = pre.substr(index);   //从[index]截取到末尾

    //调用自身节点
    test(left_pre,left_in);
    test(right_pre,right_in);
    printf("%c",root);
}

int main(){
    cin >> in;
    cin >> pre;
    test(pre,in);
    
    system("pause");
    return 0;
}