# Comprehension in python is "syntactic sugar", or shortcut syntax. It's a way of looping and preforming operations 
# without writing out the whole loop explicitly.

fruit_list = ["Apple", "Banana", "Orange"]

# We can create a loop to print the values of these list items:
print("Normal loop:")
for s in fruit_list:
    print(s)

# This is such a common operation that a shortcut exists: list comprehension.
# This is an equivalent to the loop above:
print("List comprehension: ")
result = [print(s) for s in fruit_list]

# We can assign the result of list comprehension and utilize that. In this example, however, the result is empty.
# Can you tell why that is?
print("Result: ")
print(result)

# It was empty because the list was created based on preforming the print() function on each item. print() doesn't
# return any value, so the resultant list has three "None" values. print() has a side effect of outputting text to the 
# terminal, but it doesn't result in anything. Here's a better example:

# Here we are printing the list that results from taking the length of each string in the original list.
print("lengths: ")
print([len(s) for s in fruit_list])

