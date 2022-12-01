from firebase_admin import auth
import google
import datetime as dt

def create_user(db, ent):

    email = ent['email']
    password = ent['senha']
    nome = ent['nome']

    try:
        user = auth.create_user(email=email, password=password)
        db.collection('user').document().set({
            'email': email,
            'nome': nome,
            'user_id': user.uid,
            'dt_created': dt.datetime.now()
        })
        return True
    except auth.EmailAlreadyExistsError as msg:
        print(msg)
        return False
    except ValueError as msg:
        print(msg)
        return False
