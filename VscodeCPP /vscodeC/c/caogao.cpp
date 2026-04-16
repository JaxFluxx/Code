#include<bits/stdc++.h>
using namespace std;

void hano(int n,char x,char y, char z);

int main(){
    int n;
    char x, y, z;   //起始，目的，过渡
    scanf("%d",&n);
    scanf("%c %c %c",&x,&y,&z);
    hano(n,x,y,z);
    system("pause");
    return 0;
}

void hano(int n,char x,char y, char z){
    if(n==1)
        printf("%d: %c -> %c\n",n,x,y);
    else{
        
    }
}