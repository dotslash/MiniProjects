#include <iostream>
#include <algorithm>
#include<memory.h>
using namespace std;
#define MAXE 2000002
#define MAXV 2000002


struct edge{int e, nxt;};
int V, E;
edge e[MAXE], er[MAXE];
int sp[MAXV], spr[MAXV];
int group_cnt, group_num[MAXV];
bool v[MAXV];
int stk[MAXV];

void fill_forward(int x)
{
	int i;
	v[x]=true;
	for(i=sp[x];i;i=e[i].nxt) if(!v[e[i].e]) fill_forward(e[i].e);
	stk[++stk[0]]=x;
}
void fill_backward(int x)
{
	int i;
	v[x]=false;
	group_num[x]=group_cnt;
	for(i=spr[x];i;i=er[i].nxt) 
		if(v[er[i].e]) 
			fill_backward(er[i].e);
}
void add_edge(int v1, int v2) //add edge v1->v2
{
	//cout<<v1<<v2<<"\n";
	e [++E].e=v2; e [E].nxt=sp [v1]; sp [v1]=E;
	er[E].e=v1; er[E].nxt=spr[v2]; spr[v2]=E;
}
void SCC()
{
	int i;
	stk[0]=0;
	memset(v, false, sizeof(v));
	for(i=1;i<=V;i++) if(!v[i]) fill_forward(i);
	group_cnt=0;
	for(i=stk[0];i>=1;i--)
	if(v[stk[i]])
	{
		group_cnt++; 
		fill_backward(stk[i]);
	}
}

int n;
int negation(int num){
	if(num>n) return num-n;
	else return num+n;
}

int main (int argc, char const* argv[])
{
 	cin>>n;
 	
 	V = 2*n+1;
 	E = 2*n;
	//1..n: +ve
	//n+1....2n : -ve
	for (int i = 0; i < n; i += 1)
	{
		int a,b; cin>>a>>b;
		if(a<0) a = (n-a);
		if(b<0) b = (n-b);
		
		add_edge(negation(b),a);
		add_edge(negation(a),b);		
	}
	SCC();
	for (int i = 1; i <= n; i += 1)
	{
		if(group_num[i]==group_num[i+n]) {
			cout<<0;return 0;
		}
		//cout<<i<<":"<<group_num[i]<<" "<<group_num[n+i]<<"\n";
	}
	cout<<1;
}

