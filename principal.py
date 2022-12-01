import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkcalendar import Calendar
import firebase_connection as fc
import datetime as dt
import json
import os
import zipfile as zip
import login
import despesa
import receita
import transferencia
import cadastrar_user
import update


def get_data(collection):
   #return db.collection(collection).order_by('dt_valor').get()
   # Retorna os registros por usuário
   return db.collection(collection).where('user', '==', str(login_ent['uid'])).get()

def get_despesas():
   return db.collection('registro').where('tipo', '==', 'Despesa').where('user', '==', str(login_ent['uid'])).get()
def get_receitas():
   return db.collection('registro').where('tipo', '==', 'Receita').where('user', '==', str(login_ent['uid'])).get()

def get_data_by_id(collection, id):
   return db.collection(collection).document(id).get()

def get_user_uid(ent):
   user = login.user_uid(str(ent['Email'].get()))
   return user

def importar_dados(collection, ent):
   db.collection(collection).document().set(ent)

def update_doc(frame, id):
   container = tk.Toplevel(frame)
   container.title('Update')
      
   reg = get_data_by_id('registro', id)
   reg = reg.to_dict()
   tipo = reg.get('tipo')

   if tipo == 'Transferência':
      campos = ('Descricao', 'Valor', 'Tipo', 'Conta', 'Conta Destino')
   else:
      campos = ('Descricao', 'Valor', 'Tipo', 'Categoria', 'Conta')

   entradas = {}
   for campo in campos:
      row = tk.Frame(container)
      tk.Label(row, width=20, text=campo+": ", anchor='w').pack(side = tk.LEFT)
      ent = tk.Entry(row)
      ent.insert(0, reg.get(campo.lower().replace(' ', '_')))
      if(campo == 'Tipo'):
         ent.config(state='readonly')
      row.pack(side = tk.TOP, fill = tk.X, padx = 5, pady = 10)
      ent.pack(side = tk.RIGHT, expand = tk.YES, fill = tk.X)
      entradas[campo] = ent

   data_valor = dt.datetime.strptime(reg.get('dt_valor'), '%Y-%m-%d')
   row_cal=tk.Frame(container)
   tk.Label(row_cal, text='Data: ', width=20, anchor='w').pack(side=tk.LEFT)
   row_cal.pack(side = tk.TOP, fill = tk.X, padx = 5, pady = 10)
   cal = Calendar(container, selectmode='day', year=data_valor.year, month=data_valor.month, day=data_valor.day, date_pattern='y-mm-dd')
   cal.pack(pady=5)
   entradas['Data'] = cal
      
   btnFrame = tk.Frame(container)
   btnFrame.pack(side=tk.TOP, fill=tk.X, expand=False, padx=15, pady=10)
   tk.Button(btnFrame, text='Atualizar', command=(lambda: entrada(tipo))).pack(side=tk.LEFT, padx=1)
   btnFrame1 = tk.Frame(container)
   btnFrame1.pack(side=tk.BOTTOM, fill=tk.X, expand=False, padx=15, pady=10)
   tk.Button(btnFrame1, text='Cancelar', command=(lambda: container.destroy())).pack(side=tk.RIGHT, padx=1)
         
   def entrada(tipo):
      if tipo == 'Transferência':
         ent = {
         'user': str(login_ent['uid']),
         'valor': str(entradas['Valor'].get()).replace(',','.'),
         'dt_valor': str(entradas['Data'].get_date()),
         'descricao': str(entradas['Descricao'].get()),
         'tipo': tipo,
         'conta': str(entradas['Conta'].get()),
         'conta_destino': str(entradas['Conta Destino'].get()),
         'dt_updated': str(dt.datetime.now())
         }
      else:
         ent = {
         'user': str(login_ent['uid']),
         'valor': str(entradas['Valor'].get()).replace(',', '.'),
         'dt_valor': str(entradas['Data'].get_date()),
         'descricao': str(entradas['Descricao'].get()),
         'tipo': tipo,
         'categoria': str(entradas['Categoria'].get()),
         'conta': str(entradas['Conta'].get()),
         'dt_updated': str(dt.datetime.now())
         }
      update.update_values(db, ent, id)
      messagebox.showinfo(tipo, tipo + ' atualizada.')
      container.destroy()


def show_data_toplevel(frame, dados):
   win = tk.Toplevel(frame)
   win.geometry("670x400")
   win.title("Dados importados")
   win.grid_rowconfigure(0, weight=1)
   win.grid_columnconfigure(0, weight=1)
   win.grid_propagate(False)

   canvas = tk.Canvas(win)
   canvas.grid(row=0, column=0, sticky=tk.NSEW)
   scroll = tk.Scrollbar(win, orient=tk.VERTICAL, command=canvas.yview)
   scroll.grid(row=0, column=1, sticky=tk.NS)
   canvas.config(yscrollcommand=scroll.set)
   container = tk.Frame(canvas, width=100, height=80)
   canvas.create_window((0,0), window=container, anchor=tk.NW)
      
   for i, dado in enumerate(dados):
      txt = tk.Text(container, height=5, width=80, pady=5)
      ins = dict(dado)
      txt.insert(tk.INSERT, ins)
      txt.config(state='disabled')
      txt.grid(row=i, column=0)
   container.update_idletasks()
   canvas.config(scrollregion=canvas.bbox(tk.ALL))

global login_ent
login_ent = {}
# Tela de login
class LoginPage(tk.Frame):
   def __init__(self, parent, controller, *args, **kwargs):
      tk.Frame.__init__(self, parent, *args, **kwargs)
      
      def fazer_login():
         if login.check_email(str(login_ent['Email'].get())):
            login_ent['uid'] = get_user_uid(login_ent)
            controller.maisframes(parent)
            controller.show(HomePage)
         else:
            messagebox.showerror('Erro', 'Usuário não existe.')

      campos = ('Email', 'Senha')
      for campo in campos:
         row = tk.Frame(self)
         tk.Label(row, width=20, text=campo+": ", anchor='w').pack(side = tk.LEFT)
         row.pack(side = tk.TOP, fill = tk.X, padx = 5, pady = 10)
         ent = tk.Entry(row)
         ent.pack(side = tk.RIGHT, expand = tk.YES, fill = tk.X)
         if campo == 'Senha':
            ent.configure(fg='black',show='*')
         login_ent[campo] = ent

      btnFrame = tk.Frame(self)
      btnFrame.pack(side=tk.TOP, fill=tk.X, expand=False, padx=15, pady=10)
      tk.Button(btnFrame, text='Fazer login', command=(lambda: fazer_login())).pack(side=tk.LEFT, padx=1)
      tk.Button(btnFrame, text='Fazer cadastro', command=(lambda: controller.show(CadastroPage))).pack(side=tk.RIGHT, padx=1)

# Tela de cadastro
class CadastroPage(tk.Frame):
   def __init__(self, parent, controller, *args, **kwargs):
      tk.Frame.__init__(self, parent, *args, **kwargs)
      
      def criar_user():
         ent = {
            'nome': str(entradas['Nome'].get()),
            'email': str(entradas['Email'].get()),
            'senha': str(entradas['Senha'].get())
         }
         if cadastrar_user.create_user(db, ent):
            messagebox.showinfo('Cadastro', 'Usuário cadastrado com sucesso.')
            controller.show(LoginPage)
         else:
            messagebox.showerror('Cadastro', 'Erro ao cadastrar.')

      campos = ('Nome', 'Email', 'Senha')
      entradas = {}
      for campo in campos:
         row = tk.Frame(self)
         tk.Label(row, width=22, text=campo+": ", anchor='w').pack(side = tk.LEFT)
         ent = tk.Entry(row)
         row.pack(side = tk.TOP, fill = tk.X, padx = 5, pady = 10)
         ent.pack(side = tk.RIGHT, expand = tk.YES, fill = tk.X)
         if campo == 'Senha':
            ent.configure(fg='black',show='*')
         entradas[campo] = ent

      btnFrame = tk.Frame(self)
      btnFrame.pack(side=tk.TOP, fill=tk.X, expand=False, padx=15, pady=10)
      tk.Button(btnFrame, text='Cadastrar', command=(lambda: criar_user())).pack(side=tk.LEFT, padx=1)
      tk.Button(btnFrame, text='Sair', command=(lambda: main.quit())).pack(side=tk.RIGHT, padx=1)
      tk.Button(btnFrame, text='Cancelar', command=(lambda: controller.show(LoginPage))).pack(side=tk.RIGHT, padx=1)

# Tela home
class HomePage(tk.Frame):
   def __init__(self, parent, controller, *args, **kwargs):
      tk.Frame.__init__(self, parent, *args, **kwargs)

      despesas = get_despesas()
      despesas_sum = round(sum(map(lambda d: round(float(d.get('valor')), 2), despesas)),2)
      receitas = get_receitas()
      receitas_sum = round(sum(map(lambda r: round(float(r.get('valor')), 2), receitas)),2)
      total = round((receitas_sum - despesas_sum),2)

      row = tk.Frame(self)
      row.pack(side=tk.TOP, expand=False, fill=tk.X, pady=5, padx=5)
      tk.Label(row, width=30, text="DESPESA: "+  str(despesas_sum), anchor='w', justify=tk.CENTER, font=30, height=5).pack(side = tk.LEFT, padx=10)
      row1 = tk.Frame(self)
      row1.pack(side=tk.TOP, expand=False, fill=tk.X, pady=5, padx=5)
      tk.Label(row1, width=30, text="RECEITA: "+ str(receitas_sum), anchor='w', justify=tk.CENTER, font=30, height=5).pack(side = tk.LEFT, padx=10)
      row2 = tk.Frame(self)
      row2.pack(side=tk.TOP, expand=False, fill=tk.X, pady=5, padx=5)
      tk.Label(row2, width=30, text="TOTAL: "+ str(total), anchor='w', justify=tk.CENTER, font=30, height=5).pack(side = tk.LEFT, padx=10)

      btnFrame = tk.Frame(self)
      btnFrame.pack(side=tk.BOTTOM, fill=tk.X, expand=False, padx=15, pady=10)
      tk.Button(btnFrame, text='Extrato', command=(lambda: controller.show(ExtratoPage))).pack(side=tk.LEFT, padx=1)
      tk.Button(btnFrame, text='Despesa', fg='red', command=(lambda: controller.show(DespesaPage))).pack(side=tk.LEFT, padx=1)
      tk.Button(btnFrame, text='Receita', fg='green', command=(lambda: controller.show(ReceitaPage))).pack(side=tk.LEFT, padx=1)
      tk.Button(btnFrame, text='Transferência', fg='blue', command=(lambda: controller.show(TransferPage))).pack(side=tk.LEFT, padx=1)

# Tela de inserção de despesa
class DespesaPage(tk.Frame):
   def __init__(self, parent, controller, *args, **kwargs):
      tk.Frame.__init__(self, parent, *args, **kwargs)
      
      def entrada():
         ent = {
         'user': str(login_ent['uid']),
         'valor': str(entradas['Valor'].get()).replace(',', '.'),
         'dt_valor': str(entradas['Data'].get_date()),
         'descricao': str(entradas['Descricao'].get()),
         'tipo': 'Despesa',
         'categoria': str(entradas['Categoria'].get()),
         'conta': str(entradas['Conta'].get()),
         'dt_created': str(dt.datetime.now()),
         'dt_updated': str(dt.datetime.now())
         }
         despesa.set_values(ent, db)
         messagebox.showinfo('Despesa', 'Despesa inserida.')
         controller.show(HomePage)

      campos = ('Descricao', 'Valor', 'Categoria', 'Conta')
      entradas = {}
      for campo in campos:
         row = tk.Frame(self)
         tk.Label(row, width=20, text=campo+": ", anchor='w').pack(side = tk.LEFT)
         ent = tk.Entry(row)
         row.pack(side = tk.TOP, fill = tk.X, padx = 5, pady = 10)
         ent.pack(side = tk.RIGHT, expand = tk.YES, fill = tk.X)
         entradas[campo] = ent
      
      row_des=tk.Frame(self)
      tk.Label(row_des, text= 'Tipo: ', width=20, anchor='w').pack(side=tk.LEFT)
      ent_des = tk.Entry(row_des)
      row_des.pack(side = tk.TOP, fill = tk.X, padx = 5, pady = 10)
      ent_des.insert(0, "Despesa")
      ent_des.config(state='readonly')
      ent_des.pack(side = tk.RIGHT, expand = tk.YES, fill = tk.X)
      entradas['Tipo'] = ent_des

      row_cal=tk.Frame(self)
      tk.Label(row_cal, text='Data: ', width=20, anchor='w').pack(side=tk.LEFT)
      row_cal.pack(side = tk.TOP, fill = tk.X, padx = 5, pady = 10)
      cal = Calendar(self, selectmode='day', year=dt.date.today().year, month=dt.date.today().month, day=dt.date.today().day, date_pattern='y-mm-dd')
      cal.pack(pady=5)
      entradas['Data'] = cal
      
      btnFrame = tk.Frame(self)
      btnFrame.pack(side=tk.TOP, fill=tk.X, expand=False, padx=15, pady=10)
      tk.Button(btnFrame, text='Inserir Despesa', command=(lambda: entrada())).pack(side=tk.LEFT, padx=1)
      btnFrame1 = tk.Frame(self)
      btnFrame1.pack(side=tk.BOTTOM, fill=tk.X, expand=False, padx=15, pady=10)
      tk.Button(btnFrame1, text='Voltar para Home', command=(lambda: controller.show(HomePage))).pack(side=tk.RIGHT, padx=1)

# Tela de inserção de receita
class ReceitaPage(tk.Frame):
   def __init__(self, parent, controller, *args, **kwargs):
      tk.Frame.__init__(self, parent, *args, **kwargs)

      def entrada():
         ent = {
         'user': str(login_ent['uid']),
         'valor': str(entradas['Valor'].get()).replace(',','.'),
         'dt_valor': str(entradas['Data'].get_date()),
         'descricao': str(entradas['Descricao'].get()),
         'tipo': 'Receita',
         'categoria': str(entradas['Categoria'].get()),
         'conta': str(entradas['Conta'].get()),
         'dt_created': str(dt.datetime.now()),
         'dt_updated': str(dt.datetime.now())
         }
         receita.set_values(ent, db)
         messagebox.showinfo('Receita', 'Receita inserida.')
         controller.show(HomePage)

      campos = ('Descricao', 'Valor', 'Categoria', 'Conta')
      entradas = {}
      for campo in campos:
         row = tk.Frame(self)
         tk.Label(row, width=20, text=campo+": ", anchor='w').pack(side = tk.LEFT)
         ent = tk.Entry(row)
         row.pack(side = tk.TOP, fill = tk.X, padx = 5, pady = 10)
         ent.pack(side = tk.RIGHT, expand = tk.YES, fill = tk.X)
         entradas[campo] = ent
      
      row_des=tk.Frame(self)
      tk.Label(row_des, text= 'Tipo: ', width=20, anchor='w').pack(side=tk.LEFT)
      ent_des = tk.Entry(row_des)
      row_des.pack(side = tk.TOP, fill = tk.X, padx = 5, pady = 10)
      ent_des.insert(0, "Receita")
      ent_des.config(state='readonly')
      ent_des.pack(side = tk.RIGHT, expand = tk.YES, fill = tk.X)
      entradas['Tipo'] = ent_des

      row_cal=tk.Frame(self)
      tk.Label(row_cal, text='Data: ', width=20, anchor='w').pack(side=tk.LEFT)
      row_cal.pack(side = tk.TOP, fill = tk.X, padx = 5, pady = 10)
      cal = Calendar(self, selectmode='day', year=dt.date.today().year, month=dt.date.today().month, day=dt.date.today().day, date_pattern='y-mm-dd')
      cal.pack(pady=5)
      entradas['Data'] = cal
      
      btnFrame = tk.Frame(self)
      btnFrame.pack(side=tk.TOP, fill=tk.X, expand=False, padx=15, pady=10)
      tk.Button(btnFrame, text='Inserir Receita', command=(lambda: entrada())).pack(side=tk.LEFT, padx=1)
      btnFrame1 = tk.Frame(self)
      btnFrame1.pack(side=tk.BOTTOM, fill=tk.X, expand=False, padx=15, pady=10)
      tk.Button(btnFrame1, text='Voltar para Home', command=(lambda: controller.show(HomePage))).pack(side=tk.RIGHT, padx=1)      

# Tela de inserção de transferência
class TransferPage(tk.Frame):
   def __init__(self, parent, controller, *args, **kwargs):
      tk.Frame.__init__(self, parent, *args, **kwargs)

      def entrada():
         ent = {
         'user': str(login_ent['uid']),
         'valor': str(entradas['Valor'].get()).replace(',','.'),
         'dt_valor': str(entradas['Data'].get_date()),
         'descricao': str(entradas['Descricao'].get()),
         'tipo': 'Transferência',
         'conta': str(entradas['Conta'].get()),
         'conta_destino': str(entradas['Conta Destino'].get()),
         'dt_created': str(dt.datetime.now()),
         'dt_updated': str(dt.datetime.now())
         }
         transferencia.set_values(ent, db)
         messagebox.showinfo('Transferência', 'Transferência inserida.')
         controller.show(HomePage)

      campos = ('Descricao', 'Valor', 'Conta', 'Conta Destino')
      entradas = {}
      for campo in campos:
         row = tk.Frame(self)
         tk.Label(row, width=20, text=campo+": ", anchor='w').pack(side = tk.LEFT)
         row.pack(side = tk.TOP, fill = tk.X, padx = 5, pady = 10)
         ent = tk.Entry(row)
         ent.pack(side = tk.RIGHT, expand = tk.YES, fill = tk.X)
         entradas[campo] = ent
      
      row_des=tk.Frame(self)
      tk.Label(row_des, text= 'Tipo: ', width=20, anchor='w').pack(side=tk.LEFT)
      ent_des = tk.Entry(row_des)
      row_des.pack(side = tk.TOP, fill = tk.X, padx = 5, pady = 10)
      ent_des.insert(0, "Transferência")
      ent_des.config(state='readonly')
      ent_des.pack(side = tk.RIGHT, expand = tk.YES, fill = tk.X)
      entradas['Tipo'] = ent_des

      row_cal=tk.Frame(self)
      tk.Label(row_cal, text='Data: ', width=20, anchor='w').pack(side=tk.LEFT)
      row_cal.pack(side = tk.TOP, fill = tk.X, padx = 5, pady = 10)
      cal = Calendar(self, selectmode='day', year=dt.date.today().year, month=dt.date.today().month, day=dt.date.today().day, date_pattern='y-mm-dd')
      cal.pack(pady=20)
      entradas['Data'] = cal
      
      btnFrame = tk.Frame(self)
      btnFrame.pack(side=tk.TOP, fill=tk.X, expand=False, padx=15, pady=10)
      tk.Button(btnFrame, text='Inserir Transferência', command=(lambda: entrada())).pack(side=tk.LEFT, padx=1)
      btnFrame1 = tk.Frame(self)
      btnFrame1.pack(side=tk.BOTTOM, fill=tk.X, expand=False, padx=15, pady=10)
      tk.Button(btnFrame1, text='Voltar para Home', command=(lambda: controller.show(HomePage))).pack(side=tk.RIGHT, padx=1)

# Tela de inserção de transferência
class ExportarDadosPage(tk.Frame):
   def __init__(self, parent, controller, *args, **kwargs):
      tk.Frame.__init__(self, parent, *args, **kwargs)
      
      def exportar():
         dados = get_data('registro')
         dados_lista = []
         for dado in dados:
            dados_lista.append(dado.to_dict())

         dirname = filedialog.askdirectory(initialdir='/', title='Selecione a pasta')
         fname = '/relatorio_' + str(dt.datetime.strftime(dt.datetime.now(), '%Y%m%d%H%M%S')) + '.json'
         fpath = dirname + fname
         with open(fpath, 'w') as arq:
            json.dump(dados_lista, arq, indent=4)
         
         zname = dirname + '/relatorio_' + str(dt.datetime.strftime(dt.datetime.now(), '%Y%m%d%H%M%S')) + '.zip'
         zf = zip.ZipFile(zname, 'w')
         zf.write(filename=fpath, arcname=fname)
         zf.close()

         os.remove(fpath)
         messagebox.showinfo('Exportação', 'Dados exportados.')

      row=tk.Frame(self)
      tk.Label(row, text= 'Exportar dados do app.', width=40, anchor='w').pack(side=tk.LEFT)
      row.pack(side = tk.TOP, fill = tk.X, padx = 5, pady = 10)

      btnFrame = tk.Frame(row)
      btnFrame.pack(side=tk.TOP, fill=tk.X, expand=False, padx=15, pady=10)
      tk.Button(btnFrame, text='Exportar', command=(lambda: exportar())).pack(side=tk.LEFT, padx=1)
      btnFrame1 = tk.Frame(self)
      btnFrame1.pack(side=tk.BOTTOM, fill=tk.X, expand=False, padx=15, pady=10)
      tk.Button(btnFrame1, text='Voltar para Home', command=(lambda: controller.show(HomePage))).pack(side=tk.RIGHT, padx=1)

# Tela Extrato
class ExtratoPage(tk.Frame):
   def __init__(self, parent, controller, *args, **kwargs):
      tk.Frame.__init__(self, parent, *args, **kwargs)
      
      def deletar_registro(id):
         db.collection('registro').document(id).delete()
         messagebox.showinfo('Deletar registro', 'Registro deletado.')

      # REFRESH DATA

      self.grid_rowconfigure(0, weight=1)
      self.grid_columnconfigure(0, weight=1)
      self.grid_propagate(False)
      canvas = tk.Canvas(self)
      canvas.grid(row=0, column=0, sticky=tk.NSEW)
      scroll = tk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
      scroll.grid(row=0, column=3, sticky=tk.NS)
      canvas.config(yscrollcommand=scroll.set)
      container = tk.Frame(canvas, width=100, height=80)
      canvas.create_window((0,0), window=container, anchor=tk.NW)

      dados = get_data('registro')
      for i, dado in enumerate(dados):
         txt = tk.Text(container, height=5, width=80, pady=5)
         ins = dado.to_dict().get('descricao')+'\nValor:\t'+dado.to_dict().get('valor')+'\nData:\t'+dado.to_dict().get('dt_valor')+'\nTipo: '+dado.to_dict().get('tipo')
         txt.insert(tk.INSERT, ins)
         txt.config(state='disabled')
         txt.grid(row=i, column=0)
         tk.Button(container, text='Ver', command=(lambda d=dado: update_doc(self, d.id))).grid(row=i, column=1)
         tk.Button(container,  text='Deletar', command=(lambda d=dado: deletar_registro(d.id))).grid(row=i, column=2)
      container.update_idletasks()
      canvas.config(scrollregion=canvas.bbox(tk.ALL))

# Tela Dados Importados
class ImportsPage(tk.Frame):
   def __init__(self, parent, controller, *args, **kwargs):
      tk.Frame.__init__(self, parent, *args, **kwargs)
      self.grid_rowconfigure(0, weight=1)
      self.grid_columnconfigure(0, weight=1)
      self.grid_propagate(False)
      
      canvas = tk.Canvas(self)
      canvas.grid(row=0, column=0, sticky=tk.NSEW)
      scroll = tk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
      scroll.grid(row=0, column=3, sticky=tk.NS)
      canvas.config(yscrollcommand=scroll.set)
      container = tk.Frame(canvas, width=100, height=80)
      canvas.create_window((0,0), window=container, anchor=tk.NW)
      dados = get_data('import')
      for i, dado in enumerate(dados):
         txt = tk.Text(container, height=10, width=50, pady=5, padx=10)
         ins = ''
         for key, value in dado.to_dict().items():
            ins = ins + f"{key}: {value}\n"
         txt.insert(tk.INSERT, ins)
         txt.config(state='disabled')
         txt.grid(row=i, column=0)

      container.update_idletasks()
      canvas.config(scrollregion=canvas.bbox(tk.ALL))

# Tela Sobre
class AboutPage(tk.Frame):
   def __init__(self, parent, controller, *args, **kwargs):
      tk.Frame.__init__(self, parent, *args, **kwargs)
      
      about = "SOBRE O APP:\n\nDesenvolvido por alunos de ADS para a disciplina de Tópicos Especiais em Informática da FATEC Ribeirão Preto.\nO aplicativo foi desenvolvido em Pyhton, com interface do Tkinter.\nO banco de dados utilizado é o Firestore."
      tk.Label(self, text=about).pack(side=tk.TOP, fill=tk.BOTH, padx=5, pady=5, expand=True)
      devs = "DEVS:\n\nMarina Mendes\nThiago Martins Menegusso"
      tk.Label(self, text=devs).pack(side=tk.TOP, fill=tk.BOTH, padx=5, pady=5, expand=True)
      tk.Button(self, text='Voltar', command=(lambda: self.lower())).pack(side=tk.BOTTOM, padx=10, pady=5)

# Tela Importar Dados
class ImportarDadosPage(tk.Frame):
   def __init__(self, parent, controller, *args, **kwargs):
      tk.Frame.__init__(self, parent, *args, **kwargs)

      def importar():
         try:
            fname = filedialog.askopenfilename(initialdir='/', title='Selecione o arquivo', filetypes = (("Json","*.json*"), ("All Files", "*.*")))
            file = []
            with open(fname, 'r') as arq:
               doc = json.load(arq)
               file.extend(doc)
            for f in file:
               imp = dict(f)
               imp['user'] = str(login_ent['uid'])
               importar_dados('import', imp)
            show_data_toplevel(self, file)
            messagebox.showinfo('Importação', 'Dados Importados.')
         except json.decoder.JSONDecodeError:
            messagebox.showerror('Erro', 'Formato de arquivo não suportado.')

      row=tk.Frame(self)
      tk.Label(row, text= 'Importar dados para o app.', width=40, anchor='w').pack(side=tk.LEFT)
      row.pack(side = tk.TOP, fill = tk.X, padx = 5, pady = 10)

      btnFrame = tk.Frame(row)
      btnFrame.pack(side=tk.TOP, fill=tk.X, expand=False, padx=15, pady=10)
      tk.Button(btnFrame, text='Importar', command=(lambda: importar())).pack(side=tk.LEFT, padx=1)

      btnFrame1 = tk.Frame(self)
      btnFrame1.pack(side=tk.BOTTOM, fill=tk.X, expand=False, padx=15, pady=10)
      tk.Button(btnFrame1, text='Voltar para Home', command=(lambda: controller.show(HomePage))).pack(side=tk.RIGHT, padx=1)

# Tela principal
class MainPage(tk.Tk):
   def __init__(self, *args, **kwargs):
      tk.Tk.__init__(self, *args, **kwargs)
      self.title('Aplicativo')
      self.geometry('800x600')

      self.menu = tk.Menu(self)
      self.files = tk.Menu(self.menu, tearoff=0)
      self.files.add_command(label='Importar dados', state='disable', command=(lambda: self.show(ImportarDadosPage)))
      self.files.add_command(label='Exportar dados', state='disable', command=(lambda: self.show(ExportarDadosPage)))
      self.files.add_command(label='Sair', command=(lambda: self.quit()))
      self.menu.add_cascade(label='File', menu=self.files)
      views = tk.Menu(self.menu, tearoff=0)
      views.add_command(label='Home', command=(lambda: self.show(HomePage)))
      views.add_command(label='Extrato', command=(lambda: self.show(ExtratoPage)))
      views.add_command(label='Dados importados', command=(lambda: self.show(ImportsPage)))
      self.menu.add_cascade(label='Ver', state='disable', menu=views)
      registros = tk.Menu(self.menu, tearoff=0)
      registros.add_command(label='Despesa', command=(lambda: self.show(DespesaPage)))
      registros.add_command(label='Receita', command=(lambda: self.show(ReceitaPage)))
      registros.add_command(label='Transferência', command=(lambda: self.show(TransferPage)))
      self.menu.add_cascade(label='Inserir', state='disable', menu=registros)
      help = tk.Menu(self.menu, tearoff=0)
      help.add_command(label='Sobre', command=(lambda: self.show(AboutPage)))
      self.menu.add_cascade(label='Help', menu=help)
      self.config(menu=self.menu)

      container = tk.Frame(self)
      container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
      container.grid_rowconfigure(0, weight=1)
      container.grid_columnconfigure(0, weight=1)
      self.frames = {}
      for f in (LoginPage, CadastroPage, AboutPage):
         frame = f(container, self)
         self.frames[f] = frame
      
      self.show(LoginPage)

   def show(self, cont):
      frame = self.frames[cont]
      frame.grid(row=0, column=0, sticky=tk.NSEW)
      frame.tkraise()
   def maisframes(self, container):
      for f in (HomePage, DespesaPage, ReceitaPage, TransferPage, ExtratoPage, ExportarDadosPage, ImportarDadosPage, ImportsPage):
         frame = f(container, self)
         self.frames[f] = frame
      self.files.entryconfig(0, state='normal')
      self.files.entryconfig(1, state='normal')
      self.menu.entryconfig(2, state='normal')
      self.menu.entryconfig(3, state='normal')

global app_firebase
global db
app_firebase = fc.Firestore_Connection.firebase_initialize()
db = fc.Firestore_Connection.firestore_client(app_firebase)

main = MainPage()

main.mainloop()
