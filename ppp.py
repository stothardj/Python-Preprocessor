#!/usr/bin/env python
# Python preprocessor
# This is a general preprocessor written in python. It is not
# really intended to be used on python, since python doesn't
# really need it. This is just a bit of glue for my coffeescript, based
# on c preprocessor, but simple enough that it won't do anything
# it's not supposed to and not conflicting with # as comments

# For now very simple, just enough to allow including other files from the same directory
# More features may be as needed

import argparse
import re
import os
parser = argparse.ArgumentParser(description='Python preprocessor')
parser.add_argument('filename')
args = parser.parse_args()

import_prefix = '__import_'

# Signal at the start of the line that this may be for ppp
sig = '!'

# Syntax, if can it can even be called that
# Note: change the right hand side if you want to modify what is recognized as
# the syntax. The left is the meaning that is used
syntax = {
    'def' : 'define',
    'udef' : 'undefine',
    'ifdef' : 'ifdef',
    'ifndef' : 'ifndef',
    'else' : 'else',
    'endif' : 'endif',
    'include' : 'include',
    'import' : 'import'
}

defs = {}
# Are we in a case where we should print to stdout?
ifstack = [True]

# So I can use recursion for include
def process_file(fname):
    with open(fname, 'r') as f:
        for line in f:
            # Should I print this line as it is?
            printit = all(ifstack)

            if line[:len(sig)] == sig:
              for k, v in syntax.items():
                  # Does it start with v?
                  sel = re.match('\s*%s(.*)' % v, line[len(sig):])
                  if sel:
                      args = sel.group(1)
                      if k == 'def':
                          m = re.match(r'\s+(\S+)\s*(\S*)', args)
                          defs[m.group(1)] = m.group(2)
                          printit = False
                      elif k == 'udef':
                          m = re.match(r'\s+(\S+)', args)
                          del defs[m.group(1)]
                          printit = False
                      elif k == 'ifdef':
                          m = re.match(r'\s+(\S+)', args)
                          ifstack.append( m.group(1) in defs )
                          printit = False
                      elif k == 'ifndef':
                          m = re.match(r'\s+(\S+)', args)
                          ifstack.append( m.group(1) not in defs )
                          printit = False
                      elif k == 'else':
                          ifstack[-1] = not ifstack[-1]
                          printit = False
                      elif k == 'endif':
                          ifstack.pop()
                          printit = False
                      elif k == 'include':
                          # TODO: use path. Pay attention to "" vs <>
                          # This is the curdir of the file doing the including,
                          # not the curdir of the ppp program
                          curdir = os.path.split(fname)[0]
                          loc = args.strip()
                          
                          process_file( os.path.join(curdir, loc[1:-1]) )
                          printit = False
                      elif k == 'import':
                          loc = args.strip()
                          # Yes I leave on the "" or <>, that way if it later
                          # causes two different files to be included based
                          # on whether the curdir is included then it won't collide
                          key = import_prefix + loc
                          if key not in defs:
                              defs[key] = ''
                              curdir = os.path.split(fname)[0]
                              process_file( os.path.join(curdir, loc[1:-1]) )
                          printit = False
            if printit:
                print (line, end='')

if __name__ == '__main__':
    process_file(args.filename)
