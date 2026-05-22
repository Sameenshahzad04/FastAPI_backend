# # Request Body

# When you need to send data from a client (let's say, a browser) to your API, you send it as a request body.
# A request body is data sent by the client to your API. A response body is the data your API sends to the client.
# Your API almost always has to send a response body. But clients don't necessarily need to send request bodies all
#  the time, sometimes they only request a path, maybe with some query parameters, but don't send a body.
# To declare a request body, you use Pydantic models with all their power and benefits.




import random
from fastapi import FastAPI, Query,Body
from pydantic import BaseModel,AfterValidator, Field

from typing import Annotated

class user(BaseModel):
    
    name: str
    email: str
    password: str

app = FastAPI()


@app.post("/users/")
def create_user(user: user):
    return user

# -----------------------------------------------------
# Query Parameters and String Validations¶


#  we can make the q query parameter required just by not declaring a default value, like:
# q: str
#this is now required query parameter, and if you try to call /items/ without providing a value for q, you'll get an error.


# The query parameter q is of type str | None, 
# that means that it's of type str but could also be None, and indeed, the default value is None, so FastAPI will know it's not required.
# We are going to enforce that even though q is optional, whenever it is provided, its length doesn't exceed 50 characters.

# To achieve that, first import:

# Query from fastapi
# Annotated from typing



# from typing import Annotated

# from fastapi import FastAPI, Query

# app = FastAPI()




# @app.get("/items/")
#
# def read_items(q: str | None = None):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results


@app.get("/users/")
def show_user(
    email: Annotated[str | None, Query(min_length=3, max_length=8)] = None,
):
    results = { "users": [{"user_id": "504"}, {"name": "sam"}] }
    if email:
        results.update({"email": email})
    return results

    # We had this type annotation:


    # q: str | None = None
    # What we will do is wrap that with Annotated, so it becomes:
    # q: Annotated[str | None] = None


# ------------------------------------------------------------------------

# Custom Validation¶
# There could be cases where you need to do some custom validation that can't be done with the parameters shown above.

# In those cases, you can use a custom validator function that is applied after the normal validation (e.g. after validating that the value is a str).

# You can achieve that using Pydantic's AfterValidator inside of Annotated.

# import random
# from typing import Annotated

# from fastapi import FastAPI
# from pydantic import AfterValidator

# app = FastAPI()

data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}


def check_valid_id(id: str):
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id


@app.get("/items/")
def read_items(
    id: Annotated[str | None, AfterValidator(check_valid_id)] = None,
):
    if id:
        item = data.get(id)
    else:
        id, item = random.choice(list(data.items()))
    return {"id": id, "name": item}








# Body - Fields
# The same way you can declare additional validation
# and metadata in path operation function parameters with Query, Path and Body,
# you can declare validation and metadata inside of Pydantic models using Pydantic's Field.

  
class Projectfind(BaseModel):
    #id :int
    name:str=Field(...,min_length=3)
    des :str=Field(...,min_length=3) 

# Nested Models
# Each attribute of a Pydantic model has a type.

# But that type can itself be another Pydantic model.

# So, you can declare deeply nested JSON "objects" with specific attribute names, types and validations.

# All that, arbitrarily nested.

# Define a submodel¶
# For example, we can define an Image model:





class Image(BaseModel):
    url: str
    name: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results


# --------------------------------------------------
# Declare Request Example Data¶
# You can declare examples of the data your app can receive.

# Here are several ways to do it.


#******* 1: Declare an example in the Body() of the parameter:







# from typing import Annotated

# from fastapi import Body, FastAPI
# from pydantic import BaseModel

# app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Annotated[
        Item,
        Body(
            examples=[
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ],
        ),
    ],
):
    results = {"item_id": item_id, "item": item}
    return results

# ***********2 : Declare an example in the Config of the Pydantic model:


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ]
        }
    }


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results

# ******3 :Field additional arguments ,When using Field() with Pydantic models, you can also declare additional examples:


from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class Item(BaseModel):
    name: str = Field(examples=["Foo"])
    description: str | None = Field(default=None, examples=["A very nice Item"])
    price: float = Field(examples=[35.4])
    tax: float | None = Field(default=None, examples=[3.2])


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results





















