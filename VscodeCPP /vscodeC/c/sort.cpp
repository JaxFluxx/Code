#include<stdio.h>
#include<bits/stdc++.h>
#include<string.h>
using namespace std;
void sort(int num[],int n)//把评分成绩从大到小排序 
{
	int i,j;
	int temp;
	for(i=0;i<n-1;i++)
	{
		for(j=0;j<n-i-1;j++)
		{
			if(num[j] < num[j+1])
			{
				temp = num[j];
				num[j] = num[j+1];
				num[j+1] = temp;
			}
		}
	}
}
void sort1(double score[],int n)//把评分成绩从大到小排序 
{
	int i,j;
	double temp;
	for(i=0;i<n-1;i++)
	{
		for(j=0;j<n-i-1;j++)
		{
			if(score[j] > score[j+1])
			{
				temp = score[j];
				score[j] = score[j+1];
				score[j+1] = temp;
			}
		}
	}
}
int main()
{
	int n,m,k;
	int i,j,nums,t; 
	double score[10001];//每个人的成绩评分总和 
	scanf("%d %d %d",&n,&k,&m);
	for(i=0;i<n;i++)
	{
		int num[11];//暂时存成绩
		for(j=0;j<k;j++)
		{
			scanf("%d",&num[j]);
		}
		sort(num,k);//排序 
		nums = 0;
		for(j=1;j<k-1;j++)//减去最低和最高评分 
		{
			nums += num[j];
		}
		score[i] = nums*1.0; 
		//printf("%d\n",nums);
	}
	sort1(score,n);//排序 
	for(i=n-m;i<n-1;i++)
		printf("%.3f ",score[i]/(k-2));
	printf("%.3f",score[n-1]/(k-2));
    system("pause");
	return 0;
} 
