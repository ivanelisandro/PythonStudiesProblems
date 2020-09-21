friends = []
while True:
    name = input()
    if name == ".":
        break
    else:
        friends.append(name)

print(friends)
print(len(friends))
