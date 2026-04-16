//实现计算器的抽象类

#include<bits/stdc++.h>
using namespace std;

class AbstractCaculator{  //父类
public:
    int m_Num1;
    int m_Num2;

//理解为在子类中选择调用虚函数，父类虚函数只是有一个声明（每一个子类就是一次函数重载）
//调用哪个子类的函数取决于创建什么类型的子类对象
    virtual int getResult(){  //完全虚函数————给子类重载建框架
        return 0;
    }
};

class AddCaculator :public AbstractCaculator{  //子类加法
public:
    int getResult(){
        return m_Num1 + m_Num2;
    }
};

class SubCaculator :public AbstractCaculator{  //子类减法
public:
    int getResult(){
        return m_Num1 - m_Num2;
    }
};

class MulCaculator :public AbstractCaculator{  //子类乘法
public:
    int getResult(){
        return m_Num1 * m_Num2;
    }
};

void test(); //测试加法、减法、乘法
void test(){
    //父类指针指向子类对象
        //在父类框架下创建指针指向子类，然后执行子类重载函数
    AbstractCaculator *abc = new AddCaculator; //new返回开辟出来的地址
    abc->m_Num1 = 10;
    abc->m_Num2 = 20;

    cout << abc->m_Num1 <<"+"<< abc->m_Num2 <<"="<< abc->getResult() << endl;
    delete abc;  //删除的是abc指向的内存数据，指针还存在

    abc = new SubCaculator; //new返回开辟出来的地址
    abc->m_Num1 = 10;
    abc->m_Num2 = 20;

    cout << abc->m_Num1 <<"-"<< abc->m_Num2 <<"="<< abc->getResult() << endl;
    delete abc;  //删除的是abc指向的内存数据，指针还存在

    abc = new MulCaculator; //new返回开辟出来的地址
    abc->m_Num1 = 10;
    abc->m_Num2 = 20;

    cout << abc->m_Num1 <<"*"<< abc->m_Num2 <<"="<< abc->getResult() << endl;
    delete abc;  //删除的是abc指向的内存数据，指针还存在
}

int main(){
    test();
    system("pause");
    return 0;
}