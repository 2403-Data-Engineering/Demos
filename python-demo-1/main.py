class Animal:

    def __init__(self, name):
        self.name = name
        print("This is in the __init__ method")

    def sound(self):
        print("I'm an animal")

class Dog(Animal):
    def __init__(self, name):
        self.name = name
    
    def sound(self):
        print("bark!")
    



bobby = Animal("bobby")
harry = Dog("harry")
harry.sound()

