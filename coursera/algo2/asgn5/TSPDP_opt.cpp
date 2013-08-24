#include <iostream>
#include <algorithm>
#include <math.h>
#include <stdio.h>
#include <assert.h>
using namespace std;

#define pii pair<int,int> 
#define INF 100000000

int subsets[(1<<24) + 10000];
float dist[25][25];
float co_ord[25][2];

//dp[i][j][k] => i:present/prev j:subsetIndex among subsets of same size k:end point
float dp[2][5500000][25]; 
//ssOfSzK[i] => start and end index of subsets of size i
pii ssOfSzK[26];
//Index of subset among subsets of same size
int indInSz[(1<<25)];

int nodes;

int NumberOfSetBits(int i)
{
    i = i - ((i >> 1) & 0x55555555);
    i = (i & 0x33333333) + ((i >> 2) & 0x33333333);
    return (((i + (i >> 4)) & 0x0F0F0F0F) * 0x01010101) >> 24;
}

//compare function to sort based on number of set bits
bool cmp(int i1,int i2){
	return NumberOfSetBits(i1)<NumberOfSetBits(i2);
}

void generateSS(){
	
	int basic = (1<<(nodes-1));
	int pow2 = nodes;
	
	//all subsets that contain 0
	for(int i=0;i< basic;i++){
		subsets[i] = 2*i+1;
	}
	
	//all monotonix sets
	for (int i = 0; i < pow2; i += 1){
		subsets[basic + i] = 1<<(i+1);
	}		
	stable_sort(subsets,subsets+basic+pow2,cmp);
	
	//setting up ssOfSzK and indInSz
	int prev=0;
	for (int i = 0; i < (basic+pow2); i += 1)
	{
		int pres = NumberOfSetBits(subsets[i]);
	
		if(prev!=pres){
			ssOfSzK[pres].first = i;
		}
	
		indInSz[subsets[i]] = i-ssOfSzK[pres].first;
		ssOfSzK[pres].second = i;
		prev=pres;
	}
	
}


void solve(){
	int pres=1,past=0;
	
	//init: not necessary
	for (int i = 0; i < 5500000; i += 1){
		dp[0][0][i]=0;
	}
	
	for(int sz=2;sz<=nodes;sz++){
		cout<<sz<<" is the pres size\n";
		for(int ind=ssOfSzK[sz].first;ind<=ssOfSzK[sz].second;ind++){
			//best among the paths starting at 0 and ending at i = best (best among paths starting at 0 ending at j) + ij
			int num = subsets[ind];
			for(int i=1;i<nodes;i++){
				if(( (1<<i)&num) ==0){
					continue;
				}
				int powi2 = 1<<i;
				float value = INF;
				for(int j=0;j<nodes;j++){
					if(((1<<j)&num) ==0 || i==j ||(j==0 && sz!=2)){
						continue;
					}
					int indOfSub = indInSz[num-powi2];
					value = min(dp[past][indOfSub][j] + dist[i][j], value);
				}
				dp[pres][ind -ssOfSzK[sz].first ][i] = value;
			}
		}
		pres = 1-pres; 
		past = 1-past;
	}
	
	float soln = INF;
	cout<<"done\n";
	//best tour : best (dp(Universal Set,j)+0j)
	for(int i=1;i<nodes;i++){
		soln = min(dp[past][0][i]+dist[i][0],soln);
	}
	printf("%.10f\n",soln);
}

int main (int argc, char const* argv[])
{	
	cin>>nodes;
	
	for(int i=0;i<nodes;i++){
		cin>>co_ord[i][0]>>co_ord[i][1];
	}
	
	for(int i=0;i<nodes;i++){
		for(int j=0;j<nodes;j++){
			float xd = co_ord[j][0]-co_ord[i][0];
			float yd = co_ord[j][1]-co_ord[i][1];
			dist[i][j] = sqrt( xd*xd + yd*yd );
		}
	}
	generateSS();
	solve();
	return 0;
}
