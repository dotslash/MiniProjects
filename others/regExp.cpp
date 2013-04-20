#include <cstring>
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <climits>
#include <cmath>

#include <string>
#include <iostream>

#include <algorithm>
#include <set>
#include <queue>
#include <stack>
#include <map>
#include <vector>

using namespace std;

#define DEBUG false
#define MAXV 500010
#define LL long long
//for loops

#define rep(i,s,n) for(LL i=(s);i<(LL)(n);i++)
#define repr(i,s,n) for(LL i=(s);i>(LL)(n);i--)
#define snuke(c,itr) for(__typeof((c).begin()) itr=(c).begin();itr!=(c).end();itr++)

//vector
#define vl vector<LL>
#define vi vector<int>
#define pb push_back
//pair
#define pll pair<LL,LL> 
#define pii pair<int,int> 
#define fir first
#define sec second

#define SI set<int>
class RegExp{
 public:
   string regExp, input;
   int* preProc;
   int* nextOr;
   void transform(){
      	
   }
   void init(){
      transform()
      preProc = new int[regExp.length()];
      nextOr = new int[regExp.length()];
      fill(preProc,preProc+regExp.length(),0);
      stack<int> st;
      rep(i,0,regExp.length()){
         if(regExp[i]=='('){
            st.push(i);
         }
         else if(regExp[i]==')'){
            assert(!st.empty());
            int x = st.top(); st.pop();
            preProc[x] = i;
            preProc[i] = x;
         }
      }
      assert(st.empty());
      if(DEBUG){
         rep(i,0,regExp.length()){
            cout<<regExp[i]<<":"<<i<<":"<<preProc[i]<<" ";
         }
         cout<<"\n";
      }
      fill(nextOr,nextOr+regExp.length(),regExp.length()+1000);
      for(int i=regExp.length()-2;i>-1;i--){
         if(regExp[i+1]=='|'){
            nextOr[i] = i+1;
         }
         else nextOr[i] = nextOr[i+1];
      }
   }
   
   bool isSimple(char c){
      return (c=='.' || (c>='a' && c<='z') || (c>='A' && c<='Z') || (c>='0' && c<='9'));
   }
   SI Union(SI s1,SI s2){
      SI ret;
      snuke(s1,it) ret.insert(*it);
      snuke(s2,it) ret.insert(*it);
      return ret;
   }
   
   bool ok(int s,int e){
      return (regExp[s]=='(' && regExp[e]==')' && preProc[s]==e && preProc[e]==s);
   }
   int orSplit(int start,int end){
      int next = nextOr[start];
      return (next<end && ok(start,end) && ok(start+1,next-1) && ok(next+1,end-1))?next:-1;
   }
   SI Matches(int reS,int reE,int ind){      
      if(true || DEBUG) {
         //cout<<reS<<":"<<reE<<":"<<ind<<"\n";
         //int x; cin>>x; 
         cout<<regExp.substr(reS,1-reS+reE)<<endl;
         
      }
      //match single char by char until a bracket is found
      if(reS==regExp.size() || reS>reE){
          SI ret;
          ret.insert(ind);
          return ret;
      }
      bool something= false;
      while(reS<=reE && isSimple(regExp[reS])){
         if(ind>=input.length()) return SI(); //return empty set
         else if(regExp[reS]=='.' || regExp[reS]==input[ind]) {
            reS++;
            ind++;
            something= true;
         }
         else return SI(); //return empty set
      }
      if(something){
         return Matches(reS,reE,ind);
      }
      
      int s = orSplit(reS,reE);
      if( reE>=reS+5 && ok(reS,reE) && regExp[reE-1]=='*'){ //((P)*)
         cout<<"* found:"<<endl;
         SI ret;
         ret.insert(ind);
         int len=0;
         while(1){   
            SI t = Union(ret,ret);
            snuke(ret,it){
               SI tmp =  Matches(reS+1,reE-2,*it);
               t = Union(tmp,t);
            }
            ret = t;
            if(len==ret.size()) break;
            len = ret.size();
         }
         return ret;
      }
      else if(s!=-1){ //((P)|(P))
         cout<<"split:"<<s<<endl;
         SI s1 = Matches(reS+1,s-1,ind);
         SI s2 = Matches(s+1,reE-1,ind);
         return Union(s1,s2);
      }
      else if(ok(reS,reE)){  //(P)
         return Matches(reS+1,reE-1,ind);
      }
   }
};

int main(){
   
   while(1){
      RegExp re;
      cout<<"RE string\n";
      cin>>re.regExp;// = "((1)(.23)*)";
      cin>>re.input;
      re.init();                
      SI s = re.Matches(0,re.regExp.size()-1,0);
      cout<<"Results\n";
      snuke(s,it) cout<<re.input.substr(0,*it)<<endl;
   }
   return 0;
}
