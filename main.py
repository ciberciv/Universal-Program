from mpmath import *
from collections import Counter, OrderedDict


class OrderedCounter(Counter, OrderedDict):
    """Counter that remembers the order elements are first seen"""

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, OrderedDict(self))

    def __reduce__(self):
        return self.__class__, (OrderedDict(self),)


mp.dps = 1000


def prime_factorization(n):
    """Returns an ordered dictionary with keys the prime factors and values their exponent"""

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
    """Generates prime numbers up to p (sieve of Eratosthenes)"""
    p = int(float(nstr(p)))

    prime_list = [2]
    p_half = p**0.5
    flags = [True, True] + [False] * (p-1)

    # Just checks odd numbers
    for i in range(3, p+1, 2):
        if flags[i]:
            continue
        prime_list.append(i)
        # Excludes multiples of the prime
        if i <= p_half:
            for j in range(i*i, p, i << 1):
                flags[j] = True

    return prime_list


def is_instruction(instruction):
    """Check for a valid instruction.
    Returns false if it is not a valid instruction, a list with the referenced
    states if it is"""
    prime_factors = prime_factorization(instruction)
    possible_primes = [2, 3, 5, 7]
    referenced_states = []

    if [x for x in prime_factors.keys() if x not in possible_primes]:
        return False  # wrong instruction (primes not in possibleprimes)

    if 2 not in prime_factors.keys():
        return False  # 2 must always be a factor for any instruction

    if 5 not in prime_factors.keys():
        referenced_states.append(0)
    else:
        referenced_states.append(prime_factors.get(5))

    if 3 in prime_factors.keys():
        if prime_factors.get(3) != 1:
            return False  # wrong exponent (0 for addition, 1 for substraction)

        if 7 not in prime_factors.keys():
            referenced_states.append(0)
        else:
            referenced_states.append(prime_factors.get(7))
    elif 7 in prime_factors.keys():
        return False  # 7 can't be a factor in addition

    return referenced_states


def u(n, k, m):
    """
    To see if n encodes a program, we have to check if:
    1- n = 2^i(1)*3^i(2)*...*p(r-1)^i(r)
    2- Each i(t) = 2^j*5^k OR i(t) = 2^j*3*5^k*7^l

    This translate into checking for the following:
    1- A instruction can only have 2, 3, 5 and 7 as prime factors (done)
    2- A instruction must have 2 as prime factor (done)
    3- 3 in a instruction must be either to the power 0 or 1 (done)
    4- A instruction must not reference a non existent state (done)
    5- There must be a valid instruction for each referenced state (done)
    """
    prime_descomposition = prime_factorization(n)
    prime_factors = list(prime_descomposition.keys())
    primes_indexed = primes_up_to(prime_factors[-1])
    states = {0: [0]}

    for i in range(0, len(primes_indexed)):
        p = primes_indexed[i]
        if p not in prime_factors:
            states[i+1] = False
            continue

        exponent = prime_descomposition.get(p)

        states[i+1] = is_instruction(exponent)

    for state in states.keys():
        if not states.get(state):
            continue

        for s in states.get(state):
            if s not in states.keys():
                return 'State '+str(s)+' does not exist, accessed from '+str(state)
            elif not states.get(s):
                return 'State '+str(s)+' is not valid, accessed from '+str(state)

    '''
    An encoded k-uple is a product of the first k prime numbers (except for 2, which
    we'll consider the 0-th prime number for the sake of notation) where the
    exponent of the i-th prime represents the value on the register Ri.

    That said, getting the exponents for the first k prime numbers should just
    check the following:
    1- The factorization can't contain a prime past the k-th prime number
    2- If a prime before the k-th prime number is not present in the factorization,
        that means the corresponding register is set to 0
    '''
    prime_descomposition = prime_factorization(m)
    prime_factors = list(prime_descomposition.keys())
    primes_indexed = primes_up_to(prime_factors[-1])
    primes_indexed.remove(2)
    registers = {}

    if 2 in prime_factors:
        return '2 cannot be a factor in the descomposition for the '+str(k)+'-uple'

    if len(primes_indexed) > k:  # Checks for condition 1
        return 'More than '+str(k)+' registers represented in the '+str(k)+'-uple'

    for i in range(0, len(primes_indexed)):  # Includes all up to the biggest one that appears in the factorization
        p = primes_indexed[i]
        if p not in prime_factors:
            registers[i+1] = 0
        else:
            registers[i+1] = prime_descomposition.get(p)

    for i in range(len(primes_indexed), k):  # Sets to 0 the registers past the bigest one in the factorization (if any)
        registers[i+1] = 0

    return True


# For the examples, we are using the next program:
# (2, -, 2, 0) S1
# (1, +, 1)    S2
# On each error, we either add a third state or modify a existent one

# Work:
# print(u(fmul(power(2, 300), power(3, 10)), 2, power(5, 2)))  # Works with everything well defined
# print(u(fmul(fmul(power(2, 300), power(3, 10)), power(5, 10)), 2, power(5, 2)))  # Works with a non accessible, well defined state
# print(u(fmul(fmul(power(2, 300), power(3, 10)), power(5, 7)), 2, power(5, 2)))  # Works with a non accessible, bad defined state

# Fail on the encoded program:
# print(u(fmul(power(2, 300), power(3, 250)), 2, power(5, 2)))  # Fails on non existant state
# print(u(fmul(power(2, 300), power(3, 7)), 2, power(5, 2)))  # Fails on non valid state

#Fail on the encoded k-uple:
# print(u(fmul(power(2, 300), power(3, 10)), 2, fmul(power(2, 7), power(5, 2))))  # Fails on 2 as a factor encoding the k-uple
# print(u(fmul(power(2, 300), power(3, 10)), 2, fmul(power(5, 2), power(7, 4))))  # Fails on more than k registers
