//!! 最小生成树（并查集）
//https://blog.csdn.net/qq_51916951/article/details/122004965

//思路：1.使用kruskal算法（破圈法）生成最小生成树
//2.每次新接入一条边，都使用并查集来找到新两个节点的根结点是否同属一棵树，同则代表加入此边会构成回路，不可以加入此边，不同则将第二点归并入第一点所在的树
//3.最后检查并查集是否所有点的根节点都是同样的（即所有点联通）,同样则输出KPL

#include <bits/stdc++.h>
using namespace std;
const int N = 1e5 + 5;

typedef struct Node{
    int a, b, c;
}Node;

Node arr[N];

int n, m, BingCha[N] = {0}, flag, sum;

//比较权值大小
bool test(Node x, Node y){
    //小于返回1，大于返回0
    return x.c < y.c;
}

//查找两个两个根节点
int findRoot(int x){
    if(x != BingCha[x])
        BingCha[x] = findRoot(BingCha[x]);

    return BingCha[x];
}

int main(){
    scanf("%d %d",&n, &m);  //点，边

    //并查集初始化,每一个节点的根节点都是自己
    for(int i = 1; i <= n; i++)
        BingCha[i] = i;

    //接收数据
    for(int i = 0; i < m; i++){
        scanf("%d %d %d",&arr[i].a,&arr[i].b,&arr[i].c);
    }

    //从小到大排序所有道路
    sort(arr,arr + m,test);

    for(int i = 0; i < m; i++){
        if(findRoot(arr[i].a) != findRoot(arr[i].b)){
            //将a节点并入b节点所在的树
            BingCha[findRoot(arr[i].a)] = findRoot(arr[i].b);

            sum = sum + arr[i].c;
        }
    }

    //判断所有节点是否都已经联通
    flag = 0;
    for(int i = 1; i <= n; i++)
        if(findRoot(i) == i)
            flag++;

    if(flag == 1)
        printf("%d",sum);

    system("pause");
    return 0;
}