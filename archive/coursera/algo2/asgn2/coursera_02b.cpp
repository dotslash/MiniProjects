#include <iostream>
#include <algorithm>
#include <vector>
#include <map>
#include <cassert>

using namespace std;
//convert binary string to number : order does not matter for this problem
int str2num(string str){
    int pres=1,res=0;
    for (int i = 0; i < str.length(); i += 1){
        if(str[i]=='1'){
            res+=pres;
        }
        pres=pres*2;
    }
    return res;
}
//flip bit in position pos in number
int flip(int number,int pos){
    if(number&(1<<pos)){
        return number-=(1<<pos);
    }
    else return number+=(1<<pos);
}


vector<vector<int> > subsets;
//add subsets of  set {0...n-1} having size k  to subsets
//init values : start=0,pres=empty vector
void subsets_size_k(int n,int k,int start,vector<int> pres){

    if(start+k-pres.size() > n)return;
    if(pres.size()==k){
        subsets.push_back(pres);
        return;
    }
    vector<int> tmp = vector<int>(pres);
    tmp.push_back(start);
    subsets_size_k(n,k,start+1,pres);
    subsets_size_k(n,k,start+1,tmp);

}

//Union Find
int parent[1000000];
void init(){
    for (int i = 0; i < 1000000; i += 1){
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



int main (int argc, char const* argv[])
{
    //generate all subsets of size 1 and 2 of the set {0...23} amd add them to subsets
    subsets_size_k(24,2,0,vector<int>());
    subsets_size_k(24,1,0,vector<int>());
    cout<<subsets.size()<<"\n";
    
    //inputs
    string str;
    int tc,tmp; cin>>tc>>tmp;
    map<int,int> s;
    int count=0;
    for (int i = 0; i < tc; i += 1){
        cin>>str;
        int num=str2num(str);
        //remove duplicates
        if(s.find(num)!=s.end()) continue;
        s[num]=count++;
    }
    
    init();
    cout<<s.size()<<"\n";
    //iterate through all the items in set and 
    //union the valid neighbours obtained by flipping the bits corresponding to each subset
    for (map<int,int>::iterator it=s.begin(); it != s.end(); it++){
        for (int i = 0; i < subsets.size(); i += 1){
            int neigh = it->first;
            
            for (int j = 0; j < subsets[i].size(); j += 1){
                neigh = flip(neigh,subsets[i][j]);
            }
            if(s.find(neigh)!=s.end()){
                Union(s[neigh],it->second);     
            }
        }
    }
    int cnt=0;
    //find the number of clusters
    for (int i = 0; i < count; i += 1){
        if(parent[i]==i) cnt++;
    }
    cout<<cnt<<"\n";
    return 0;
}
