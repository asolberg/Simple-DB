#!/usr/bin/python
"""
A simple in-memory database supporting transactions
in an memory-efficient manner.
SET n 2 (set variable n to 2)
GET n (return variable n)
UNSET n (remove the variable assigned to n)
NUMEQUALTO 2 (return a variable count set to 2)
BEGIN (begin a transactional block, can be layered)
COMMIT (commit a transactional block)
ROLLBACK (rollback a transactional block)
"""

__author__ = "Arian Solberg"
__version__ = "1.0.0"
__email__ = "asolberg@gmail.com"


import sys

# initiate db data structures, starting variables
index = [{}]
db = [{}]
depth = 0

# set debug for verbose data structure output on every command
# set unit test for verification of correct indexing

SET_UNIT_TEST = 0 
SET_DEBUG = 0

# while in a transaction block this function
# determines if a variable has been set somewhere
# down the stack

def findLevelSet(var):
  levels_scan = depth
  while var not in db[levels_scan]:
    if levels_scan == 0:
      break
    levels_scan -= 1
  if var in db[levels_scan]:
    return (levels_scan, db[levels_scan][var])
  else:
    return None

# while in a transaction block this function determines
# if a value has been set somewhere down the stack

def findIndexSet(val):
  levels_scan = depth
  while val not in index[levels_scan]:
    if levels_scan == 0:
      break
    levels_scan -= 1
  if val in index[levels_scan]:
    return (levels_scan, index[levels_scan][val])
  else:
    return None

k = 0
while True:
  k = k + 1
  command = sys.stdin.readline()
  cl = command.split()
  if cl[0] == 'SET' and len(cl) == 3:
    if depth == 0:
      # Update index to reflect new value addition
      if cl[2] in index[0]:
        index[0][cl[2]] += 1
      else:
        index[0][cl[2]] = 1
      
      # Update index to reflect loss of old value
      if cl[1] in db[0]:
        old_value = db[0][cl[1]]
        # None value gets carried through but we don't track that in the index
        if old_value != None:
          index[0][old_value] -= 1

      # Set key, value in db
      db[0][cl[1]] = cl[2]
    
    else:
      # Find the most recent information about the key, value pair
      mrs = findLevelSet(cl[1]) #most recent set
      if mrs:
        if mrs[1] != None:
          #existing key in db, meaning we must update the index to reflect the loss of the old value
          value_lost = mrs[1] 
          if value_lost in index[depth]:
            index[depth][value_lost] -= 1
          else:
            index[depth][value_lost] = -1

      # Update the index to reflect the addition of the NEW value
      if cl[2] in index[depth]:
        index[depth][cl[2]] += 1
      else:
        index[depth][cl[2]] = 1
      db[depth][cl[1]] = cl[2]

  if cl[0] == 'GET':
    
    if depth == 0:
      if cl[1] in db[0]:
        print db[0][cl[1]]
      else:
        print 'NULL'
    else: 

      # We are in some level of transaction block. 
      # Find the most recent set and print if not None
      mrs = findLevelSet(cl[1])
      if mrs != None:
        print db[mrs[0]][cl[1]]
      else:
        print 'NULL'

  if cl[0] == 'UNSET':
    
    #level 0, remove item, decrement index
    if depth == 0:
      if cl[1] in db[0]:
        # need to update the index, but first check if value is a none value
        # left over from a previous transaction block
        # if it is, just delete it, no need to update the index
        if db[0][cl[1]] != None:
          index_item = db[0].pop(cl[1])
          index[0][index_item] -= 1
        else:
          db[0].pop(cl[1])
    
    else:

    # in some transaction block. We need to set
    # current value to none and update the index
    # but first we need to find the most recent
    # value set for the variable
      mrs = findLevelSet(cl[1])

      if mrs != None:
        if mrs[1] != None:
          if mrs[1] in index[depth] :
           # If this value is in the current depth
            # index, decrement it
            index[depth][mrs[1]] -= 1
          else:
            # otherwise start it at negative one
            # so it will propagate backwards
            # upon commit
            index[depth][mrs[1]] = -1
        db[depth][cl[1]] = None
  
  if cl[0] == 'NUMEQUALTO':
    if depth == 0:
      if cl[1] in index[0]:
        print index[0][cl[1]]
      else:
        print '0'
    else: 
      answer = 0
      for level in index:
        if cl[1] in level:
          answer+=level[cl[1]]
      print answer
  
  if cl[0] == 'BEGIN':
    depth += 1
    db.append({})
    index.append({})
  
  if cl[0] == 'COMMIT':
    if depth == 0:
      print "NOT IN A TRANSACTION BLOCK"
    else:
      for i in range ((depth)):
        #Recursively update the DB incorporating all changes since last commit
        db[depth-(i+1)].update(db[depth-i])
        # Remove the transaction block and continue
        db.pop()
      #For every level of a transacation block....
      for i in range ((depth)):
        # For every value in the index of the current block (which represents changes made)
        for val in index[depth-i]:
          # If that same value exists in the next block down....
          if val in index[depth-(i+1)]:
            # Sum the count of the values to get the new count
            index[depth-(i+1)][val] += index[depth-i][val]
          # If that value doesn't exist in the lower level, carry over the value from the higher level
          else:
            index[depth-(i+1)][val] = index[depth-i][val]
        # Remove the transaction block and continue
        index.pop()
      depth = 0 
  if cl[0] == 'END':
    sys.exit(0)
  if cl[0] == 'ROLLBACK':
    if depth == 0:
      print 'INVALID ROLLBACK'
    else:
      depth -= 1
      db.pop()
      index.pop()

  if SET_DEBUG:
    print "Command #%d: %s" % (k, command)
    print "Depth = %d" % depth
    print "Database are:"
    for l in db:
      print l
    print "Indexes are"
    for l in index:
      print l

  if SET_UNIT_TEST:
    flat_db = {}
    flat_index = {}
    index_check = {}
    for level in db:
      for key, value in level.items():
        flat_db[key] = value
    for key, value in flat_db.items():
      if value != None:
        if value in index_check:
          index_check[value] += 1
        else:
          index_check[value] = 1
    for level in index:
      for key, value in level.items():
        if key in flat_index:
          flat_index[key] += value
        else:
          flat_index[key] = value
    for key, value in flat_index.items():
      if value == 0:
        del flat_index[key]
    if index_check == flat_index:
      print "UNITS VALIDATED\n\n"
    else:
      print "index check: ",
      print index_check
      print "flat index: ",
      print flat_index
      print "UNIT MISMATCH\n\n"
      raise Exception('UNIT MISMATCH')
