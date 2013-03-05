#for pypy use wordRuggelnumpypy.py
import datetime
import numpy as npy
print "ni"
trie = npy.zeros((3000000,26,2),dtype=npy.int32)
next=2
neigh = []
visited = [False]*16
board = ""
pres = []

def chr2num(c):
	x = ord(c)-ord('a')
	if(x<0): return ord(c)-ord('A')
	return x
def addWord(string):	
	pres=1
	prev=-1
	for c in string:	
		if ((c<='z' and c>='a') or (c<='z' and c>='a')): continue
		else : return
	global next
	for c in string:
		np = trie[pres][chr2num(c)]
		#print pres,trie[pres]
		if(np[1]==0):
			trie[pres][chr2num(c)][0],trie[pres][chr2num(c)][1] = np[0],next
			next+=1
		prev = pres
		pres = trie[pres][chr2num(c)][1]
	c=string[-1]
	x=chr2num(c)
	
	taildata = trie[prev][chr2num(c)]	
	trie[prev][chr2num(c)][1],trie[prev][chr2num(c)][1] = (1,taildata[1])

def exists(string):
	pres=1
	prev=-1
	for c in string:
		np = trie[pres][chr2num(c)]
		#print pres,trie[pres]
		if(np[1]==0	): return "--"
		prev = pres
		pres = np[1]
	return trie[prev][chr2num(string[-1])][0]

def ok(i,j):
	return 0<=i and 0<=j and i<4 and j<4
def num(i,j):
	return i*4+j

def printPath(): 
	string = ""
	path=""
	for p in pres:
		string+=board[p[1]]
		path+="("+str(p[1]/4)+","+str(p[1]%4)+") "
	print string+":"+path
	

def recurse(start):
	trieNode = pres[-1][0]
	char = chr2num(board[pres[-1][1]])
	if(trie[trieNode][char][0]==1): printPath()
	if(trie[trieNode][char][1]==0): return
	if(visited[start]): return
	visited[start]=True
	
	for n in neigh[start]:
		pres.append((trie[trieNode][char][1],n))
		recurse(n)
		pres.pop()
	visited[start]= False



print "start"
words = []
print datetime.datetime.now()
inp = open('all','r')
for line in inp:
	word = line.strip()
	if(len(word)<3):continue
	#words.append(word)
	addWord(word)

print datetime.datetime.now()
print "trie built"

board = raw_input()+raw_input()+raw_input()+raw_input()

for i in xrange(16):
	x,y = i/4,i%4
	lst = []
	for xd in xrange(-1,2):
		for yd in xrange(-1,2):
			if(xd==0 and yd==0): continue
			if(ok(x+xd,y+yd)): lst.append(num(x+xd,y+yd))
	neigh.append(lst)

for i in xrange(16):
	pres = [(1,i)]
	recurse(i)
