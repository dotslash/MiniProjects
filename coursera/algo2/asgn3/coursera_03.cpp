#include <iostream>
#include <algorithm>
#include <vector>
#include <map>
#include <cassert>

#define pii pair<int,int> 
#define val first 
#define wt second
using namespace std;

pii goods[1000];
int cnt;
map<pii,int> value;
//recursive knapsack
int knapsack(int rem,int start){
    if(rem<=0 || start>=cnt) return 0;
    map<pii,int>::iterator fnd = value.find(pii(rem,start));
    if(fnd!=value.end()){
        return value[pii(rem,start)];
    }
    
    int best=0;
    if(rem>=goods[start].wt){
        best = goods[start].val+ knapsack(rem-goods[start].wt,start+1);
    }
    best = max(best,knapsack(rem,start+1));
    value[pii(rem,start)]=best;
    return best;
}

int main (int argc, char const* argv[])
{
    int total;
    cin>>total>>cnt;
    for (int i = 0; i < cnt; i += 1){
        cin>>goods[i].val>>goods[i].wt;
    }
    
    cout<<knapsack(total,0)<<endl;
    return 0;
}
