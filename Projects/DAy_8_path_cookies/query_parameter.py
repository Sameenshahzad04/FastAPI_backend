
#Query Parameter
#A query parameter is a key-value pair that is appended to the end of a URL after
# a question mark ?. Multiple query parameters can be included in a URL, and they are 
# separated by and sign &.

# When you declare other function parameters that are not part of the path parameters, 
# they are automatically interpreted as "query" parameters.



from typing import Annotated, Literal

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()


@app.get("/items/{item_id}")
async def read_user_item(
    item_id: str, needy: str, skip: int = 0, limit: int | None = None
):
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item

# In this case, there are 3 query parameters:

# needy, a required str.
# skip, an int with a default value of 0.
# limit, an optional int.



# ----------------------------------------------------------------------------------------------------

# Query Parameters with a Pydantic Model¶
# Declare the query parameters that you need in a Pydantic model, and then declare the parameter as Query:




# from typing import Annotated, Literal

# from fastapi import FastAPI, Query
# from pydantic import BaseModel, Field

# app = FastAPI()


class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []


@app.get("/items/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query
# Here, Query() is the key part. It tells FastAPI:

# "Hey, take all those query parameters from the URL and fill in the FilterParams blueprint with them."

# Without Query()
# FastAPI wouldn't know where to get the data from — should it come from the URL? The request body? Query() 
# makes it explicit: "from the URL query parameters."





