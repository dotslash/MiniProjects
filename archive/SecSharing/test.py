from revealSecret import *
from genSecret import *

print "enter number of users:"
user_cnt = int(raw_input())
secrets,primes = generateSecrets(user_cnt)
primes = primes[1:]
#primes.sort()
print "secrets:",secrets
print "primes:\n",primes

pred_primes = revealPrimes(secrets)
#pred_primes.sort()
print "predicted primes:\n",pred_primes
