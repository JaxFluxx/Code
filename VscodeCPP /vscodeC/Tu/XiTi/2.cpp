// !!!
//寻找最短路径
//https://blog.csdn.net/qq_48508278/article/details/121447890

#include <bits/stdc++.h>
using namespace std;

int point, edge;

//邻接矩阵
static int arr[100][100] = {0};
//记录结点是否被访问过
static int flag[100] = {0};

//到a点的距离数组
static int _distance[100] = {0};
//邻接矩阵只保留上三角区。主对角线全部清零
int _arr[100][100] = {0};
//记录节点是否被访问过
int _flag[100] = {0};

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

//计算最短路径（广度优先）
void BFS(int a, int b) {
    queue<int> q;
    // 起点元素入队
    q.push(a);
    _flag[a] = 1;   // 起点元素已经被访问过
    _distance[a] = 0;

    while (!q.empty()) {
        // 让所有相邻点入队，并计算距离
        for (int i = 0; i < point; i++) {
            if (arr[q.front()][i] == 1 && _flag[i] == 0)    // 元素与队首元素相邻，且这个元素没有被访问过
            {
                q.push(i);
                _flag[i] = 1;  // 标记此元素已经入队过

                //printf("\n%d和%d",_distance[q.front()] + 1, _distance[i]);
                if (_distance[q.front()] + 1 < _distance[i]) {
                    _distance[i] = _distance[q.front()] + 1;
                    //printf("_distance[%d]修改为%d",i,_distance[i]);
                }
            }
        }
        q.pop();
    }
}



int main(){
    for(int i = 0; i < 100; i++){
        _distance[i] = 999;
    }
        

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
    if(flag[y] == 1){
         BFS(x,y);
        printf("The length of the shortest path between %d and %d is %d.",x,y,_distance[y]);
    }
    else
        printf("There is no path between %d and %d.",x,y);



    system("pause");
    return 0;
}