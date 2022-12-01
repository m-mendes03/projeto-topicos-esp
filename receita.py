import datetime as dt

def set_values(ent, db):
    user = ent['user']
    valor = ent['valor']
    dt_valor  = str(ent['dt_valor'])
    descricao = ent['descricao']
    tipo = ent['tipo']
    categoria = ent['categoria']
    conta = ent['conta']
    dt_created = str(ent['dt_created'])
    dt_updated = ''

    db.collection('registro').document().set({
        'user': user,
        'valor': valor,
        'dt_valor': dt_valor,
        'descricao': descricao,
        'tipo': tipo,
        'categoria': categoria,
        'conta': conta,
        'dt_created': dt_created,
        'dt_updated': dt_updated
    })

    get_categoria = db.collection('categoria').where('nm_categoria', '==', categoria).get()
    if (len(get_categoria) == 0):
        db.collection('categoria').document().set({
            'user': user,
            'nm_categoria': categoria,
            'dt_created': dt.datetime.now(),
            'dt_updated': dt.datetime.now()
        })

    get_conta = db.collection('conta').where('nm_conta', '==', conta).get()
    if (len(get_conta) == 0):
        db.collection('conta').document().set({
            'user': user,
            'nm_conta': conta,
            'dt_created': dt.datetime.now(),
            'dt_updated': dt.datetime.now()
        })
