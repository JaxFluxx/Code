/*该程序接收学生总数N和总课程数K，并建立一个二维数组m来存储学生的名字和所选课程。数组m的每一行都存储一个学生的名字，而对应的列存储学生选修的课程。

首先，程序定义了一个map类型的变量m，它的key是学生的名字，value是一个vector<int>，表示所选课程的编号。然后，程序定义了一个迭代器it，用来遍历vector<int>类型的数据。

接下来，程序接收输入的课程信息。每次循环，程序会先接收一个课程编号a和该课程有多少名学生选修的信息b。然后，程序再循环接收b次学生的名字s，并将该学生的选课信息添加到m中。

最后，程序接收输入的学生名字，输出该学生选修课程的数量以及课程编号。程序首先根据输入的学生名字s查找到该学生的选课信息m[s]，并将选课的数量len保存下来。然后，程序将选修课程的编号排序，并依次输出。最后，程序换行输出换行符"\n"。

整体思路是，通过map将学生名字和选课信息关联起来，在接收学生名字后，可以直接通过map的key找到对应的选课信息，并输出结果。*/
#include<bits/stdc++.h>
using namespace std;
int main(){
    map<string,vector<int> > m;  //名字和动态数组绑定
    vector<int>::iterator It;  //迭代器
    int n, k;  char name[4];
    scanf("%d %d",&n,&k);
    while(k--){  //接收课程数据10
        int a, b;  //接收课程编号及其学生数
        scanf("%d %d",&a,&b);
        while(b--){  //添加课程到每个学生名下
            scanf("%s",name);
            m[name].push_back(a);  //m[s]代表的是以s为键的vector容器
        }
    }
    while(n--){  //输出来查询学生的课程
            scanf("%s",name);
            int len = m[name].size();
            printf("%s %d",name,len);
            sort(m[name].begin(),m[name].end());
            for(It=m[name].begin();It!=m[name].end();It++)
                printf(" %d",*It);
            printf("\n");
        }
    system("pause");
    return 0;
}