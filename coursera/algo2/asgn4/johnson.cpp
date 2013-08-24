#include <iostream>
#include <algorithm>
#include <vector>
#include <queue>
#include <limits>
#include <cassert>
using namespace std;


#define int_min numeric_limits<int>::min()
#define int_max numeric_limits<int>::max()
#define pii pair<int,int> 


vector<vector<pii> > AdjList;

//pii AdjList_arr[50000]; //all edges in array
//pii AdjList_node_data[1002]; //start and end
int ShortestPaths[1002][1002],DummyPathLengths[1002];
int nodes,best;

void init(){
	
	best = int_max; //best is the answer
	int pres_cnt=0;
	/*
	for (int i = 0; i < AdjList.size(); i += 1){
		int start = pres_cnt;
		for (int j = 0; j < AdjList[i].size(); j += 1){
			AdjList_arr[pres_cnt++]=AdjList[i][j];
		}
		int end = pres_cnt; //start=end => no edges from i
		AdjList_node_data[i]=pii(start,end);
	}
	*/
	
	
	fill(ShortestPaths[0], ShortestPaths[1001]+1001 ,int_max);
	
	//init DummyPathLengths to zero because there is an edge 
	//from each dummy node to each other node with weight 0
	//Actually any positive value shoud be fine
	fill_n(DummyPathLengths,1002,0);
}

//modifies edge weights

int modEdge(int s,int ind){
	int ret = AdjList[s][ind].second + DummyPathLengths[s] - DummyPathLengths[AdjList[s][ind].first];
	assert(ret>=0);
	return ret;
}
/*
int modEdge_arr(int s,int ind){
	int ret = AdjList_arr[ind].second + DummyPathLengths[s] - DummyPathLengths[AdjList_arr[ind].first];
	assert(ret>=0);
	return ret;
}
*/

void Dijkstra(int source){
	priority_queue<pii,vector<pii>, greater<pii> > pq;
	pq.push(pii(0,source));
	
	while(!pq.empty()){
		pii pres = pq.top(); pq.pop();
		int pres_node = pres.second,pres_dist = pres.first;
		
		/*
		if(pres_dist >= ShortestPaths[source][pres_node]){
			continue;
		}	
		*/
		
		ShortestPaths[source][pres_node] = pres_dist;
		if(source!=pres_node)best = min(best,pres_dist-DummyPathLengths[source]+DummyPathLengths[pres_node]);
		
		for (int i = 0; i <AdjList[pres_node].size(); i += 1){
			int iter_node = AdjList[pres_node][i].first;
			int iter_dist = pres_dist+ modEdge(pres_node,i);
			if( iter_dist < ShortestPaths[source][iter_node] ){
				pq.push(pii(iter_dist,iter_node));
			}
		}
		/*
		pii	node_data = AdjList_node_data[pres_node];
		for (int i = node_data.first; i < node_data.second; i += 1)
		{
			pq.push(pii(pres_dist+ modEdge_arr(pres_node,i),AdjList_arr[i].first));
		}
		*/
		
	}	
	//cout<<source<<"\n";
}

void Belman_Ford(int source){
	//finding shortest path lengths from source 
	for (int i = 0; i<nodes ; i += 1){
		for (int j = 0; j <= nodes; j += 1){
			for (int k = 0; k < AdjList[j].size(); k += 1){
				DummyPathLengths[AdjList[j][k].first] = min(DummyPathLengths[AdjList[j][k].first],
																		  DummyPathLengths[j]+AdjList[j][k].second);				
			}
		}
	}
	
	//check for negative cycles
	for (int j = 0; j <= nodes; j += 1){
		for (int k = 0; k < AdjList[j].size(); k += 1){
			int a = DummyPathLengths[AdjList[j][k].first],b = DummyPathLengths[j]+AdjList[j][k].second;
			assert(a<=b); 
			
		}
	}	
}


void input(){
	int edges; cin>>nodes>>edges;
	AdjList = vector<vector<pii> >(nodes+1);
	for (int i = 0; i < edges; i += 1){
		int a,b,c; cin>>a>>b>>c;
		AdjList[a].push_back(pii(b,c));
	}
}

int main(){
	input();
	init();
	//Belman_Ford with dummy node : fills DummyPathLengths with appropriate values
	Belman_Ford(0);
	for (int i = 1; i <= nodes; i += 1){
		//Dijkstra with each node as source
		Dijkstra(i);
	}
	//print the best path length
	cout<<best<<"\n";
	return 0;
}
