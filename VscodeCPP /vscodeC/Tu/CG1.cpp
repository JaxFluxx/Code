#include <bits/stdc++.h>
using namespace std;

/*
邻接表中的每个链表的头节点与其后的所有节点都是相邻节点。

在邻接表的表示法中，NodeList是一个vector容器，其中每个元素都表示一个节点的邻接链表，而每个邻接链表的头节点指向与该节点直接相邻的其他节点。

具体地说，对于Graph结构体中的NodeList数组中的每个元素，它们都是指向一个链表的头节点。这个链表中的每个节点代表与该特定节点相关联的其他节点。链表的头节点和链表中的其他节点都是相邻的。

所以，确切地说，NodeList中的每个元素都指向的是一个链表的头节点，而这个链表的头节点和链表中的其他节点是相邻关系。
*/

//节点定义
typedef struct Node{
    string name;
    int weight;
    Node* next;
}Node;

//创建图
typedef struct Graph{
    int numNode;
    vector<Node*> NodeList;
}Graph;

//初始化图
void InitGraph(Graph* G, int numNode){
    G->numNode = numNode;
    //将NodeList的数目改为numNode(多删少补)，并全部赋值为NULL
    G->NodeList.resize(numNode, NULL);
}

//创建节点
Node* createNode(const string& name){
    Node* newNode = (Node*)malloc(sizeof(Node));
    newNode->weight = 0;
    newNode->name = name;
    newNode->next = NULL;
    return newNode;
}

//添加边
    //传入参数：图，要连接的节点下标，目标节点名字
void addEgde(Graph* G, const string& name1, const string& name2){
    Node* newNode1 = createNode(name1);
    Node* newNode2 = createNode(name2);

    int index1 = findIndex(G,name1);
    int index2 = findIndex(G,name2);

    //在节点1后添加节点2
    newNode2->next = G->NodeList[index1];
    G->NodeList[index1] = newNode2;

    //在节点1后添加节点2
    newNode1->next = G->NodeList[index2];
    G->NodeList[index2] = newNode1;
}


//根据名字找到其在图中的下标
int findIndex(Graph* G, const string& name){
    for(int i = 0; i < G->numNode; i++){
        if(G->NodeList[i]->name == name){
            return i;
        }
    }
    //执行到这一步则证明找不到
    return -1;
}

//判断两个顶点是否相邻
bool isAdjcent(Graph* G, const string& name1, const string& name2){
    Node* curr = G->NodeList[findIndex(G, name1)];
    while(curr != NULL){
        if(curr->name == name2){
            return true;
        }
        curr = curr->next;
    }
    return false;
}

//获取一个顶点的所有邻居
void getNeighbors(Graph* G, const string& name){
    cout << name << " 的邻居如下: ";
    int index = findIndex(G, name);
    Node* curr = G->NodeList[index];
    while(curr != NULL){
        cout << curr->name << " ";
        curr = curr->next;
    }
    cout << endl;
}

//在图中添加一个顶点
void addNode(Graph* G, const string& name){
    Node* newNode = createNode(name);
    G->NodeList.push_back(newNode);
    G->numNode++;
}

//删除一个点
void deleteNode(Graph* G,const string& name){
    //判断节点是否存在
    int index = findIndex(G,name);
    if(index == -1){
        printf("\n图中无此节点!");
        return;
    }

    Node* curr = G->NodeList[index];
    Node* prev = NULL;
    while(curr != NULL){
        if(curr->name == name){
            G->NodeList[index] = curr->next;
            free(curr);
            
            printf("\n %s 节点已删除！",name);
        }else{
            prev->next = curr->next;
            free(curr);

            printf("\n %s 节点已删除！",name);
        }
        prev = curr;
        curr = curr->next;  
    }
    G->numNode--;
}

//获取第一个邻居
void firstNeighbor(Graph* G, const string& name){
    int index = findIndex(G, name);
    //判断节点是否存在
    if(index == -1){
        printf("\n图中无此节点!");
        return;
    }

    //判断该节点是否有邻居
    if(G->NodeList[index]->next == NULL){
        printf("\n此节点没有邻居!");
        return;
    }else{
        printf("\n%s 的第一个邻居为 %s",name , G->NodeList[index]->next->name);
    }
}

//设置边的值
void setEdgeValue(Graph* G, const string& name1, const string& name2, int weight){
    int index = findIndex(G,name1);
    Node* curr = G->NodeList[index];

    while(curr != NULL){
        if(curr->name == name2){
            curr->weight = weight;
            printf("\n%s 和 %s 之间边的权重已设置为: %d",name1,name2,curr->weight);

            break;
        }
        curr = curr->next;
    }
}

//获取边的值
int getEgdeValue(Graph* G, const string& name1, const string& name2){
    int index = findIndex(G,name1);
    Node* curr = G->NodeList[index];

    while(curr != NULL){
        if(curr->name == name2){
            printf("\n%s 和 %s 之间边的权重为: %d",name1,name2,curr->weight);
            return curr->weight;

            break;
        }
        curr = curr->next;
    }

    //没有找到
    return -1;
}



void testGraph() {
    Graph graph;
    InitGraph(&graph, 5);

    addNode(&graph, "A");
    addNode(&graph, "B");
    addNode(&graph, "C");
    addNode(&graph, "D");
    addNode(&graph, "E");

    addEgde(&graph, "A", "B");
    addEgde(&graph, "A", "C");
    addEgde(&graph, "B", "D");
    addEgde(&graph, "C", "E");

    // 测试获取邻居
    getNeighbors(&graph, "A");

    // 测试判断两个顶点是否相邻
    cout << "A 和 B 是否相邻： " << isAdjcent(&graph, "A", "B") << endl;
    cout << "A 和 C 是否相邻： " << isAdjcent(&graph, "A", "C") << endl;
    cout << "A 和 D 是否相邻： " << isAdjcent(&graph, "A", "D") << endl;

    // 测试删除节点
    deleteNode(&graph, "D");
    getNeighbors(&graph, "B");

    // 测试设置边的权重和获取边的权重
    setEdgeValue(&graph, "A", "B", 10);
    cout << "A 和 B 之间边的权重为： " << getEgdeValue(&graph, "A", "B") << endl;
}


int main() {
    testGraph(); // 调用测试函数

    // 暂停程序运行，防止控制台窗口一闪而过
    system("pause");
    return 0;
}