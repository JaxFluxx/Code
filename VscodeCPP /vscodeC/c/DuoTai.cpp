#include<bits/stdc++.h>
using namespace std;
 
 class Animal{  //父类
public:
    virtual void speak(){  //虚函数
        cout << "动物在说话" << endl;
    }
 };

 class Cat :public Animal{  //子类，继承父类的public
public:
    void speak(){  //重写函数
        cout << "小猫在说话" << endl;
    }
 };

void DoSpeak(Animal &p);  //函数 声明

 void DoSpeak(Animal &p){
    p.speak();
 }

 void test(){
    Cat cat;
    DoSpeak(cat);
 }

 int main(){
    test();
    system("pause");
    return 0;
 }