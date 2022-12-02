import datetime as dt

# Função para iserir um documento de transferência no banco
def set_values(ent, db):
    user = ent['user']
    valor = ent['valor']
    dt_valor  = str(ent['dt_valor'])
    descricao = ent['descricao']
    tipo = ent['tipo']
    conta = ent['conta']
    conta_destino = ent['conta_destino']
    dt_created = str(ent['dt_created'])
    dt_updated = ''

    db.collection('registro').document().set({
        'user': user,
        'valor': valor,
        'dt_valor': dt_valor,
        'descricao': descricao,
        'tipo': tipo,
        'conta': conta,
        'conta_destino': conta_destino,
        'dt_created': dt_created,
        'dt_updated': dt_updated
    })
    
    # previne a adição de contas duplicadas
    get_conta = db.collection('conta').where('nm_conta', '==', conta).get()
    if (len(get_conta) == 0):
        db.collection('conta').document().set({
            'user': user,
            'nm_conta': conta,
            'dt_created': dt.datetime.now(),
            'dt_updated': dt.datetime.now()
        })
    get_conta_destino = db.collection('conta').where('nm_conta', '==', conta_destino).get()
    if (len(get_conta_destino) == 0):
        db.collection('conta').document().set({
            'user': user,
            'nm_conta': conta,
            'dt_created': dt.datetime.now(),
            'dt_updated': dt.datetime.now()
        })
