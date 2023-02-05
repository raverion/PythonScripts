import random
import sys

def factorial(n):
    if (n==0):
        return 1
    else:
        return n*factorial(n-1)

def nCr(n, r):
    return factorial(n) / (factorial(n-r) * factorial(r))

#--------------------------------------------------------------------------------------------------------------
# estimating average length between any 2 points in a line segment by generating random numbers

sum_of_all_distances = 0
for num_points in range(1,1000000):
    x1 = random.uniform(0,1)
    x2 = random.uniform(0,1)
    sum_of_all_distances = sum_of_all_distances + abs(x1-x2)

average = sum_of_all_distances / num_points

print("average by random   =",average)


#--------------------------------------------------------------------------------------------------------------
# estimating average length between any 2 points in a line segment by dividing the line segment infinitesimally

sys.setrecursionlimit(2500)

num_points = 2500
num_divs = num_points - 1
num_pairs = nCr(num_points,2)

div = 1 / num_divs
sum_of_all_distances = 0
n = 1
step = 0
while (num_divs-step)>0:
    sum_of_all_distances = sum_of_all_distances + div * n * (num_divs-step)
    step = step + 1
    n = n + 1
    
average = sum_of_all_distances / num_pairs

print("average by division =",average)
