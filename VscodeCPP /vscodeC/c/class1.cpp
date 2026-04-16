#include<bits/stdc++.h>
using namespace std;
class Person{
private:

public:
    int age;
    int* height;
    static int m_A;
    //无参构造函数
    Person(){
    }
    //有参构造函数
    Person(int _age,int _height = 160){
        age = _age;
        height = &(_height);  //整形给指针赋值
    }
    //拷贝构造函数(深拷贝)
    Person(const Person &p){
        age = p.age;   
        height = new int();     //这两行等价height = new int(*p.height);
        *height = *(p.height);  //指针之间赋值
    }

    //析构函数
    ~Person(){
        if(height != NULL){
            delete height;
            height = NULL;
        }
    }

    //引用传递和this指针
    Person& PersonAddAge(Person p){  //返回值是引用传递，确保是对p2.age进行操作，而不是调用拷贝构造函数值传递返回
        this->age += p.age;
        return *this;
    }
    
};

int Person::m_A = 100;

void test(){
    Person p1(10,160);
    Person p2(p1);
    cout << "p1:" << p1.age << endl << *(p1.height) << endl;
    cout << Person::m_A;
}
void test01(){
    Person p1(10);  Person p2(10);
    p2.PersonAddAge(p1).PersonAddAge(p1).PersonAddAge(p1);
    cout << "p2.age = " << p2.age << endl;
}

int main(){
//    test();
    test01();
    system("pause");
    return 0;
}