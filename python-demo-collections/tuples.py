# Tuples are immutable & ordered - These are read only

tuple_example = (1, 2)
print(tuple_example)

a, b = tuple_example

print(a, b)


nonupple = (1,2,3,4,5,6,7,8,9)
a, b, c, _, _, d, *the_rest = nonupple

print(a,b,c,d)
print(the_rest)


a, b, *six, d = nonupple
print(a, b, d)
print(six)
print(type(nonupple))

from collections import namedtuple
Thing = namedtuple ('type', ["one", "two"])
named_tuple = Thing(1,2)
print(named_tuple.one)
print(type(named_tuple))