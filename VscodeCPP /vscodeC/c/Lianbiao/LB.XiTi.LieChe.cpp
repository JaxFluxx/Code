#include <bits/stdc++.h>
using namespace std;

//首先第一个数肯定要占用一条轨道；后面的列车进来我先判断它是可以接到别的轨道后面还是要新开轨道
//判断可不可以接到别的轨道后面就是新数和所有轨道最末尾的数比较，一旦比较发现所有轨道末尾数字有比新数大的，就证明不用新开轨道
//接下来就判断新数要接到哪一条轨道后面：在所有比新数大的轨道末尾数里找最小那一个，那一条就是新数要进入的轨道
//如果要放入新的轨道，就把这个新数放到新轨道，然后标记这个新数字是轨道末尾数就可以了

void DoWork1(int N, int arr[]) {
    int _arr[N + 1]; //最多准备好9条轨道，记录本条轨道最小元素
    for (int i = 0; i <= N; i++)
        _arr[i] = 0;

    _arr[1] = arr[1]; //先把第一个数压入第一条轨道
    _arr[0] = 1; //存储已有多少条轨道

    int p; //arr的数组指针
    for (p = 2; p <= N; p++) { //一次循环插入一个数

        //printf("\n此次插入数%d",arr[p]);
        //找到比此数在所有已有轨道大的最接近的数
        int num, test = 0; //num为插入轨道末尾数，初值为一条轨道末尾最小数
        //if(arr[p] < _arr[1])    num = _arr[1];

        for (int i = 1; i <= _arr[0]; i++) {
            if (arr[p] < _arr[i]) {
                //printf("\n%d < %d\n",arr[p],_arr[i]);
                test = 1; //test为1，即找到了轨道，不用新建轨道
                num = _arr[i];
                //printf("%d\n",num);
                break;
            }
        }
        //有轨道插入后，找到最适合插入的轨道末尾元素
        if (test == 1) {
            for (int i = 1; i <= _arr[0]; i++) {
                if (num > _arr[i] && num > arr[p] && _arr[i] > arr[p]) {   //num为大于插入数，且所有轨道末位数中最小的
                    num = _arr[i];
                }
            }
        }
        //printf("末尾num:%d\n",num);
        //找到将要插入的轨道后刷新轨道值
        if (test == 1) {
            for (int i = 1; i <= _arr[0]; i++) {
                if (_arr[i] == num) {
                    _arr[i] = arr[p];
                }
            }
        } else if (test == 0) {
            _arr[0]++; //增加一条轨道
            _arr[_arr[0]] = arr[p]; // 修改这里，将新值赋给正确的位置
        }
    
        /*
        for(int i = 1; i <= _arr[0];i++ ){
            printf("%d ",_arr[i]);
        }        
        */
    }
    printf("%d", _arr[0]);
}

int main() {
    int N;
    scanf("%d", &N);
    int arr[N + 1];
    for (int i = 1; i <= N; i++) {
        scanf("%d", &arr[i]);
    }

    DoWork1(N, arr);

    system("pause");
    return 0;
}
