"""Install the portfolio schema into an empty DB and add fictional demonstration data."""
from pathlib import Path
import argparse
import db

def install():
    with db.transaction() as cur:
        cur.execute("SELECT count(*) AS n FROM information_schema.tables WHERE table_schema='public'")
        if cur.fetchone()['n']:
            raise RuntimeError('Database is not empty. Refusing to overwrite existing data.')
        cur.execute(Path(__file__).with_name('database').joinpath('schema.sql').read_text(encoding='utf-8'))
        for login, password, admin in [('demo','DemoPass2026',False),('admin','AdminPass2026',True)]:
            cur.execute('INSERT INTO "Clients" ("Login","Password","is_admin") VALUES (%s,%s,%s)',
                        (login,db.password_hash(password),admin))
        cur.execute('''INSERT INTO "Theaters" ("Title","Contact_phone","Address","Number_of_halls")
          VALUES ('Учебный театр','+0 000 000-00-00','Демонстрационный адрес, 1',1) RETURNING "ID_Theater"''')
        theater=cur.fetchone()['ID_Theater']
        for name, genre, duration in [('Вечер комедии','Комедия',100),('Городские истории','Драма',120),('Музыкальная прогулка','Мюзикл',90)]:
            cur.execute('''INSERT INTO "Productions" ("Title","Annotation","Author","Duration","Actors","ID_Theater","Genre")
             VALUES (%s,'Вымышленная постановка для демонстрации проекта.','Учебный автор',%s,'Демонстрационный состав',%s,%s)
             RETURNING "ID_Production"''',(name,duration,theater,genre))
            production=cur.fetchone()['ID_Production']
            for offset in (3,10):
                cur.execute('''INSERT INTO "Show_Details" ("ID_Production","Show_Date","Start_time","Hall_number")
                 VALUES (%s,CURRENT_DATE+%s,'19:00',1) RETURNING "ID_ShowDetails"''',(production,offset+production))
                show=cur.fetchone()['ID_ShowDetails']
                for kind,total in [('партер',50),('бельэтаж',30),('балкон',20)]:
                    cur.execute('INSERT INTO "ShowSeats" ("ShowDetails_ID","SeatType","TotalSeats") VALUES (%s,%s,%s)',(show,kind,total))
    print('Installed fictional demo. Viewer: demo / DemoPass2026; admin: admin / AdminPass2026')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    install()
