import json
from string import ascii_lowercase, ascii_uppercase
import random

def generate_password(event, context):

    length = event["pwd-length"]
    punctuation = ['@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '*']
    numbers = list(range(10))+list(ascii_uppercase)+list(ascii_lowercase)+list(punctuation)
    
    password=[]
    for _ in range(length):
        ele=random.choice(numbers)
        password.append(str(ele))

    random.shuffle(password)
    password="".join(password)
    
    return {"statusCode": 200, "body": json.dumps({"password":password})}

