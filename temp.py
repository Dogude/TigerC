
import re
import sys

line = '"add.h"'
iline = '<123.h>'

j = re.findall(r'[a-zA-Z0-9_-]+|\s|.|"|<|>',line)

g = []

for i in j:
	if i == ' ':
		continue
	g.append(i)
			
print(g , len(g))

sys.exit(1)

filename = ''

if len(j) == 5:	
	for i in range(len(j)):
			if j[i] == '"':
				filename = j[i+1] + j[i+2] + j[i+3]
			if j[i] == '<':
				filename = j[i+1] + j[i+2] + j[i+3]
				
print(filename)			
