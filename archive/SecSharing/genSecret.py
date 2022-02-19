from random import randint

'''
generate n distinct primes between prime[0] and prime[up_limit]
up_limit <= 1000000
n users => 2^n primes : upto 15 users
'''
def genPrimes(count,up_limit):
    prev = set()
    for i in xrange(count):
        x = randint(1,up_limit)
        while(prev.__contains__(x)):
            x = randint(1,up_limit)
        prev.add(x)

    bm = [1]*1300000
    bm[2]=1
    primes = []
    for i in xrange(2,1300000):
        if(bm[i]==0): continue
        primes.append(i)
        for j in xrange(2*i,1300000,i):
           bm[j]=0

    prime_lst = []
    for num in prev: prime_lst.append(primes[num])
    return prime_lst


def Bfunc(number,k):
    if( (number & (1<<k)) ==0 ): return False
    return True


'''
input:user_id  : id of the user 
      prime_lst: list of primes
      user_cnt : total number of users
      
user_cnt>=user_id>=1
length of prime_lst >= 2^(user_cnt)

'''
def Secret(user_id,prime_lst,user_cnt):
    retval= 1
    string = ""
    for i in xrange(1,1<<user_cnt):
        if(Bfunc(i,user_cnt-user_id)):
            retval*=prime_lst[i]
            string+=(str(i) +" ")
    return retval

def generateSecrets(user_cnt):
    prime_lst = genPrimes(1<<user_cnt,10000)
    secrets = []
    for i in xrange(user_cnt):
        secrets.append(Secret(i+1,prime_lst,user_cnt))
    return secrets,prime_lst
