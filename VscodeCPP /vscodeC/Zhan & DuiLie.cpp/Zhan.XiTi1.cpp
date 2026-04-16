//出栈序列的合法性
//https://blog.csdn.net/seveny_/article/details/81508118

#include <bits/stdc++.h>
using namespace std;

int main(){
    int M, N, K;
    scanf("%d %d %d",&M, &N, &K);

    stack<int> a[1009];     //创建了1009个动态栈
    int b[1009];

    //主体
    for(int i = 1;i <= K; i++){  //需要检查K个数列
        //接收单行序列
        for(int k = 1;k <= N; k++){
            scanf("%d",&b[k]);
        }

        int test = 1, index = 1;    //test用来检测是否溢出（为0时满），index为b[]下标

        for(int l = 1; l <= N;l++){  //N个元素依次压入栈

        
            a[i].push(l);
            //判断溢栈
            if(a[i].size() > M)
                test = 0;
            
            //如果栈顶元素与序列前头元素相同，栈顶元素出栈出栈，数组下标后移
            while(a[i].top() == b[index]){
                index++;
                a[i].pop();
                if(a[i].empty())
                    break;
            }
        }

        if(test == 0){
            printf("NO\n");
        }else{
            if(a[i].empty()){
                printf("YES\n");
            }else{
                printf("NO\n");
            }
        }
    }

    system("pause");
    return 0;
}
