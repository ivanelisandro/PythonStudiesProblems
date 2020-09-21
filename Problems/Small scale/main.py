numbers = []
while True:
    number = input()
    if number == ".":
        break
    else:
        numbers.append(float(number))

print(min(numbers))
