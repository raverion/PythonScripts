def calcR(limit):
    
    x = limit
    Rab = 3 * (1/2**x)
    print(x)
    while x>0:
        x = x - 1
        Rab = (Rab * 1/2**x) / (Rab + 1/2**x)
        if x>0:
            Rab = Rab + (2 * 1/2**x)
        
    return (Rab)

if __name__ == '__main__':

    number = input("enter limit: ")

    result = calcR(int(number))

    print(result)
