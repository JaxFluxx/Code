#include<iostream>
#include<stdio.h>
#include<iomanip>
#include<algorithm>
#include<string>
#include<map>
using namespace std;
//此程序可以在dev c++运行
void Printmap(map<string,int>&m);

void test01(){
    map<string,int>m;  //默认构造
    m.insert(pair<string,int>("david",1234));
    m.insert(pair<string,int>("damn it",7890));
    m.insert(pair<string,int>("OMG",2697));
    Printmap(m);
}

void Printmap(map<string,int>&m){
    for(map<string,int>::iterator it=m.begin();it!=m.end();it++){
        cout << "name:" << setw(8) << setiosflags(ios::left) << it->first;
		cout << " password :" << (*it).second << endl;
    }
}

int main(){
    test01();
    cin.get();
    return 0;
}