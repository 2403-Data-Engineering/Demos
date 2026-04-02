# unordered and mutable
# uniqueness - no dupes

empty_set = {}


set_one = {"Banana", "Apple"}
set_one.add("Orange")
print(set_one)
print(len(set_one))

set_two = {"Banana", "Kiwi", "Lime"}

print("Union: ", set_one | set_two)
print("Intersect: ", set_one & set_two)
print("Diff A - B: ", set_one - set_two)
print("Diff B - A: ", set_two - set_one)
print("Symetric: ", set_one ^ set_two)


if "Banana" in set_one:
    print("Banana is in set one")
