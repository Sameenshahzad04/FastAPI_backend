#path parameters

#they are parameters or variables that are passed in the url and
#are used to identify a specific resource or perform a specific action 
# on the server.
#type hint help in data validation, it allows you to specify the expected data type of a parameter,
#  which can help catch errors early and improve the overall reliability of your application.
from fastapi import FastAPI

from enum import Enum



app = FastAPI()

#When creating path operations, you can find situations where you have a fixed path.
# Like /users/me, let's say that it's to get data about the current user.
# And then you can also have a path /users/{user_id} to get data about a specific user by some user ID.
# Because path operations are evaluated in order, you need to make sure that the path for /users/me is declared before the one for /users/{user_id}:


@app.get("/users/me")
def read_user_me():
    return {"user_id": "the current user"}




@app.get("/users/{user_id}")
def read_item(user_id: int):
    return {"user_id": user_id}
#--------------------------------

# Predefined values
# If you have a path operation that receives a path parameter, but you want the possible valid path parameter values to be predefined, 
# you can use a standard Python Enum.

# Create an Enum class¶
# Import Enum and create a sub-class that inherits from str and from Enum.
# By inheriting from str the API docs will be able to know that the values must be of type string and will be able to render correctly.
# Then create class attributes with fixed values, which will be the available valid values:



# from enum import Enum



class Role(str, Enum):
    admin = "admin"
    Manager = "Manager"
    user = "user"


app = FastAPI()


@app.get("/users/{role}")
async def get_user(role: Role):
    if role is Role.admin:
        return {"role": role, "message": "Accessing admin panel!"}

    if role is Role.Manager:
        return {"role": role, "message": "Accessing manager panel!"}

    return {"role": role, "message": "Accessing user panel!"}
