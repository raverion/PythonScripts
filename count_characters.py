'''for brushing up my python skills'''


def find_most_repeated(input_dict):
    '''find the most repeated character'''
    return max(input_dict, key=input_dict.get)


MESSAGE = 'It was a bright cold day in April, and the clocks were striking thirteen.'

count = {}

for char in MESSAGE.upper():
    if char == ' ':
        continue
    count.setdefault(char, 0)
    count[char] += 1

print(count)

# sort dictionary be decreasing value
count = dict(sorted(count.items(), key=lambda item: item[1], reverse=True))

print(count)

most_repeated = find_most_repeated(count)

print(most_repeated)
