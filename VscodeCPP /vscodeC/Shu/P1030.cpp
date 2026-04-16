/*
思路：后序排列的最后一个字母是根，标记下来后在后序中尾删这个字母
    中序中找到该字母，中序里此字母左右为此字母（即根）的左右子树
    也将后序分为左右子树
    打印/递归左子树/递归右子树
*/

#include<iostream>
#include<cstring>
#include<string.h>
#include<stdio.h>

using namespace std;

string in,post;

void work(string in, string post){
    if(in.empty() || post.empty())
        return;

    char root = post[post.size()-1];
    int index = in.find(root);

    //中序找出左子树、右子树
    string in_left = in.substr(0,index);
    string in_right = in.substr(index+1);

    //后序找出左子树、右子树
    string post_left = post.substr(0,index);
    string post_right = post.substr(index,post.size()-index-1);

    cout << root;
    work(in_left,post_left);
    work(in_right,post_right);
}

int main(){
    cin >> in;
    cin >> post;
    work(in,post);

    system("pause");
    return 0;
}