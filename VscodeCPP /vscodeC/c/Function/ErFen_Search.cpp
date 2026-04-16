#include <bits/stdc++.h>
using namespace std;

int main(){
    int N;
    scanf("%d",&N);

    map<string,string> m;
    while(N--){
        string key,value;
        cin >> key >> value;
        m.insert(pair<string,string>(key,value));
    }

    int M;
    vector<string> v;
    scanf("%d",&M);
    while(M--){
        string id,_id;  //_id��id����һ��
        cin >> id;
        
        //��map���ҵ����id����һ��
        map<string,string>::iterator it;
        it = m.find(id);
        if(it != m.end()){
            _id = it->second;
        }
        else{  //����Ҳ���������value��key
            for(it = m.begin(); it != m.end(); it++)
                if(it->second == id){
                    _id = it->first;
                    break;
                }
        }

        //��vector�м��id����һ���Ƿ���ڣ������ڲ�¼��
            //count���ڷ���1�������ڷ���0
        vector<string>::iterator _it,_it1;
        if(count(v.begin(),v.end(),_id)){  //����ҵ�����һ�룬��v��ɾ�����Ԫ��
            for(_it = v.begin();_it != v.end();){
                if(*_it == id || *_it == _id) { // ͬʱɾ��id����֮��Ե�Ԫ��
                    _it = v.erase(_it);  // ע��������Ҫ���»�ȡ������
                } else {
                    ++_it;
                }
            }
        } else {
            v.push_back(id);  // ��������ڣ�ֱ�����ӵ�vector��
        }
    }
    sort(v.begin(),v.end());

    vector<string>::iterator _it;
    printf("%d\n",v.size());
    for(_it = v.begin();_it != v.end() - 1; _it ++){
        cout << *(_it) << " ";
    }
    cout << *(_it);

    system("pause");
    return 0;
}
