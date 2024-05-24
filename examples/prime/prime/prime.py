import sys

MAXPRIMES = 50

def prime(n):
    primes = [0] * MAXPRIMES
    primes[0] = 2
    num_primes = 1
    cur_prime = 2

    while num_primes < n:
        # cur_prime += 1
        cur_prime += num_primes
        is_prime = True

        for i in range(num_primes):
            if cur_prime % primes[i] == 0:
                is_prime = False
                break

        if is_prime:
            primes[num_primes] = cur_prime
            num_primes += 1

    return primes[:num_primes]
