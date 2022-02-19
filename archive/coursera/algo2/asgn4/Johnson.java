import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.PriorityQueue;
import java.util.StringTokenizer;

class pii{
	public pii(int b, int c) {
		first = b;
		second = c;
	}
	public pii(){};
	public int first,second;
}

class PairComparator implements Comparator<pii>
{
    @Override
    public int compare(pii x, pii y)
    {
        // Assume neither string is null. Real code should
        // probably be more robust
        if (x.first < y.first)
        {
            return -1;
        }
        if (x.first > y.first)
        {
            return 1;
        }
        return 0;
    }
}

public class Johnson {
	
	public static void solve(String[] args) throws IOException {
		new Johnson().solve();
	}
	
	void solve() throws IOException{
		input();
		init();
		//Belman_Ford with dummy node : fills DummyPathLengths with appropriate values
		Belman_Ford(0);
		for (int i = 1; i <= nodes; i += 1){
			//Dijkstra with each node as source
			Dijkstra(i);
		}
		//print the best path length
		System.out.println(best);
		return;
	}

	ArrayList<ArrayList<pii> > AdjList;
	
	private int nodes,best;
	final int int_max = Integer.MAX_VALUE,int_min=Integer.MIN_VALUE;; 
	
	private int[] DummyPathLengths = new int[1002];
	private int[][] ShortestPaths = new int[1002][1002];
	
	public static void main(String [] a) throws IOException{
		new Johnson().solve();
	}
	
	void init(){
		
		best = int_max; //best is the answer
		
		for(int[] subarray : ShortestPaths) {
	        Arrays.fill(subarray, int_max);
	    }
		
		//init DummyPathLengths to zero because there is an edge 
		//from each dummy node to each other node with weight 0
		//Actually any positive value shoud be fine
		Arrays.fill(DummyPathLengths,0);
	}
	
	//modifies edge weights
	int modEdge(int s,int ind){
		int ret = AdjList.get(s).get(ind).second + DummyPathLengths[s] - DummyPathLengths[AdjList.get(s).get(ind).first];
		assert(ret>=0);
		return ret;
	}
	
	
	void Dijkstra(int source){
		Comparator<pii> cmp = new PairComparator();
		PriorityQueue<pii>  pq = new PriorityQueue<pii>(10,cmp);
		pq.add(new pii(0,source));
		
		while(!pq.isEmpty()){
			pii pres = pq.poll();
			int pres_node = pres.second,pres_dist = pres.first;
			
			if(pres_dist >= ShortestPaths[source][pres_node]){
				continue;
			}	
			
			ShortestPaths[source][pres_node] = pres_dist;
			if(source!=pres_node)best = Math.min(best,pres_dist-DummyPathLengths[source]+DummyPathLengths[pres_node]);
			for (int i = 0; i <AdjList.get(pres_node).size(); i += 1){
				pq.add(new pii(pres_dist+ modEdge(pres_node,i),AdjList.get(pres_node).get(i).first));
			}
		}
		//System.out.println("Dijkstra " +source + " done");
	}
	
	void Belman_Ford(int source){
		//finding shortest path lengths from source 
		for (int i = 0; i<nodes ; i += 1){
			for (int j = 0; j <= nodes; j += 1){
				for (int k = 0; k < AdjList.get(j).size(); k += 1){
					DummyPathLengths[AdjList.get(j).get(k).first] = Math.min(DummyPathLengths[AdjList.get(j).get(k).first],
																			  DummyPathLengths[j]+AdjList.get(j).get(k).second);				
				}
			}
		}
		
		//check for negative cycles
		for (int j = 0; j <= nodes; j += 1){
			for (int k = 0; k < AdjList.get(j).size(); k += 1){
				int a = DummyPathLengths[AdjList.get(j).get(k).first],b = DummyPathLengths[j]+AdjList.get(j).get(k).second;
				assert(a<=b); 
				
			}
		}	
		//System.out.println("BF done");
	}
	
	BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
	StringTokenizer tokenizer = null;


	int ni() throws IOException{
		return Integer.parseInt(ns());
	}

	long nl() throws IOException{
		return Long.parseLong(ns());
	}

	double nd() throws IOException{
		return Double.parseDouble(ns());
	}

	String ns() throws IOException{
		while (tokenizer == null || !tokenizer.hasMoreTokens())
			tokenizer = new StringTokenizer(br.readLine());
		return tokenizer.nextToken();
	}

	String nline() throws IOException{
		tokenizer = null;
		return br.readLine();
	}

	
	void input() throws IOException{
		int edges; 
		
		nodes=ni();
		edges=ni();
		int a,b,c; 
		AdjList = new ArrayList<ArrayList<pii>>(nodes+1);
		for(int i=0;i<=nodes;i++){
			AdjList.add(new ArrayList<pii>());
		}
		for (int i = 0; i < edges; i += 1){
			a=ni();b=ni();c=ni();			
			ArrayList<pii> tmp = AdjList.get(a); 
			tmp.add(new pii(b,c));
			AdjList.set(a,tmp);
		}
		//System.out.println("input done");
	}
	
}