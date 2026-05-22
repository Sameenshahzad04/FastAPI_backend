# utils/cache.py

from config.redis_config import redis_client
import json


#get data from cache
def cache_get(key):
   
    if redis_client is None:
        return None
    
    value = redis_client.get(key)
    if value:
        try:
            return json.loads(value)    #it convert json string to python object like dict,list
        except:
            return value
    return None


#set data to cache with expiration time (default 1 hour)
#setx means set with expiration time
#set means set without expiration time this is used for session management where we want to keep data until user logs out or session expires,but for 1000 user data it will consume more ram memory and can get crashed 

def cache_set(key, value, expire_seconds=3600):
   
    if redis_client is None:
        return False
    
    serialized = json.dumps(value)      #it convert python object to json string
    redis_client.setex(key, expire_seconds, serialized)
    return True


# Delete data  from cache
def cache_delete(key):
    
    if redis_client is None:
        return False
    
    redis_client.delete(key)
    return True
