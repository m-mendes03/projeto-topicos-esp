from firebase_admin import auth
import google
import datetime as dt
# import pyrebase

# Função para conferir se o email está cadastrado no authentication
def check_email(ent):
    email = str(ent)
    try:
        auth.get_user_by_email(email)
        return True
    except auth.UserNotFoundError:
        return False

# Função para pegar o user uid
def user_uid(email):
    return auth.get_user_by_email(email).uid
