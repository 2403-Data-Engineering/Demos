from bson import ObjectId


class Preferences:
    def __init__(self, theme="light", language="en",
                 notifications=None, timezone="America/New_York"):
        self.theme = theme
        self.language = language
        self.notifications = notifications or {"email": True, "sms": False}
        self.timezone = timezone

    def to_dict(self):
        return {
            "theme": self.theme,
            "language": self.language,
            "notifications": self.notifications,
            "timezone": self.timezone,
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return cls()
        return cls(
            theme=data.get("theme", "light"),
            language=data.get("language", "en"),
            notifications=data.get("notifications"),
            timezone=data.get("timezone", "America/New_York"),
        )


class Address:
    def __init__(self, street, city, state, zip_code, _id=None):
        self._id = _id
        self.street = street
        self.city = city
        self.state = state
        self.zip = zip_code

    def to_dict(self):
        doc = {
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "zip": self.zip,
        }
        if self._id:
            doc["_id"] = self._id
        return doc

    @classmethod
    def from_dict(cls, data):
        return cls(
            _id=data.get("_id"),
            street=data["street"],
            city=data["city"],
            state=data["state"],
            zip_code=data["zip"],
        )


class User:
    def __init__(self, name, email, address_id=None,
                 preferences=None, _id=None):
        self._id = _id
        self.name = name
        self.email = email
        self.address_id = address_id            # ObjectId reference
        self.preferences = preferences or Preferences()


    def to_dict(self):
        doc = {
            "name": self.name,
            "email": self.email,
            "address_id": self.address_id,
            "preferences": self.preferences.to_dict(),
        }
        if self._id:
            doc["_id"] = self._id
        return doc

    @classmethod
    def from_dict(cls, data):
        return cls(
            _id=data.get("_id"),
            name=data["name"],
            email=data["email"],
            address_id=data.get("address_id"),
            preferences=Preferences.from_dict(data.get("preferences")),
        )