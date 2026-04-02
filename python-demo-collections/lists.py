# Lists are mutable & ordered iterable collections
# Useful in place of arrays
list

my_list = ["Kiwi", "Lime"]

print(my_list[0], my_list[1]) # We can access members by index with [brackets]



my_list.append("Apples")
my_list.append("Banana")
my_list.append("Orange")
my_list.insert(0, "Dragon Fruit")
my_list.remove("Banana")

# Stack & queue operations - We really only have pop, and it's implemented with index access.
# by default, with no index, this is pop_back, it pops from the back of the list. Append is basically
# push_back, and insert can be used to push to the front.
fruit_0 = my_list.pop(0)

# We can combine lists with extend()
my_list.extend(["Tomato", "Zucchini"])

# We can pass any iterable into the sorted() function to produce a sorted list, based on natural order.
# We can provide a key for sorting, which controls how the sort is done.
sorted_list = sorted(my_list)
custom_sorted_list = sorted(my_list, key=lambda s: len(s)) # This sorts by length instead of alphabetical



# The key isn't a consumer, this is less like Java Streams than I thought. The key is just that, a key.
# The key produces a value, these values are not compared to eachother like a consumer might do, instead
# each value in the iterable is transformed with the key function, the result is then sorted on 
# natural order (like alphabetical or numerical)
my_list.sort(key=lambda s: (len(s), s.lower()))


# Commonly we would pass an ad-hoc anonymous lambda function, but we can just pass any function that fits.
def my_sort_func(s) -> tuple[int, str]:
    return (len(s), s.lower())

my_list.sort(key=my_sort_func)


print(my_list)
print(sorted_list)

for t in my_list:
    print(t)