#include <stdio.h>
#include <stdlib.h>

#define MAX_VERTICES 100

// 图的邻接表表示
typedef struct Node {
    int vertex;
    int weight;     //此点后面边的权重
    struct Node* next;
} Node;

typedef struct {
    int numVertices;    //顶点个数
    Node* adjList[MAX_VERTICES];    //创建一个指向Node的指针列表
} Graph;

// 创建节点
Node* createNode(int v, int weight) {
    Node* newNode = (Node*)malloc(sizeof(Node));
    newNode->vertex = v;
    newNode->weight = weight;
    newNode->next = NULL;
    return newNode;
}

// 初始化图
void initGraph(Graph* G, int numVertices) {
    G->numVertices = numVertices;

    for (int i = 0; i < numVertices; i++) {
        G->adjList[i] = NULL;
    }
}

// 添加边(头插)
void addEdge(Graph* G, int src, int dest, int weight) {
    //创建点并连接其他点
    Node* newNode = createNode(dest, weight);
    newNode->next = G->adjList[src];
    G->adjList[src] = newNode;
}

// 判断两个顶点是否相邻
int isAdjacent(Graph* G, int x, int y) {
    Node* curr = G->adjList[x];
    while (curr != NULL) {
        if (curr->vertex == y) {
            return 1;
        }
        curr = curr->next;
    }
    return 0;
}

// 获取一个顶点的所有邻居
void getNeighbors(Graph* G, int x) {
    printf("Neighbors of vertex %d: ", x);
    Node* curr = G->adjList[x];
    while (curr != NULL) {
        printf("%d ", curr->vertex);
        curr = curr->next;
    }
    printf("\n");
}

// 添加顶点
void insertVertex(Graph* G, int x) {
    if (x >= MAX_VERTICES) {
        printf("Graph can't have more than %d vertices\n", MAX_VERTICES);
        return;
    }

    G->adjList[x] = NULL;
    G->numVertices = x + 1;
}

// 删除顶点
void deleteVertex(Graph* G, int x) {
    if (x >= G->numVertices) {
        printf("Vertex %d does not exist in the graph\n", x);
        return;
    }

    // 删除与顶点x相关的边(遍历图)
    for (int i = 0; i < G->numVertices; i++) {
        //curr先走，prev后走
        Node* curr = G->adjList[i];
        Node* prev = NULL;
        while (curr != NULL) {
            if (curr->vertex == x) {
                if (prev == NULL) {     //要删除的是第一个节点
                    G->adjList[i] = curr->next;
                } else {    //普适情况
                    prev->next = curr->next;
                }
                free(curr);
                break;
            }
            prev = curr;
            curr = curr->next;
        }
    }
    G->numVertices--;
}

// 获取第一个邻居
int firstNeighbor(Graph* G, int x) {
    if (G->adjList[x] != NULL) {
        return G->adjList[x]->vertex;
    }
    return -1;
}

// 获取下一个邻居
int nextNeighbor(Graph* G, int x, int y) {
    Node* curr = G->adjList[x];
    while (curr != NULL && curr->vertex != y) {
        curr = curr->next;
    }
    if (curr != NULL && curr->next != NULL) {
        return curr->next->vertex;
    }
    return -1;
}

// 设置边的值
void setEdgeValue(Graph* G, int x, int y, int weight) {
    Node* curr = G->adjList[x];
    while (curr != NULL) {
        if (curr->vertex == y) {
            curr->weight = weight;
            break;
        }
        curr = curr->next;
    }
}

// 获取边的值
int getEdgeValue(Graph* G, int x, int y) {
    Node* curr = G->adjList[x];
    while (curr != NULL) {
        if (curr->vertex == y) {
            return curr->weight;
        }
        curr = curr->next;
    }
    return -1;
}

int main() {
    Graph G;
    initGraph(&G, 5);

    addEdge(&G, 0, 1, 1);
    addEdge(&G, 0, 4, 2);
    addEdge(&G, 1, 2,3);
    addEdge(&G, 1, 3, 4);
    addEdge(&G, 1, 4, 5);
    addEdge(&G, 2, 3, 6);
    addEdge(&G, 3, 4, 7);

    printf("Adjacent(0, 1): %d\n", isAdjacent(&G, 0, 1));
    getNeighbors(&G, 1);

    insertVertex(&G, 5);
    addEdge(&G, 0, 5, 8);
    addEdge(&G, 1, 5, 9);
    addEdge(&G, 2, 5, 10);
    addEdge(&G, 3, 5, 11);
    addEdge(&G, 4, 5, 12);

    printf("Neighbors of vertex 5: ");
    Node* curr = G.adjList[5];
    while (curr != NULL) {
        printf("%d ", curr->vertex);
        curr = curr->next;
    }
    printf("\n");

    deleteVertex(&G, 5);
    getNeighbors(&G, 5);

    setEdgeValue(&G, 0, 1, 13);
    printf("Edge value of (0, 1): %d\n", getEdgeValue(&G, 0, 1));

    system("pause");
    return 0;
}