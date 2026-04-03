# Strings in python are immutable sequences of characters bounded by single or double quotes.
"This is a string"
'This is also a string.'

# Three single or double quotes will create a multi-line string that includes newline characters.
"""This is
a multi line
string"""

multi_line_string_2 = '''This is also a 
multi line string, whitespace is reflected in this string

    This line is indented.'''
# probably never cause an increase in memory footprint


my_string = "This is my string"
my_string = my_string + " more string."

# String concatination in a loop is bad, strings are immutable so interning string to the string pool includes overhead
for x in range(10):
    my_string += "Even more text"


parts = []
for x in range(10):
    parts.append("Even more text")
result = "".join(parts)



# Multi-line strings are often used in python as multi-line comments. This is a common pattern for doc comments on functions:
def func(param_1: str, param_2: int) -> str:
    '''
    This is a doc comment, used to document the usage of this function. This is the text that would appear in
    the hint popups if you hover over the function name.
    Args:
    param_1: description of the parameter
    param_2: description of the parameter
    
    returns: 
        description of the return value
    Raises: 
        ValueError: or whatever, indicate the possible exceptions that could be raised
    '''

# Now hover over the function identifier to see the doc comments.
func()
# not sure why mine is only showing part of the text. Maybe a caching issue.





