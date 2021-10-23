import mysql.connector
import traceback
import time

BD_PASS = 'Shaman34#'
mydb = None

def abrir_conexao():
    global mydb
    mydb = mysql.connector.connect(user='root', password=BD_PASS,host='127.0.0.1', database='manga')

def fechar_conexao():
    mydb.close()

def buscar_mangas():
    c = mydb.cursor(dictionary=True)
    c.execute("select id, idTenmanga, url from manga", ())
    r = c.fetchall()
    return r

def salvar_capitulo(idManga, titulo, url):
    c = mydb.cursor(dictionary=True)
    c.execute("insert into capitulo(manga_id, titulo, url, data) values(%s, %s, %s, CURRENT_TIMESTAMP()) ", 
                (idManga, titulo, url))
    mydb.commit()

def run():
	pass

while True:
    try:
        abrir_conexao()
        run()
        fechar_conexao()
    except:
        print("Erro aconteceu: ", traceback.format_exc())

    time.sleep(5 * 60)