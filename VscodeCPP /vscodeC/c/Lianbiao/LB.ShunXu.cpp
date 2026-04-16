#include<stdio.h>
#include<stdlib.h>
using namespace std;
const int InitSize = 10;

//结构体声明
typedef struct {
	int* data;
	int MaxSize;
	int length;  //目前存入数据数
}SeqList;

//顺序表初始化
void InitList(SeqList& L) {
	//用malloc申请空间
	L.data = (int*)malloc(sizeof(int) * InitSize);
	L.length = 0;
	L.MaxSize = InitSize;
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//增加动态数组长度
void IncreaseSize(SeqList& L, int len) {
	int* p = L.data;
	L.data = (int*)malloc(sizeof(int) * (L.MaxSize + len));	//重新申请空间
	for (int i = 0; i < L.length; i++)
		L. data[i] = p[i];		//将数据赋值到新区域
	L.MaxSize = L.MaxSize + len;
	free(p);
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//插入
bool ListInsert(SeqList &L,int i,int e){    //链表，插入位，，插入数
    if(i<1 || i>L.length+1)     return false;       //插入数与原顺序表有空隙，返回false
    if(L.length>=L.MaxSize)     return false;		//插入数在数组空间外
    for(int j=L.length;j>=i;i--)
        L.data[j] = L.data[j-1];
    L.data[i-1] = e;
    L.length++;
    return true;
}

//按位删除
bool ListDelete(SeqList &L,int i,int &e){	//顺序表，要删除第几位数，删除数
	if(i<1 || i>L.length+1)     return false;
	e = L.data[i];
	for(int j=i;j<=L.length;i++)
		L.data[j-1] = L.data[j];
	L.length--;
	return true;
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//按值查找，返回位次
int LocateElem(SeqList L,int e){
	for(int i=0;i<L.length;i++)
		if(L.data[i]==e)
			return i;
	return 0;
}

int main(){
	SeqList L;
	InitList(L);
	IncreaseSize(L, 5);
    system("pause");
	return 0;
}