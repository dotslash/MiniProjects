def Bfunc(number,k):
    if( (number & (1<<k)) ==0 ): return False
    return True

def gcd2(num1,num2):
    n1 = max(num1,num2)
    n2 = min(num1,num2)
    while n2!=0:
        n = n2
        n2 = n1%n2
        n1 = n
    return n1
    
def gcdn(num_lst):
    if(len(num_lst)==0): return 0
    if(len(num_lst)==1): return num_lst[0]
    start = gcd2(num_lst[0],num_lst[1])
    for num in num_lst[2:]:
        start = gcd2(num,start)
    return start

def revealPrimes(secrets):
    num_users = len(secrets)
    
    tmp = []
    for i in xrange(1,1<<num_users):
        tmp.append((bin(i).count("1"),i))
    tmp.sort()
    tmp.reverse()
    
    primes = []
    for numb in tmp:
        set_id = numb[1]
        numbers_in_set = []
        for i in xrange(1,num_users+1):
            if(Bfunc(set_id,num_users-i)):
                numbers_in_set.append(i)
        #print set_id,numbers_in_set
        tmp_lst = []
        for num in numbers_in_set:
            tmp_lst.append(secrets[num-1])
        gcd_nums = gcdn(tmp_lst)
        primes.append(gcd_nums)
        for num in numbers_in_set:
            secrets[num-1] = secrets[num-1]/gcd_nums
    return primes
