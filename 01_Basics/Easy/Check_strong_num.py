#Write your code here
a = int(input())

def Factorial(a):
    if a == 0 or a == 1:
        return 1
    return a * Factorial(a - 1)

def check_strong_num(a):
    digits = [int(d) for d in str(a)]
    Fact_sum = 0
    for num in digits:
        result = Factorial(num)
        Fact_sum += result
    if(Fact_sum == a):
        print("Yes")
    else:
        print("No")

check_strong_num(a)