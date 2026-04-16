//!七桥问题
//用并查集检查是否为连通图
//两个数组，并查集,边数

#include <bits/stdc++.h>
using namespace std;

int BC[1005] = {0};
int Du[1005] = {0};

int findRoot(int x){
    if(BC[x] != x)
        BC[x] = findRoot(BC[x]);
    return BC[x];
}

int main(){
    int point, edge;
    scanf("%d %d",&point,&edge);

    //初始化并查集
    for(int i = 1; i <= point; i++)
        BC[i] = i;
    //初始化度
    for(int i = 1; i <= point; i++)
        Du[i] = 0;

    //接收数据
    for(int i = 1; i <= edge; i++){
        int x, y;
        scanf("%d %d",&x, &y);

        //记录点的度集合
        Du[x] += 1;
        Du[y] += 1;
        
        //x点与y点如果不同属于一棵树
        if(findRoot(x) != findRoot(y)){
            //将a节点并入b节点所在的树
                BC[findRoot(x)] = findRoot(y); 
        }
    }

    //检查是否为连通图
    int flag = 0, flag1 = 0;
    for(int i = 1; i <= point; i++)
        if(findRoot(i) == i)
            flag++;
    //如果不是是连通图,则
    if(flag != 1)
            printf("0");
    //如果是连通图，检查有无奇度顶点
    else{
        for(int i = 1; i <= point; i++)
            if(Du[i] % 2 != 0)
                flag1++;
        
        if(flag1 == 0)
            printf("1");
        else
            printf("0");
    }


    system("pause");
    return 0;
}