# Universal-Program
Universal Program, in Python, (Mathematical) Logic project, Mathematics Degree (UMA, Spain)

Install: pip install mpmath

The goal of this project is to simulate a universal program u(n, k, m), that is, given a number n that encodes a program, k the length of a k-uple and m a k-uple (m_1, ..., m_k), then u(n, k, m) = r, where r is the final computation done by the program n. If any of the premises isn't fulfilled, then u(n, k, m) is not defined (so it must return an error)

TODO:
- A version that only uses mpmath numbers

DONE:
- Check if n actually encodes a program.
- Translation from prime to number of register/state to make it easier to read.
- Check if m actually encodes a k-uple.
- Run the program n with starting registers m if every condition is met.

CD;PW (Could Do; Probably Won't):
- Implement a better prime factorization algorithm
- Write final state (if reached) in a text file.

F.A.Q.:
- What is a encoded program?
A number encodes a program if it can be factored into primes and the exponent of each of those primes encodes a instruction.

- What is a encoded instruction?
A number encodes a instruction if it can be factored into either 2^i*5^j or 2^i*3*5^j*7^l, where i is the index of a register (a natural number) and j and l are the index of a state (0 or natural). The first kind encodes addition, the second one encodes substraction.

- Why don't do things listed in CD;PW?
Because time, as opposite to the number of registers of a Minsky machine, is finite. Maybe one day I'll do it, but probably not for presentation day.
