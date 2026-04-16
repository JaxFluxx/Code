//从小到大排序并分成两组人
//对两波人求和并求差
#include<bits/stdc++.h>
using namespace std;
const int N = 1e5;


int main(){
    int arr[N], sum1, sum2, num, sum;
    scanf("%d",&sum);
    for(int i=1;i<=sum;i++){
        scanf("%d",arr[i]);
    }
    sort(arr[1],arr[sum]);
    for(int i=1;i<=n;i++)
        printf("%d",arr[i]);
}
