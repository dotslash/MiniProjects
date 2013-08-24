#include <iostream>
#include <algorithm>
using namespace std;
#define pii pair<long long,long long>

int parent[1000000];
void init(){
    for (int i = 0; i < 1000000; i += 1)
    {
        parent[i] = i;
    }
}
int root(int a){
    while(parent[a]!=a){
        parent[a] = parent[parent[a]];
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
    int m,n; cin>>n>>m;
    init();
    edge edges[m];
    for (int i = 0; i < m; i += 1)
    {
        int a,b,c;
        cin>>a>>b>>c;
        edges[i] = edge(a,b,c);
    }
    sort(edges,edges+m,cmp);
    long long total=0;
    for (int i = 0; i < m; i += 1)
    {
        edge e = edges[i];
        if(!find(e.start,e.end)){
            Union(e.start,e.end);
            total+=e.weight;
        }
    }
    
    cout<<total<<"\n"   ;
    return 0;
}
//-3612829
