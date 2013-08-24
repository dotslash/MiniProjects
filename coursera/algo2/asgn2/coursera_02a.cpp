#include <iostream>
#include <algorithm>
#include <vector>
#include <map>
#include <cassert>



using namespace std;
#define pii pair<long long,long long>

//Union Find
int parent[1000000];
void init(){
    for (int i = 0; i < 1000000; i += 1){
        parent[i] = i;
    }
}
int root(int a){
    while(parent[a]!=a){
        //parent[a] = parent[parent[a]];
        a = parent[a];
    }
    return a;
}
void Union(int a,int b){
    parent[root(a)] = root(b);
}
bool find(int a,int b){
    return root(a)==root(b);
}

//edge class
class edge{
 public:
    int start,end,weight;
    edge(int a,int b,int c){
        start = a;
        end = b;
        weight = c;
    }
    edge(){}
};

bool cmp(edge e1,edge e2){
    return e1.weight < e2.weight;
}

int main (int argc, char const* argv[])
{
    //inputs
    int n,m; cin>>n; m = n*(n-1)/2;
    init();
    edge edges[m];
    for (int i = 0; i < m; i += 1)
    {
        int a,b,c;
        cin>>a>>b>>c;
        edges[i] = edge(a,b,c);
    }
    
    //Single Link clustering for 4 clusters
    sort(edges,edges+m,cmp);
    int count=n;
    int answer=0;
    for (int i = 0; i < m; i += 1)
    {
        edge e = edges[i];
        if(!find(e.start,e.end)){
            if(count==4){
                answer = e.weight;
                break;
            }
            Union(e.start,e.end);
            cout<<root(e.start)<<"\n";
            count--;
            
        }
    }
    cout<<answer<<"\n";
    return 0;
}
//106
