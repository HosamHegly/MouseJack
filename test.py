f = open('script.txt', 'r')
for line in f:
    for word in line.split()[1:]:
         for x in word:
             print(x)
