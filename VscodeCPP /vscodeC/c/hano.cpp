#include<bits/stdc++.h>
#include<stdlib.h>
using namespace std;

void hano(int n,char x,char y,char z);

int main(){
    int n;
    char x, y, z;  //起始，目的，过渡
    scanf("%d\n",&n);
    scanf("%c %c %c",&x,&y,&z);
    hano(n,x,y,z);
    system("pause");
    return 0;
}
void hano(int n,char x,char y,char z){
    if(n==1)
        printf("%d: %c -> %c\n",n,x,y);
    else{
        hano(n-1,x,z,y);  //从n-1个盘从初始到过渡，借助目的
        printf("%d: %c -> %c\n",n,x,y);
        hano(n-1,z,y,x);  //从n-1个盘从过渡到过渡，借助初始
    }
}