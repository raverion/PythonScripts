number = input("Input any number: ")

remainder = 0
prev_remainder = 1
exponent = 1
while remainder != prev_remainder:
    prev_remainder = remainder
    remainder = int(number) % 10 ** exponent
    exponent += 1


number_of_digits = exponent-2
print(number_of_digits)


inverted_number = 0
prev_modulo = 0
for i in range(number_of_digits):
    inverted_number += int((int(number) % 10 ** (i+1) - prev_modulo)* 10**(number_of_digits-1-i*2))
    prev_modulo = int(number) % 10 ** (i+1)


print("inverted number = ",inverted_number)
