#include <bits/stdc++.h>
using namespace std;
void test(int & x);

void test(int &x){
    x = 1024;
    printf("函数内部x=",x);
}

int main(){
    int x = 1;
    printf("调度前x=%d",x);
    test(x);
    printf("调度后x=%d",x);
}