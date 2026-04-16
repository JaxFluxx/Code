#include<bits/stdc++.h>
using namespace std;
const int N = 1e5;
struct book{
    char name[31];
    double price;
};
int main(){
    struct book books[10];
    int n, i, _max=0, _min = 0;
    scanf("%d",&n);
    cin.ignore(1021,'\n');
    for(i=0;i<n;i++){
        cin.getline(books[i].name,31);
        scanf("%lf",&books[i].price);
    }
    for(i=1;i<n;i++){
        if(books[i].price > books[_max].price)    _max = i;
        if(books[i].price < books[_min].price)    _min = i;
    }
    printf("%.2f, %s",books[_max].price,books[_max].name);
    printf("%.2f, %s",books[_min].price,books[_min].name);
    system("pause");
    return 0;
}