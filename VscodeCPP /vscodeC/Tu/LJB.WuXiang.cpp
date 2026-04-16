#include <stdio.h>
#include <stdlib.h>

// 图的邻接表表示
typedef struct Node {
    int vertex;
    int weight;
    struct Node* next;
} Node;

typedef struct {
    int numVertices;
    Node** adjList;
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
Graph* initGraph(int numVertices) {
    Graph* G = (Graph*)malloc(sizeof(Graph));
    G->numVertices = numVertices;
    
    // 创建邻接表数组
    G->adjList = (Node**)malloc(numVertices * sizeof(Node*));
    for (int i = 0; i < numVertices; i++) {
        G->adjList[i] = NULL;
    }
    
    return G;
}

// 添加边
void addEdge(Graph* G, int src, int dest, int weight) {
    // 添加从src到dest的边
    Node* newNode = createNode(dest, weight);
    newNode->next = G->adjList[src];
    G->adjList[src] = newNode;
    
    // 添加从dest到src的边
    newNode = createNode(src, weight);
    newNode->next = G->adjList[dest];
    G->adjList[dest] = newNode;
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
    if (x >= G->numVertices) {
        // 扩展邻接表数组
        G->adjList = (Node**)realloc(G->adjList, (x + 1) * sizeof(Node*));
        for (int i = G->numVertices; i <= x; i++) {
            G->adjList[i] = NULL;
        }
        G->numVertices = x + 1;
    }
}

// 删除顶点
void deleteVertex(Graph* G, int x) {
    if (x < G->numVertices) {
        // 删除与顶点x相关的边
        for (int i = 0; i < G->numVertices; i++) {
            Node* curr = G->adjList[i];
            Node* prev = NULL;
            while (curr != NULL) {
                if (curr->vertex == x) {
                    if (prev == NULL) {
                        G->adjList[i] = curr->next;
                    } else {
                        prev->next = curr->next;
                    }
                    free(curr);
                    break;
                }
                prev = curr;
                curr = curr->next;
            }
        }
        
        // 删除顶点x的邻接表
        Node* curr = G->adjList[x];
        while (curr != NULL) {
            Node* next = curr->next;
            free(curr);
            curr = next;
        }
        G->adjList[x] = NULL;
    }
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

// 释放图的内存
void freeGraph(Graph* G) {
    for (int i = 0; i < G->numVertices; i++) {
        Node* curr = G->adjList[i];
        while (curr != NULL) {
            Node* next = curr->next;
            free(curr);
            curr = next;
        }
    }
    free(G->adjList);
    free(G);
}

int main() {
    Graph* G = initGraph(5);

    addEdge(G, 0, 1, 1);
    addEdge(G, 0, 4, 2);
    addEdge(G, 1, 2, 3);
    addEdge(G, 1, 3, 4);
    addEdge(G, 1, 4, 5);
    addEdge(G, 2, 3, 6);
    addEdge(G, 3, 4, 7);

    printf("Adjacent(0, 1): %d\n", isAdjacent(G, 0, 1));
    getNeighbors(G, 1);

    insertVertex(G, 5);
    addEdge(G, 0, 5, 8);
    addEdge(G, 1, 5, 9);
    addEdge(G, 2, 5, 10);
    addEdge(G, 3, 5, 11);
    addEdge(G, 4, 5, 12);
    printf("Neighbors of vertex 5: ");
    for (int i = 0; i < G->numVertices; i++) {
        Node* curr = G->adjList[5];
        while (curr != NULL) {
            printf("%d ", curr->vertex);
            curr = curr->next;
        }
    }
    printf("\n");

    deleteVertex(G, 5);
    getNeighbors(G, 5);

    setEdgeValue(G, 0, 1, 13);
    printf("Edge value of (0, 1): %d\n", getEdgeValue(G, 0, 1));

    freeGraph(G);

    system("pause");
    return 0;
}