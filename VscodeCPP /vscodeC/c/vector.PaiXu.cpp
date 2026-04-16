//输入两个数组的长度和元素，并且输出合并后的升序数组
#include<bits/stdc++.h>
using namespace std;
const int N = 1e4;

int main(){
	int n1, n2, i;
	vector<int> v;
	vector<int>::iterator it;
	scanf("%d",&n1);
	for(i=1;i<=n1;i++){
		int x;
		scanf("%d",&x);
		v.push_back(x);
	}
	scanf("%d",&n2);
	for(i=1;i<=n2;i++){
		int x;
		scanf("%d",&x);
		v.push_back(x);
	}	
	sort(v.begin(),v.end(),greater<int>());
	for(it = v.begin();it<v.end();it++)
		printf("%d ",(*it));
	system("pause");
	return 0;
}