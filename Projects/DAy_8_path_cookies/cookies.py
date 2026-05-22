


# Cookie Parameters

# You can define Cookie parameters the same way you define Query and Path parameters.
# First import Cookie:

#You can define the default value as well as all the extra validation or annotation parametersjust like Query(),path()

# To declare cookies, you need to use Cookie, because otherwise the parameters would be interpreted as query parameters

# like this:
# 
# def read_items(ads_id: Annotated[str | None, Cookie()] = None)

from pydantic import BaseModel
from typing import Annotated

from fastapi import Cookie, FastAPI,Header

app = FastAPI()


@app.get("/items/")
def read_items(ads_id: Annotated[str | None, Cookie()] = None):
    return {"ads_id": ads_id}


# Header() tells FastAPI "get this data from the request headers".

# HTTP headers are extra pieces of information sent alongside a request — things like:

# (what browser/client is being used)
# Authorization (authentication tokens)
# X-Token (custom tokens)

from typing import Annotated



app = FastAPI()


@app.get("/items/")
def read_items(user_agent: Annotated[str | None, Header()] = None):
    return {"User-Agent": user_agent}





# Cookies with a Pydantic Model
# Declare the cookie parameters that you need in a Pydantic model, and then declare the parameter as cookies




class Cookies(BaseModel):
    session_id: str
    fatebook_tracker: str | None = None
    googall_tracker: str | None = None


@app.get("/items/")
def read_items(cookies: Annotated[Cookies, Cookie()]):
    return cookies

























































































