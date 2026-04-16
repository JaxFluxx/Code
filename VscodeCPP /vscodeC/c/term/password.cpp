#include<iostream>
using namespace std;
class Point{
public:
    Point(double xx=0, double yy=0);
    void Set(double xx, double yy);
    void Move(double xx,double yy);
    void Output();
private:
    double x;
    double y;
};

/* 请在这里填写构造函数定义和3个成员函数定义 */

int main()
{
    Point x;
    x.Output();
    x.Set(1,2);
    x.Output();

    double a,b;
    cin >> a >> b;
    
    Point y(a,b);
    y.Output();
    y.Move(1,5);
    y.Output();
    return 0;
}

