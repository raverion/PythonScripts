def count_digits(number):

    i = 0
    while number // (10**i): #divide and round-down (floor division) by powers of 10 until result is 0
        i += 1

    return(i)

def invert_number(number):

    num_digits = count_digits(number)
    result = 0
    digit = 0
    previous_modulo = 0
    for digit_index in range(num_digits):
        digit = number - previous_modulo #subtract the remainder from previous iteration so that the number is a multiple of 10, 100, 1000, ...
        digit = digit % (10 ** (digit_index + 1)) #get the new remainder if divided by 10, 100, 1000, ...
        digit = int(digit / (10 ** digit_index)) #divide by 10, 100, 1000, ...
        previous_modulo = number % (10 ** (digit_index + 1)) #store the remainder for next iteration
        result += digit * (10 ** (num_digits - digit_index - 1))
        
    return(result)

if __name__ == "__main__":

    while True:
        number = int(input("Enter Positive Integer in Decimal format: "))
        if(number<0):
            print(number, "is a negative number. Please enter a positive value...")
        else:
            break
        
    print("Number of digits:",count_digits(int(number)))
    print("Inverted number:",invert_number(int(number)))
