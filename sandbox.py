import sys


def my_function(*myArgs):
    '''my function'''
    print(myArgs)
    result = 1
    for i in myArgs:
        result *= i
    return result


print(my_function(3, 4, 5))
print(my_function(4, 8, 12))
