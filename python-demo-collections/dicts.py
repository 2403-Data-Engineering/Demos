user = {"name": "Kyle", "age": 40}

print(user)

print(user["age"])
print(user.get("age"))

user["age"] += 1
user["email"] = "Kyle.plummer@revature.com"

user["age"] = "None"

# del user["age"]

print(user)

# thing = user.pop("email")

# print(thing)
print(user)

for k, v in user.items():
    print(k, v)


print("=========================")
my_other_dict = {v + "." for k, v in user.items()}

print(user)
print(my_other_dict)