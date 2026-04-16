// 路径判断
//给定一个有N个顶点和E条边的无向图，请判断给定的两个顶点之间是否有路径存在。
//https://blog.csdn.net/weixin_46623714/article/details/120711543

#include <bits/stdc++.h>
using namespace std;

//邻接矩阵
static int arr[100][100] = {0};
//记录结点是否被访问过
static int flag[100] = {0};

//深度遍历
void DFS(int num,int n){
    flag[num] = 1;  //标记自身已经被访问过

    //遍历与当前结点相邻的所有结点
    for(int i = 0;i < n;i++){
        if(flag[i] == 0 && arr[num][i] == 1){
            flag[i] = 1;

            DFS(i,n);
        }
    }
}


int main(){
    int point, edge;
    scanf("%d %d",&point,&edge);

    //主对角线全部赋值1
    for(int i=0; i<point; i++)
        arr[i][i] = 1;

    //接入图
    for(int i=0; i<edge; i++){
        int x, y;
        scanf("%d %d",&x,&y);
        arr[x][y] = 1;
        arr[y][x] = 1;
    }

    int x, y;
    scanf("%d %d",&x,&y);
    DFS(x,point);

    //检查y节点是否被访问过
    if(flag[y] == 1)
        printf("There is a path between %d and %d.",x,y);
    else
        printf("There is no path between %d and %d.",x,y);


    system("pause");
    return 0;
}