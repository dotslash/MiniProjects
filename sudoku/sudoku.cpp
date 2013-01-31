# include <set>
# include <iostream>
# include <assert.h>
# include <cstdio>
# include <string>

using namespace std;
int grid[9][9];
void printSet(int num){
	for (int i = 1; i <= 9; i += 1)
	{
		if(num&(1<<i)){
			cout<<i<< " ";	
		}
	}
}
void printGrid(){
	for (int j = 0; j < 22; j += 1){
		if(j%7==0) cout<<"+";
		else cout<<"-";
	}
	cout<<"\n";
	for (int i = 0; i < 9; i += 1){
		cout<<"|";
		for (int j = 0; j < 9; j += 1)
		{
			cout<<grid[i][j]<<" ";
			if(j%3==2) cout<<"|";
		}
		cout<<"\n";
		if(i%3==2){
			for (int j = 0; j < 22; j += 1){
				if(j%7==0) cout<<"+";
				else cout<<"-";
			}
			cout<<"\n";
		}	
	}
}


int predict(int x,int y){
	if(grid[x][y]!=0) return 1<<grid[x][y];
	int result = 511*2;
	for (int i = 0; i < 9; i += 1){
		int rem = 1<<grid[i][y];
		if(rem & result) result-=rem;
		//cout<<grid[i][y]<<":";printSet(result);cout<<"\n";
	}
	//cout<<"\n";	
	for (int i = 0; i < 9; i += 1){
		int rem = 1<<grid[x][i];
		if(rem & result) result-=rem;
		//cout<<grid[x][i]<<":";printSet(result);cout<<"\n";
	}
	
	int xoff = x/3,yoff =y/3;
	//cout<<"\n";
	for (int i = 0; i < 9; i += 1)
	{
		int rem  = grid[xoff*3+i/3][yoff*3+i%3];
		rem = 1<<rem;
		if(rem & result) result-=rem;
		//cout<<grid[xoff*3+i/3][i%3+yoff*3]<<":";printSet(result);cout<<"\n";
	}
	assert(result>=0);
	return result;
}

bool solve(int pres){
	if(pres>=81) return true;
	int x=pres%9,y=pres/9;
	int res = predict(x,y);
	int init = grid[x][y];

	for (int i = 1; i <= 9; i += 1)
	{
		if(res & (1<<i)){
			grid[x][y]=i;
			if(solve(pres+1)) return true;
			grid[x][y]=init;
		}
	}
	return false;
}

int main(){
	int tc; cin>>tc;
	for(int t=1;t<=tc;t++){
		for (int i = 0; i < 9; i += 1){
			for (int j = 0; j < 9; j += 1){
				cin>>grid[i][j];
			}
		}
		if(solve(0)){
			cout<<"testCase :"<<tc<<"\n";
			printGrid();
		}
		else{
			cout<<"No Solution\n";
		}	
	}
	return 0;
}
