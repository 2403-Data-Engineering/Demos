# All of the collections are iterables. They all have implementations for __iter__() and __next__().
# __iter__() returns a new iterator. Doing so should start again at the beginning of the collection traversal.
# __next__() reutnrs the next element in the iterable. 
# You'll need to implement these with some sort of backing functionality to track where in the traversal
# the iterable is. For a list based on an array or other index-based structure, you could simply keep
# a variable that contains the current index, and advnaces when __next__() is called.

from typing import Iterable


class MyIterable:
    def __init__(self, *args):
        self.index = 0
        self.list: list = []

    # __iter_() must return an object that has a valid __next__() method. So we just return self.
    # We also reset the index count when a new iter is requested, as traversal starts over. We discard the old value.
    def __iter__(self):
        self.index = 0
        return self

    # __next__() returns the next element each time it is called. We also need to handle the end of iteration.
    # The python for loop expects to keep going until the StopIteration exception is raised.
    def __next__(self):
        self.index += 1
        if self.index > len(self.list):
            raise StopIteration
        return self.list[self.index - 1]

    def add(self, element):
        self.list.append(element)

    def get(self, index) -> any:
        return self.list[index]
    


my_iterable = MyIterable()
my_iterable.add(1)
my_iterable.add(2)
my_iterable.add(3)

for e in my_iterable:
    print(e)