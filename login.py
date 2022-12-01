from firebase_admin import auth
import google
import datetime as dt
# import pyrebase

def check_email(ent):
    email = str(ent)
    
    try:
        auth.get_user_by_email(email)
        return True
    except auth.UserNotFoundError:
        return False

def user_uid(email):
    return auth.get_user_by_email(email).uid
