"""
Simple PyMongo DAO example.

Domain: a blog with users and posts.
- users: standalone documents
- posts: reference a user via author_id, embed comments inline
"""

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime


# ---------- Connection ----------

class Database:
    def __init__(self, uri="mongodb://localhost:27017", db_name="demo"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]


# ---------- User DAO ----------

class UserDAO:
    def __init__(self, db):
        self.collection = db["users"]

    def create(self, name, email):
        result = self.collection.insert_one({"name": name, "email": email})
        return result.inserted_id

    def find_by_id(self, user_id):
        return self.collection.find_one({"_id": ObjectId(user_id)})

    def find_by_email(self, email):
        return self.collection.find_one({"email": email})

    def delete(self, user_id):
        return self.collection.delete_one({"_id": ObjectId(user_id)}).deleted_count


# ---------- Post DAO ----------

class PostDAO:
    def __init__(self, db):
        self.collection = db["posts"]

    def create(self, author_id, title, body):
        post = {
            "author_id": ObjectId(author_id),
            "title": title,
            "body": body,
            "comments": [],            # embedded
            "created_at": datetime.utcnow(),
        }
        return self.collection.insert_one(post).inserted_id

    def find_by_id(self, post_id):
        return self.collection.find_one({"_id": ObjectId(post_id)})

    def add_comment(self, post_id, author_name, text):
        # embedded update with $push
        comment = {"author": author_name, "text": text, "at": datetime.utcnow()}
        return self.collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$push": {"comments": comment}}
        ).modified_count

    def get_with_author(self, post_id):
        # demonstrate $lookup to resolve the reference
        pipeline = [
            {"$match": {"_id": ObjectId(post_id)}},
            {"$lookup": {
                "from": "users",
                "localField": "author_id",
                "foreignField": "_id",
                "as": "author",
            }},
            {"$unwind": "$author"},
        ]
        results = list(self.collection.aggregate([
            {"$match": {"_id": ObjectId(post_id)}},
            {"$lookup": {
                "from": "users",
                "localField": "author_id",
                "foreignField": "_id",
                "as": "author",
            }},
            {"$unwind": "$author"},
        ]))
        return results[0] if results else None


# ---------- Demo ----------

if __name__ == "__main__":
    db = Database().db
    users = UserDAO(db)
    posts = PostDAO(db)

    alice_id = users.create("Alice", "alice@example.com")
    post_id = posts.create(alice_id, "Hello Mongo", "First post body.")
    posts.add_comment(post_id, "Bob", "Nice post!")

    print(posts.get_with_author(post_id))


    