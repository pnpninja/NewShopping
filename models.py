from pydantic import Field, BaseModel
from typing import List


class StatusServer(BaseModel):
    status: str = Field(
        "online", title="If the server is online or not", const="online"
    )

    class Config:
        schema_extra = {"example": {"status": "online"}}


class RegisterData(BaseModel):
    email: str = Field(..., title="The user's email")
    password: str = Field(..., title="The user's password")
    first_name: str = Field(..., title="The user's first name")
    last_name: str = Field(..., title="The user's last name")
    phone_number: str = Field(..., title="The user's phone number")

    class Config:
        schema_extra = {
            "example": {
                "email": "example@gmail.com",
                "password": "test",
                "first_name": "Joe",
                "last_name": "test",
                "phone_number": "8326910295",
            }
        }


class LoginData(BaseModel):
    email: str = Field(..., title="The user's email")
    password: str = Field(..., title="The user's password")

    class Config:
        schema_extra = {"example": {"email": "example@gmail.com", "password": "test"}}


class AuthReponse(BaseModel):
    access_token: str = Field(
        ..., title="The JWT access token upon user registration/login"
    )
    role: str = Field(
        ...,
        title="The role of the user. Either CUSTOMER or MERCHANT. Used for page redirection on UI.",
    )

    class Config:
        schema_extra = {
            "example": {"access_token": "[JWT ACCESS TOKEN HERE]", "role": "CUSTOMER",}
        }


class UserDet(BaseModel):
    role: str = Field(..., title="The role of the user. Either MERCHANT or CUSTOMER")
    email: str = Field(..., title="The email of the user.")
    name: str = Field(..., title="The name of the user. [FirstName LastName]")

    class Config:
        schema_extra = {
            "example": {
                "role": "MERCHANT",
                "email": "chipotle@gmail.com",
                "name": "Chipotle Store",
            }
        }


class Ongoing(BaseModel):
    hasOngoing: bool = Field(..., title="Whether or not the user has an ongoing order.")

    class Config:
        schema_extra = {"example": {"hasOngoing": False}}


class Store(BaseModel):
    id: int = Field(..., title="The ID of the store")
    name: str = Field(..., title="The name of the store")
    lat: float = Field(..., title="The latitude (coordinates) of the store")
    lng: float = Field(..., title="The longitude of the store")
    desc: str = Field(..., title="The description of the store")
    image: str = Field(..., title="The relative link to the logo of the store")
    start: str = Field(..., title="The opening hour of the store. Format: HH:MM AM/PM")
    end: str = Field(..., title="The closing hour of the store. Format: HH:MM AM/PM")

    class Config:
        schema_extra = {
            "exmaple": {
                "id": 1,
                "name": "Sample Store",
                "lat": 28.5,
                "lng": 30,
                "desc": "A sample store for testing",
                "image": "store/sample.jpg",
                "start": "08:30 AM",
                "end": "6:00 PM",
            }
        }


class StoreItem(BaseModel):
    id: int = Field(..., title="The id of the item")
    name: str = Field(..., title="The name of the item")
    price: float = Field(..., title="The price of the item")
    image: str = Field(..., title="The relative link of the item")
    description: str = Field(..., title="The description of the item")
    quantity: int = Field(
        ..., title="The amount of this item that the user has in his cart"
    )


class ItemsResp(BaseModel):
    pageCount: int = Field(..., title="The number of pages for this category")
    items: List[StoreItem]
