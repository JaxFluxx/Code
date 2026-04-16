#include <stdio.h>
#include <stdlib.h>

#define MAX_SIZE 100

// 图的邻接矩阵表示
typedef struct {
    int matrix[MAX_SIZE][MAX_SIZE];
    int numVertices;
} Graph;

// 初始化图
void initGraph(Graph *G, int numVertices) {
    G->numVertices = numVertices;

    // 初始化邻接矩阵为0
    for (int i = 0; i < numVertices; i++) {
        for (int j = 0; j < numVertices; j++) {
            G->matrix[i][j] = 0;
        }
    }
}

// 判断两个顶点是否相邻
int isAdjacent(Graph G, int x, int y) {
    if (G.matrix[x][y] == 1 && G.matrix[y][x] == 1)
        return 1;
    return 0;
}

// 获取一个顶点的所有邻居
void getNeighbors(Graph G, int x) {
    printf("Neighbors of vertex %d: ", x);
    
    for (int i = 0; i < G.numVertices; i++) {
        if (G.matrix[x][i] == 1) {
            printf("%d ", i);
        }
    }
    
    printf("\n");
}

// 添加顶点
void insertVertex(Graph *G, int x) {
    if (G->numVertices < MAX_SIZE) {
        G->numVertices++;
        
        // 将新增的顶点与其他顶点的连接关系初始化为0
        for (int i = 0; i < G->numVertices; i++) {
            G->matrix[i][G->numVertices - 1] = 0;
            G->matrix[G->numVertices - 1][i] = 0;
        }
    }
}

// 删除顶点
void deleteVertex(Graph *G, int x) {
    if (x < G->numVertices) {
        // 将与待删除顶点相连的边的连接关系置为0
        for (int i = 0; i < G->numVertices; i++) {
            G->matrix[i][x] = 0;
            G->matrix[x][i] = 0;
        }
        
        // 移动其他顶点的位置
        for (int i = x; i < G->numVertices - 1; i++) {
            for (int j = 0; j < G->numVertices; j++) {
                G->matrix[j][i] = G->matrix[j][i + 1];
                G->matrix[i][j] = G->matrix[i + 1][j];
            }
        }
        
        G->numVertices--;
    }
}

// 添加边
void addEdge(Graph *G, int x, int y) {
    if (x < G->numVertices && y < G->numVertices) {
        G->matrix[x][y] = 1;
        G->matrix[y][x] = 1;
    }
}

// 获取第一个邻居
int firstNeighbor(Graph G, int x) {
    for (int i = 0; i < G.numVertices; i++) {
        if (G.matrix[x][i] == 1) {
            return i;
        }
    }
    
    return -1;
}

// 获取下一个邻居
int nextNeighbor(Graph G, int x, int y) {
    for (int i = y + 1; i < G.numVertices; i++) {
        if (G.matrix[x][i] == 1) {
            return i;
        }
    }
    
    -1;
}

// 设置边的值
void setEdgeValue(Graph *G, int x, int y, int value) {
    if (x < G->numVertices && y < G->numVertices) {
        G->matrix[x][y] = value;
        G->matrix[y][x] = value;
    }
}

// 获取边的值
int getEdgeValue(Graph G, int x, int y) {
    if (x < G.numVertices && y < G.numVertices) {
        return G.matrix[x][y];
    }
    
    return -1;
}

int main() {
    Graph G;
    int numVertices = 5;

    initGraph(&G, numVertices);

    addEdge(&G, 0, 1);
    addEdge(&G, 0, 4);
    addEdge(&G, 1, 2);
    addEdge(&G, 1, 3);    addEdge(&G, 1, 4);
    addEdge(&G, 2, 3);
    addEdge(&G, 3, 4);

    printf("Adjacent(0, 1): %d\n", isAdjacent(G, 0, 1));
    getNeighbors(G, 1);

    insertVertex(&G, 5);
    addEdge(&G, 0, 5);
    addEdge(&G, 1, 5);
    addEdge(&G, 2, 5);
    addEdge(&G, 3, 5);
    addEdge(&G, 4, 5);
    printf("Neighbors of vertex 5: ");
    for (int i = 0; i < G.numVertices; i++) {
        if (G.matrix[5][i] == 1) {
            printf("%d ", i);
        }
    }
    printf("\n");
    
    deleteVertex(&G, 5);
    getNeighbors(G, 5);
    
    setEdgeValue(&G, 0, 1, 2);
    printf("Edge value of (0, 1): %d\n", getEdgeValue(G, 0, 1));
    
    system("pause");
    return 0;
}