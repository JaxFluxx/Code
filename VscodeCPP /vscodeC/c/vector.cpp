#include<iostream>
#include<algorithm>
#include<vector>
#include<string>

const int N = 1e4;

using namespace std;
 

 class Person{
public:
    int age;
    string name;
    Person(string str,int age){  //有参构造函数
        this->name = str;
        this->age = age;
    }
 };

void test01(){
    Person p1("aaa",10);
    Person p2("BBB",10);
    Person p3("CcC",10);

    vector<Person> v;  //创建一个放Person的容器v
    vector<Person>::iterator it;  //给v容器定义迭代器
    //向容器里放入三个Person
    v.push_back(p1);
    v.push_back(p2);
    v.push_back(p3);

    for(it=v.begin();it!=v.end();it++){
        cout <<"姓名："<< (*it).name <<" 年龄："<<(*it).age<<endl;
    }
}

int main(){ 
    test01();
    cin.get();
    return 0;
}