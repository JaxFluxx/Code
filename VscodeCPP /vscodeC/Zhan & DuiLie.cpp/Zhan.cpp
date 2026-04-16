//相当于带指针的数组(分配内存固定)，特点是先进先出（LIFO）
#include<stdio.h>
#include<stdlib.h>
using namespace std;

const int MaxSize = 10;
typedef int ElemType;

typedef struct{
    ElemType data[MaxSize];
    int top;
}SeqStack;

//初始化栈
bool InitStack(SeqStack &S){
    S.top = -1;
    return true;
}

//判空
bool EmptyStack(SeqStack S){
    if(S.top == -1)     return true;
    else                return false;
}

//判满
bool FullStack(SeqStack S){
    if(S.top == MaxSize-1)  return true;
    else    return false;
}

//入栈
void PushStack(SeqStack &S, int num){
    //判满
    if(FullStack(S)){
        printf("栈满，无法入栈！\n");
        return;
    }
    
    S.top++;
    S.data[S.top] = num;
    printf("%d入栈成功\n",num);
    return;
}

//出栈
void PopStack(SeqStack &S){
    //判空
    if(FullStack(S)){
        printf("栈空，无法出栈!");
        return;
    }

    int Num = S.data[S.top];
    S.top--;
    printf("%d出栈成功\n",Num);
}

//输出栈
void ShowStack(SeqStack S){
    //判空
    if(EmptyStack(S)){
        printf("栈空!");
        return;
    }

    printf("栈中元素为:");
    for(int i = S.top;i >= 0; i--)
        printf(" %d",S.data[i]);
    printf("\n");
    return;
}

int main(){
    SeqStack S;
    InitStack(S);

    /*
    */
    PushStack(S,10);
    PushStack(S,20);
    PushStack(S,30);

    ShowStack(S);

    PopStack(S);
    PopStack(S);
    PopStack(S);
    ShowStack(S);

    system("pause");
    return 0;
}