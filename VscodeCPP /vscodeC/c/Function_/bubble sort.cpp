//冒泡排序

//输入在第1行中给出N和K（1≤K<N≤100），在第2行中给出N个待排序的整数，数字间以空格分隔
//在一行中输出冒泡排序法扫描完第K遍后的中间结果数列，数字间以空格分隔，但末尾不得有多余空格。
#include<bits/stdc++.h>
using namespace std;

//
const int Num = 1e4 + 5;
int N, K;   //N为数组长度，K为冒泡排序几次

void bubbleSort(int arr[]) {
    for (int i = 1; i <= K ; i++) {     //改为 i <= N为正常
        for (int j = 1; j <= N - i; j++) {
            if (arr[j] > arr[j + 1]) {
                swap(arr[j], arr[j + 1]);
            }
        }
    }
    for(int i = 1; i < N; i++)
        printf("%d ",arr[i]);
    printf("%d",arr[N]);
}

int main(){
    scanf("%d %d",&N, &K);
    int arr[Num] = {0};
    for(int i = 1; i <= N; i++)
        scanf("%d", &arr[i]);

    bubbleSort(arr);

    system("pause");
    return 0;
}