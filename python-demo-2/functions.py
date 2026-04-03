# Python is dynamically typed. This means that values have types, but variables don't. 
# Think of variables as the containers that hold values.

x:int = 1
x = "1"
# this is allowed becuase python's type hinting is not strictly enforced by the language.


# Args & kwargs: positional arguments and keyword arguments
# We can call the function and pass the arguments either based on position or based on key name
# for disambiguation: args first, kwargs next, default values must be last
def identifier(a: str, b: int, c, e, d="name") -> str:
    return a

# identifier(1, 2, 3, 4, 5)
# identifier(1, 2, 3, e=5, d=4)
# identifier(a=1, b=2, c=3, 4, 5) # This causes errors, the interpreter cannot disambiguate 4 and 5.
# Keyword args must come after positional args. If they come before, how can you be sure about the positional order of the rest?


# The *args and **kwargs parameters are like java's "varargs" or javascript's "rest" operator. These allow
# us to pass any number of positional args or keyword args.
# Just like before, kwargs must come last for disambiguation.
def function_2(a, b, *args):
    print(a)
    print(b)
    for s in args:
        print(s)
# function_2("a", "b", "The rest", "Of", "the args")


def function_3(a, b, **kwargs):
    print(a)
    print(b)
    for k, v in kwargs.items():
        print(k + ": " + v)

# function_3(a="a", b="b", c="The rest", d="Of", e="the args")

def function_4(a, b, *args, **kwargs):
    print(a)
    print(b)
    for s in args:
        print(s)
    for k, v in kwargs.items():
        print(k + ": " + v)

function_4("a", "b", "The rest", d="Of", e="the args")

# identifier(1, 2)
# identifier(1, 2, 3, a=4, e=5)



my_list = ["apple", "bananana", "orange"]
def my_list_function(l: list):
    for s in l:
        print(s)


my_list_function(my_list)


def test_function():
    print("This is the test function.")

def my_callback(a: callable):
    a()
print("My callback example: ")
my_callback(test_function)


def process(names: list[str]) -> list[int]:
    return [len(n) for n in names]

