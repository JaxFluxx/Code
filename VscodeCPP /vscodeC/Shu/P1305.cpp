/*
思路：用字符串的方式直接记录后序（左右根）
    输入的字符串[0]为根节点，在总串其位置前插入后面两个字母
*/

#include<iostream>
#include<string>
#include<cstring>

using namespace std;

void test(){
    int num;    string str, substr;
    cin >> num;
    cin >> str;

    num--;  //第一串除外
    while(num--){
        cin >> substr;
        
        //找到根在总串中是第几位
        int tick = str.find(substr[0]);

        str.erase(tick,1);  //总串中删除根节点
        str.insert(tick,substr);     //插入
    }
    for(int i=0;i<str.length();i++){
        if(str[i]!='*')     cout << str[i];     //跳过空节点
        else continue;
    }
}

int main(){
    test();

    system("pause");
    return 0;
}