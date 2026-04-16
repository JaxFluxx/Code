//next_permutation(始位，末尾的下一位)  求全排列下一个数并修改
//返回值为bool型，存在此数返回1，否则返回0
#include<bits/stdc++.h>
using namespace std;
int main(){
    int n;
    scanf("%d",&n);
    int num[15];
    for(int i=1;i<=n;i++)  //第一个要输出的数
        num[i] = i;
    do{
        for(int i=1;i<=n;i++)
            printf("%d",num[i]);
        printf("\n");
    }while(next_permutation(num+1,num+n+1));
    system("pause");
    return 0;
}