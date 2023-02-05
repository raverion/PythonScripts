def change_var(val):
    global x
    x = val

if __name__ == '__main__':

    x = 2
    print(x)
    change_var(3)
    print(x)
