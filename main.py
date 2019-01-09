from mpmath import *


mp.dps = 10000  # This needs to be a higher value for bigger programs


class Instruction:
    def __init__(self, referenced_register, substraction, referenced_states):
        self.referenced_register = referenced_register
        self.substraction = substraction
        self.referenced_states = referenced_states

    def __repr__(self):
        return 'Instruction(%s, %s, %s)' % (self.referenced_register, self.substraction, self.referenced_states)

    def __str__(self):
        operation = '+'
        if self.substraction:
            operation = '-'

        states_string = ''
        for s in self.referenced_states:
            states_string += ', '+str(s)

        return '('+str(self.referenced_register)+', '+operation+states_string+')'


def encode_instruction(instruction):
    register = instruction.referenced_register
    is_substraction = instruction.substraction
    states = instruction.referenced_states

    code = power(2, register)

    if is_substraction:
        code *= mpf(3)

    code *= power(5, states[0])

    if len(states) == 2:
        code *= power(7, states[1])

    return code


def prime_factorization(n):
    """Returns a dictionary with keys the prime factors and values their exponent"""
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

    factorization = {}

    for p in prime_factors:
        current_exponent = factorization.setdefault(p, mpf(0))
        factorization[p] = factorization[p] + 1

    return factorization


def primes_up_to(p):
    """Generates prime numbers up to p (sieve of Eratosthenes)"""
    last = int(float(nstr(p)))

    prime_list = [mpf(2)]
    p_half = power(p, 0.5)
    flags = [True, True] + [False] * (last-1)

    # Just checks odd numbers
    for i in range(3, last+1, 2):
        if flags[i]:
            continue
        prime_list.append(mpf(i))
        # Excludes multiples of the prime
        if i <= p_half:
            for j in range(i*i, last, i << 1):
                flags[j] = True

    return prime_list


def is_instruction(instruction):
    """Check for valid instructions. Returns false if it is not a valid instruction,
     a list with the referenced states if it is"""
    prime_factors = prime_factorization(instruction)
    possible_primes = [2, 3, 5, 7]
    referenced_register = mpf(0)
    is_substraction = False
    referenced_states = []

    if [x for x in prime_factors.keys() if x not in possible_primes]:
        return False  # wrong instruction (primes not in possibleprimes)

    if 2 not in prime_factors.keys():
        return False  # 2 must always be a factor for any instruction

    referenced_register = prime_factors.get(2)

    referenced_states.append(prime_factors.get(5, 0))

    if 3 in prime_factors.keys():
        if prime_factors.get(3) != 1:
            return False  # wrong exponent (0 for addition, 1 for substraction)

        is_substraction = True

        referenced_states.append(prime_factors.get(7, 0))
    elif 7 in prime_factors.keys():
        return False  # 7 can't be a factor in addition

    return Instruction(referenced_register, is_substraction, referenced_states)


def u(n, k, m):
    """
    To see if n encodes a program, we have to check if:
    1- n = 2^i(1)*3^i(2)*...*p(r-1)^i(r)
    2- Each i(t) = 2^j*5^k OR i(t) = 2^j*3*5^k*7^l

    This translate into checking for the following:
    1- A instruction can only have 2, 3, 5 and 7 as prime factors
    2- A instruction must have 2 as prime factor
    3- 3 in a instruction must be either to the power 0 or 1
    4- A instruction must not reference a non existent state
    5- There must be a valid instruction for each referenced state
    """
    prime_descomposition = prime_factorization(n)
    prime_factors = list(prime_descomposition.keys())
    primes_indexed = primes_up_to(prime_factors[-1])
    states = {mpf(0): Instruction(mpf(0), False, [mpf(0)])}

    for i in range(0, len(primes_indexed)):
        p = primes_indexed[i]
        if p not in prime_factors:
            states[mpf(i+1)] = False
            continue

        exponent = prime_descomposition.get(p)

        states[mpf(i+1)] = is_instruction(exponent)

    for state in states.keys():
        if not states.get(state):
            continue

        accessible_states = states.get(state).referenced_states

        for s in accessible_states:
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

    for i in range(0, len(primes_indexed)):  # Includes primes up to the biggest one that appears in the factorization
        p = primes_indexed[i]

        registers[mpf(i+1)] = prime_descomposition.get(p, mpf(0))

    for i in range(len(primes_indexed), k):  # Sets to 0 the registers past the bigest one in the factorization (if any)
        registers[mpf(i+1)] = mpf(0)

    '''
    Now that we know everything can execute, we do it. To do so, we run a while
    loop that checks the state we are on, starting at S1, that stops when we reach
    state S0. Do note, though, a program may never stop, e.g.
    (1, +, 1) S1
    That program just continuosly adds 1 to the first register, never reaching S0.

    Also note that any of the list accesses should not cause a problem since we
    already checked the instruction values, so addition instructions have exactly
    1 accessible state and substraction steps have 2.

    The program returns the last state of the registers, although it should return
    the value in register 1, just to make sure a program does what it should.
    '''
    current_state = mpf(1)

    while current_state != 0:
        current_instruction = states.get(current_state)
        current_register = current_instruction.referenced_register
        register_value = registers.setdefault(current_register, mpf(0))
        accessible_states = current_instruction.referenced_states

        if current_instruction.substraction:
            if not register_value:
                current_state = accessible_states[1]
            else:
                registers[current_register] = register_value - mpf(1)
                current_state = accessible_states[0]
        else:
            registers[current_register] = register_value + mpf(1)
            current_state = accessible_states[0]

    return registers


# For the next examples, we will use the next program:
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

# Fail on the encoded k-uple:
# print(u(fmul(power(2, 300), power(3, 10)), 2, fmul(power(2, 7), power(5, 2))))  # Fails on 2 as a factor encoding the k-uple
# print(u(fmul(power(2, 300), power(3, 10)), 2, fmul(power(5, 2), power(7, 4))))  # Fails on more than k registers


# The example below shows a bigger program. Things start getting real slow after 4 states:
# (1, -, 1, 2) S1
# (2, -, 3, 0) S2
# (1, +, 4)    S3
# (1, +, 2)    S4
# This program empties R1 and adds double the content on R2 to R1

# s1 = encode_instruction(Instruction(mpf(1), True, [mpf(1), mpf(2)]))
# s2 = encode_instruction(Instruction(mpf(2), True, [mpf(3), mpf(0)]))
# s3 = encode_instruction(Instruction(mpf(1), False, [mpf(4)]))
# s4 = encode_instruction(Instruction(mpf(1), False, [mpf(2)]))

# print(u(fprod([power(2, s1), power(3, s2), power(5, s3), power(7, s4)]), 2, fmul(power(3, 2), power(5, 2))))
