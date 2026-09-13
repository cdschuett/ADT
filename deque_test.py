from collections import deque

stuff = deque(maxlen=5)

stuff.append(1)
stuff.append(2)
stuff.append(3)
stuff.append(4)
stuff.append(5)

print(type(stuff))
print(stuff)