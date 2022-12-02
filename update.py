import datetime as dt

# Função para atualizar os valores de um documento no banco
def update_values(db, ent, id):
    dit = {}
    for key, value in ent.items():
        dit[key.lower()] = value
    user = ent['user']
    if ent['tipo']=='Transferência':
        conta = ent['conta']
        conta_destino = ent['conta_destino']
    else:
        categoria = ent['categoria']
        conta = ent['conta']

    # previne a adição de categorias e contas duplicadas diferenciando transferência de despesa e receita
    db.collection('registro').document(id).update(dit)
    get_conta = db.collection('conta').where('nm_conta', '==', conta).get()
    if (len(get_conta) == 0):
        db.collection('conta').document().set({
            'user': user,
            'nm_conta': conta,
            'dt_created': dt.datetime.now(),
            'dt_updated': dt.datetime.now()
        })
    if ent['tipo'] == 'Transferência':
        get_conta_destino = db.collection('conta').where('nm_conta', '==', conta_destino).get()
        if (len(get_conta_destino) == 0):
            db.collection('conta').document().set({
                'user': user,
                'nm_conta': conta,
                'dt_created': dt.datetime.now(),
                'dt_updated': dt.datetime.now()
            })
    else:
        get_categoria = db.collection('categoria').where('nm_categoria', '==', categoria).get()
        if (len(get_categoria) == 0):
            db.collection('categoria').document().set({
                'user': user,
                'nm_categoria': categoria,
                'dt_created': dt.datetime.now(),
                'dt_updated': dt.datetime.now()
            })
