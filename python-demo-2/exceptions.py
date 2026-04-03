import traceback


class MyCustomException(Exception):
    pass


raise MyCustomException()



def func_1():
    raise KeyError("We forced this exception for a demo.")
    return None

def func_2():
    try:
        func_1()
    except KeyError:
        print("The code has silently consumed the exception")
        traceback.print_exc()
        raise


def func_3():
    """Possibly raises KeyError"""
    func_2()



try:
    func_3()
except KeyError:
    print("oops")





# try:
#     print("no exception here")
#     raise ValueError()
# except ValueError:
#     print("There was a value error")
# except Exception:
#     print("There was an exception")
# else:
#     print("This is the case when no exceptions are raised.")
# finally:
#     print("finally block")
#     print("These operations are")


# print("finally block")
# print("These operations are")



