'''fizz buzz algo'''


def fizzbuzz(input_num):
    '''fizz buzz'''
    if (input_num % 3 == 0 and input_num % 5 == 0):
        return 'fizzbuzz'
    elif (input_num % 5 == 0):
        return 'buzz'
    elif (input_num % 3 == 0):
        return 'fizz'

    return input_num


print('')
fizzbuzz(31)
