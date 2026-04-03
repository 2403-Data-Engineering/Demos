# Lambdas are Ad-hoc anonymous functions, functions we don't keep to re-use.

# This lambda is equivalent to the square() function defined below
square = lambda x: x ** 2

def square(x):
    return x ** 2

# We often use these as callback functions, defined ad-hoc inline.
# Callback function - function passed as a parameter, to be called "later" 
# where later means after something else happens


def do_math(x, y, lambda_function):
    return lambda_function(x, y)



print(do_math(2, 3, lambda x, y: x * y))