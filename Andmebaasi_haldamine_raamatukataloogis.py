import sqlite3  #модуль для работы с базой данных SQL
from tkinter import *  #tkinter для создания графического интерфейса
from tkinter import messagebox  #модуль для вывода оконных сообщений
from tkinter import simpledialog #для вывода простых диалоговых окон

#создание и подключение к базе данных
conn = sqlite3.connect('raamatukogu.db')  #соединение с базой данных SQL
c = conn.cursor()  #объект курсор для выполнения SQL запросов

#создаем таблицы в базе данных, если их нету
c.execute('''  
CREATE TABLE IF NOT EXISTS Autorid (
    autor_id INTEGER PRIMARY KEY,
    autor_nimi TEXT NOT NULL,
    sünnikuupäev DATE NOT NULL
)''')

c.execute('''  
CREATE TABLE IF NOT EXISTS Žanrid (
    žanr_id INTEGER PRIMARY KEY,
    žanri_nimi TEXT NOT NULL
)''')

c.execute('''  
CREATE TABLE IF NOT EXISTS Raamatud (
    raamat_id INTEGER PRIMARY KEY,
    pealkiri TEXT NOT NULL,
    väljaandmise_kuupäev DATE NOT NULL,
    autor_id INTEGER,
    žanr_id INTEGER,
    FOREIGN KEY (autor_id) REFERENCES Autorid (autor_id),
    FOREIGN KEY (žanr_id) REFERENCES Žanrid (žanr_id)
)''')

conn.commit()
conn.close()

#создание графического интерфейса при помощи Tkinter
def näita_raamatuid():
    #новое окно
    uus_aken = Toplevel(bg='light blue')  #цвет фона окна
    uus_aken.title("Raamatute Nimekiri")  #заголовок окна

    
    conn = sqlite3.connect('raamatukogu.db')
    c = conn.cursor()
    c.execute(
        "SELECT Raamatud.raamat_id, Raamatud.pealkiri, Autorid.autor_nimi, Žanrid.žanri_nimi, Raamatud.väljaandmise_kuupäev FROM Raamatud JOIN Autorid ON Raamatud.autor_id = Autorid.autor_id JOIN Žanrid ON Raamatud.žanr_id = Žanrid.žanr_id")
    raamatud = c.fetchall()

    #отображение списка книг в новом окне
    for index, raamat in enumerate(raamatud):
        Label(uus_aken, text=f"{raamat[0]} | {raamat[1]} | {raamat[2]} | {raamat[3]} | {raamat[4]}", bg='light blue', fg='black').grid(row=index, column=0, sticky="w")

    conn.close()

def lisa_raamat():
    #запрос данных у пользователя
    pealkiri = simpledialog.askstring("Sisesta andmed", "Raamatu pealkiri:")
    autor = simpledialog.askstring("Sisesta andmed", "Autori nimi:")
    žanr = simpledialog.askstring("Sisesta andmed", "Žanri nimi:")
    kuupäev = simpledialog.askstring("Sisesta andmed", "Väljaandmise kuupäev:")
    #установка соединения с базой данных и добавление данных
    conn = sqlite3.connect('raamatukogu.db')
    c = conn.cursor()
    #проверка существования автора и жанра и добавление если нужно
    c.execute("SELECT autor_id FROM Autorid WHERE autor_nimi=?", (autor,))
    autor_id = c.fetchone()
    if autor_id is None:
        c.execute("INSERT INTO Autorid (autor_nimi, sünnikuupäev) VALUES (?, 'YYYY-MM-DD')", (autor,))
        autor_id = c.lastrowid
    else:
        autor_id = autor_id[0]
    c.execute("SELECT žanr_id FROM Žanrid WHERE žanri_nimi=?", (žanr,))
    žanr_id = c.fetchone()
    if žanr_id is None:
        c.execute("INSERT INTO Žanrid (žanri_nimi) VALUES (?)", (žanr,))
        žanr_id = c.lastrowid
    else:
        žanr_id = žanr_id[0]
    c.execute("INSERT INTO Raamatud (pealkiri, väljaandmise_kuupäev, autor_id, žanr_id) VALUES (?, ?, ?, ?)", (pealkiri, kuupäev, autor_id, žanr_id))
    conn.commit()
    conn.close()

def muuda_raamatut():
    raamat_id = simpledialog.askinteger("Sisesta andmed", "Raamatu ID:")
    #выбор поля для изменения
    väli = simpledialog.askstring("Sisesta andmed", "Mis välja soovid muuta? (pealkiri, autor, žanr, kuupäev)")
    uus_väärtus = simpledialog.askstring("Sisesta andmed", "Uus väärtus:")
    #установка соединения и изменение данных
    conn = sqlite3.connect('raamatukogu.db')
    c = conn.cursor()
    if väli == 'pealkiri':
        c.execute("UPDATE Raamatud SET pealkiri=? WHERE raamat_id=?", (uus_väärtus, raamat_id))
    elif väli == 'autor':
        c.execute("UPDATE Raamatud SET autor_id=(SELECT autor_id FROM Autorid WHERE autor_nimi=?) WHERE raamat_id=?", (uus_väärtus, raamat_id))
    elif väli == 'žanr':
        c.execute("UPDATE Raamatud SET žanr_id=(SELECT žanr_id FROM Žanrid WHERE žanri_nimi=?) WHERE raamat_id=?", (uus_väärtus, raamat_id))
    elif väli == 'kuupäev':
        c.execute("UPDATE Raamatud SET väljaandmise_kuupäev=? WHERE raamat_id=?", (uus_väärtus, raamat_id))
    conn.commit()
    conn.close()

def kustuta_raamat():
    #запрос выбора у пользователя
    valik = messagebox.askquestion("Kustuta raamat", "Kas soovid kustutada ühe raamatu või kõik raamatud?")
    conn = sqlite3.connect('raamatukogu.db')
    c = conn.cursor()
    if valik == 'yes':
        raamat_id = simpledialog.askinteger("Sisesta andmed", "Raamatu ID:")
        c.execute("DELETE FROM Raamatud WHERE raamat_id=?", (raamat_id,))
    else:
        c.execute("DELETE FROM Raamatud")
    conn.commit()
    conn.close()

#создание окна Tkinter
root = Tk()
root.title("Raamatukogu Kataloog")  #заголовок окна
root.configure(bg='light blue')  #цвет фона окна

#создание кнопок
nupp_näita = Button(root, text="Näita Kõiki Raamatuid", command=näita_raamatuid, bg='white', fg='black')
nupp_näita.pack()

nupp_lisa = Button(root, text="Lisa Raamat", command=lisa_raamat, bg='white', fg='black')
nupp_lisa.pack()

nupp_muuda = Button(root, text="Muuda Raamatut", command=muuda_raamatut, bg='white', fg='black')
nupp_muuda.pack()

nupp_kustuta = Button(root, text="Kustuta Raamat", command=kustuta_raamat, bg='white', fg='black')
nupp_kustuta.pack()

root.mainloop()

