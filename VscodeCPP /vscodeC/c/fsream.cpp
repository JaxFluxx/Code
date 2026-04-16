#include<fstream>
#include<iostream>
#include<cstring>
using namespace std;

void test1(){  //写文件
    ofstream ofs;
    ofs.open("test.txt",ios::out);
    ofs << "Hello World!" << endl;
    ofs.close();
    cout << "文件已生成";
}

void test2(){
    ifstream ifs;
    ifs.open("test.txt",ios::in);  //打开文件
    if(!ifs.is_open()){  //bool型函数is_open()判断打开文件是否成功，成功返回1
        cout << "文件打开失败！" << endl;
    }
    /*
    char buf[1024] = {0};  //第一种方式
    while(ifs >> buf){
        cout << buf;
    }
    */
    string buf;
    while(getline(ifs,buf)){
        cout << buf ;
    }
}
int main(){
    test2();
    cin.get();
    return 0;
}