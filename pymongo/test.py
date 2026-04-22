from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from model import User, Address, Preferences


# ---------- Connection ----------

class Database: 
    def __init__(self, uri="mongodb://localhost:27017", db_name="test_db"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]


# ---------- User DAO ----------

class UserDAO:
    def __init__(self, db:Database):
        self.collection:Database = db["users"]

    def create(self, user: User):
        result = self.collection.insert_one(user.to_dict())
        return result.inserted_id

    def find_by_id(self, user_id):
        user = User("","")
        return user.from_dict( self.collection.find_one({"_id": ObjectId(user_id)}))

    def update(self, user_id, **kwargs):
        if kwargs is None:
            return

        user = self.find_by_id(user_id)

        for k, v in kwargs.items():
            if k == "name":
                user.name = v
            if k == "email":
                user.email = v
            if k == "address_id":
                user.address_id = ObjectId(v)


        return self.collection.update_one({"_id": ObjectId(user_id)}, {"$set": user.to_dict()})


    def update_preferences(self, user_id, **kwargs):
        if kwargs is None:
            return

        user = self.find_by_id(user_id)
        temp = Preferences()
        for k, v in kwargs.items():
            if k == "language":
                temp.language = v
            if k == "notifications":
                temp.notifications = v
            if k == "theme":
                temp.theme = v
            if k == "timezone":
                temp.timezone = v
        user.preferences = temp


        return self.collection.update_one({"_id": ObjectId(user_id)}, {"$set": user.to_dict()})


    def get_with_address(self, user_id):
        ret = self.collection.aggregate([
            {"$match" : {"_id":ObjectId(user_id)}},
            {"$lookup": {
                "from": "users",
                "localField": "address_id",
                "foreignField":  "_id",
                "as": "address",
            }} ])
        for r in ret:
            print(r)
        return ret

    def delete(self, user_id):
        return self.collection.delete_one({"_id": ObjectId(user_id)}).deleted_count

class AddressDAO:
    def __init__(self, db):
        self.collection = db["addresses"]

    def create(self, address: Address):
        return self.collection.insert_one(address.to_dict()).inserted_id

    def find_by_id(self, address_id):
        ads = Address("","","","")
        return ads.from_dict(self.collection.find_one({"_id": ObjectId(address_id)}))

    def find_all(self) -> list[Address]:

        ls = []
        for ads in self.collection.find():
            temp_ads = Address("","","","")
            ls.append(temp_ads.from_dict(ads))


        return ls


    def update(self, address_id, **kwargs):
        if kwargs is None:
            return

        ads = self.find_by_id(address_id)

        for k, v in kwargs.items():
            if k == "street":
                ads.street = v
            if k == "city":
                ads.city = v
            if k == "state":
                ads.state = v
            if k == "zip":
                ads.zip = v


        return self.collection.update_one({"_id": ObjectId(address_id)}, {"$set": ads.to_dict()})

    def delete(self, address_id):
        return self.collection.delete_one({"_id": ObjectId(address_id)}).deleted_count


if __name__ == "__main__":
    db = Database().db
    users = UserDAO(db)
    address = AddressDAO(db)

    a = User("Alice5", "alice@example.com")

    print("Create user and find it")
    alice_id = users.create(User("Alice", "alice@example.com"))

    alic = users.find_by_id(alice_id)
    print(alic)

    print(alic)
    print(alic.to_dict())
    print(alic.name)
    print("Create Address and find it")
    ads_id = address.create(Address("6 Aldgate Ct","Princeton","NJ","09810"))
    ads = address.find_by_id(ads_id)
    print(ads_id)
    print(ads.to_dict())
    for a in address.find_all():
        print(a.to_dict())

    print("Update User and assign an address")

    users.update(alice_id, name="Alic", email="alic@example.com", address_id = ads_id)

    alic = users.find_by_id(alice_id)
    print(alic)
    print(alic.to_dict())
    print(alic.name)


    print("Update Address")
    address.update(ads_id, street= "33 Beacon")
    ads = address.find_by_id(ads_id)
    print(ads.to_dict())


    print("Update User preferences")

    users.update_preferences(alice_id, notifications={"email": False, "sms": True}, language="sp", theme= "dark")

    alic = users.find_by_id(alice_id)
    print(alic.to_dict())
    print(alic.name)



    print("Get with user address")

    users.get_with_address("69dd380a90acc8c17f941298")




 