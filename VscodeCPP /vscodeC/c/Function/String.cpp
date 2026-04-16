#include<bits/stdc++.h>
using namespace std;

const int MaxSize = 20;
typedef struct{
    char ch[MaxSize];
    int length;
}SString;

//朴素模式匹配算法
int Index(SString S, SString T){
    int i=1, j=1;
    while(i<=S.length && j<=T.length){
        if(S.ch[i] == T.ch[j]){
            ++i;    ++j;    //继续比较后续字符
        }else{
            i = i-j+2;  //主串退回下一位置准备新一轮匹配
            j = 1;      //匹配串退回第一位准备新一轮匹配
        }
    }
    if(j>T.length)      //j指向匹配串的后面一位，意味着匹配串每一个字符全部匹配成功
        return i-T.length;
    else                //匹配失败
        return -1;
}

int main(){
    SString s1, s2;
    strcpy(s1.ch,"HelloWorld");
    strcpy(s2.ch,"World");
    s1.length = strlen(s1.ch);
    s2.length = strlen(s2.ch);

    int index = Index(s1,s2);
    if(index != -1) {
        cout << "在主串中匹配成功，匹配位置为：" << index << endl;
    } else {
        cout << "在主串中匹配失败" << endl;
    }

    system("pause");
    return 0;
}