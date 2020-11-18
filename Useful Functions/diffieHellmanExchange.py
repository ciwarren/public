#Sources:
	#https://www.geeksforgeeks.org/primitive-root-of-a-prime-number-n-modulo-n/
	#https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange
	#https://stackoverflow.com/questions/15285534/isprime-function-for-python-language
	#https://asecuritysite.com/encryption/diffie_py

# I do not pretend to be smart enough to have been able to come up with some of this math, above are my sources :)
# Couldn't find another script that would also compute P and G, so I pulled some stuff together. 
# Please feel free to use this wherever you find useful!


import random
import hashlib
from math import sqrt

def findPrimefactors(s, n) : 
  
    # Print the number of 2s that divide n  
    while (n % 2 == 0) : 
        s.add(2)  
        n = n // 2
  
    # n must be odd at this po. So we can   
    # skip one element (Note i = i +2)  
    for i in range(3, int(sqrt(n)), 2): 
          
        # While i divides n, print i and divide n  
        while (n % i == 0) : 
  
            s.add(i)  
            n = n // i  
          
    # This condition is to handle the case  
    # when n is a prime number greater than 2  
    if (n > 2) : 
        s.add(n)  
  
# Function to find smallest primitive  
# root of n  

def findPrimitive( n) : 
    s = set()  

    # Check if n is prime or not  
    if (isPrime(n) == False):  
        return -1
  
    # Find value of Euler Totient function  
    # of n. Since n is a prime number, the  
    # value of Euler Totient function is n-1  
    # as there are n-1 relatively prime numbers. 
    phi = n - 1
  
    # Find prime factors of phi and store in a set  
    findPrimefactors(s, phi)  
  
    # Check for every number from 2 to phi  
    for r in range(2, phi + 1):  
  
        # Iterate through all prime factors of phi.  
        # and check if we found a power with value 1  
        flag = False
        for it in s:  
  
            # Check if r^((phi)/primefactors) 
            # mod n is 1 or not  
            if (pow(r, phi // it, n) == 1):  
  
                flag = True
                break
              
        # If there was no power with value 1.  
        if (flag == False): 
            return r  
  
    # If no primitive root found  
    return -1

def isPrime(n):
	if n == 2 or n == 3: return True
	if n < 2 or n%2 == 0: return False
	if n < 9: return True
	if n%3 == 0: return False
	r = int(n**0.5)
	f = 5
	while f <= r:
		if n%f == 0: return False
		if n%(f+2) == 0: return False
		f +=6
	return True


def genPrime(min, max):
	primes = [i for i in range(min,max) if isPrime(i)]
	p = random.choice(primes)
	return p


def diffieHellman():
	min = 100000
	max = 999999
	p = genPrime(min, max)
	g = findPrimitive(p)
	message =  f'{p},{g}'

	a = random.randint(0, 10000)
	A = (g**a) % p 

	b = random.randint(10001, 20001)
	B = (g**b) % p

	sB = (B**a) % p

	sA = (A**b) % p

	secretA = hashlib.sha256(str(sA).encode()).hexdigest()

	secretB = hashlib.sha256(str(sB).encode()).hexdigest()

	print(f'P: {p}, G: {g}')

	print (f'a: {a}, A: {A}')
	print (f'b: {b}, B: {B}')

	print (f'sA: {sA}, sB: {sB}')

	print(f'Secret A: {secretA}')
	print(f'Secret B: {secretB}')

diffieHellman()
