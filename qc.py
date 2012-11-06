#!/usr/bin/python
"""
A simple random commands generator to provide a variable
list of commands, keys, and values to simpledb.py.
"""

__author__ = "Arian Solberg"
__version__ = "1.0.0"
__email__ = "asolberg@gmail.com"

import string
import random

seed_db = {'BEGIN': 4, 'SET': 14, 'ROLLBACK': 3, 'GET': 12, 'NUMEQUALTO': 8, 'COMMIT': 3, 'UNSET': 4}
cmd_list = []
keys = string.lowercase + string.uppercase
vals = list(xrange(20))
f = open('qc1.in', 'w')
for key, value in seed_db.items():
  for i in range(value):
    cmd_list.append(key)
random.shuffle(cmd_list)

for i in range(2000):
  x = random.randint(0,len(cmd_list)-1)
  cmd = cmd_list[x]
  if cmd == 'SET':
    cmd += ' ' + keys[random.randint(0,len(keys)-1)] + ' ' + str(vals[random.randint(0,len(vals)-1)])
  if cmd == 'GET':
    cmd += ' ' + keys[random.randint(0,len(keys)-1)]
  if cmd == 'NUMEQUALTO':
    cmd += ' ' + str(vals[random.randint(0,len(vals)-1)])
  if cmd == 'UNSET':
    cmd += ' ' + keys[random.randint(0,len(keys)-1)]
  f.write(cmd + '\n')
f.write('END')
