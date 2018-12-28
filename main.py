from mpmath import *
from itertools import groupby
from collections import Counter, OrderedDict


class OrderedCounter(Counter, OrderedDict):
    'Counter that remembers the order elements are first seen'

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, OrderedDict(self))

    def __reduce__(self):
        return self.__class__, (OrderedDict(self),)


mp.dps = 1000


def prime_factorization(n):
    '''Returns an ordered dictionary with keys the prime factors and values their exponent'''

    n = mpf(n)
    prime_factors = []
    prime = mpf(2)

    while fmod(n, 2) == 0:
        prime_factors.append(prime)
        n = fdiv(n, prime)

    prime = mpf(3)
    while fmul(prime, prime) <= n:
        if n % prime == 0:
            prime_factors.append(prime)
            n = fdiv(n, prime)
        else:
            prime += 2

    if n != 1:
        prime_factors.append(n)

    factorization = OrderedCounter(prime_factors)

    return factorization


def primes_up_to(p):
    '''Generates prime numbers up to p (sieve of Eratosthenes)'''
    p = int(float(nstr(p)))

    prime_list = [2]
    p_half = p**0.5
    flags = [True, True] + [False] * (p-2)

    # Step through all the odd numbers
    for i in range(3, p, 2):
        if flags[i]:
            continue
        prime_list.append(i)
        # Exclude further multiples of the current prime number
        if i <= p_half:
            for j in range(i*i, p, i<<1):
                flags[j] = True

    return prime_list


def is_instruction(instruction):
    '''Check for a valid instruction (True/False)'''
    prime_factors = prime_factorization(instruction)
    possible_primes = [2, 3, 5, 7]

    if [x for x in prime_factors.keys() if x not in possible_primes]:
        return False  # wrong instruction (primes not in possibleprimes)

    if 2 not in prime_factors.keys():
        return False  # 2 must always be a factor for any instruction

    if 3 in prime_factors.keys():
        if prime_factors.get(3) != 1:
            return False  # wrong exponent (0 for addition, 1 for substraction)

    return True


def u(n):
    """
    To see if n encodes a program. We have to check if:
    1- n = 2^i(1)*3^i(2)*...*p(r-1)^i(r)
    2- Each i(t) = 2^j*5^k OR i(t) = 2^j*3*5^k*7^l

    This translate into checking for the following:
    1- A instruction can only have 2, 3, 5 and 7 as prime factors (done)
    2- A instruction must have 2 as prime factor (done)
    3- A 3 in a instruction must be either to the power 0 or 1 (done)
    4- A instruction must not reference a non existent state (todo)
    5- There must be a valid instruction for each prime up to the biggest one (done through checking every prime is there up to the biggest one and there is a valid instruction for each)
    """
    prime_descomposition = prime_factorization(n)
    prime_factors = list(prime_descomposition.keys())
    primes_to_look = primes_up_to(prime_factors[-1])

    for p in primes_to_look:
        if p not in prime_factors:
            return 'Prime '+nstr(p, 100)+' is not a factor (biggest prime: '+nstr(prime_factors[-1], 100)+')'  # This can go away if condition 5 is not needed

        exponent = prime_descomposition.get(p)

        if not is_instruction(exponent):
            return 'Instruction '+nstr(p, 100)+' unclear'

    return

# primes = prime_factorization(fmul(power(2, 300), power(3, 10)))
# print(primes, list(primes.keys()), primes.values())
# print(u(fmul(power(2, 300), power(3, 10))))
# print(primes_up_to(mpf('100')))
