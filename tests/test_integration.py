"""Run only against a disposable database named *_test. Creates schema if empty."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
import os
import uuid
import pytest
import psycopg2
import db
import setup_demo

@pytest.fixture(scope='session',autouse=True)
def database():
    db.load_env()
    if not os.getenv('PGDATABASE','').endswith('_test'):
        pytest.skip('Set PGDATABASE to a disposable *_test database')
    with db.transaction() as cur:
        cur.execute("SELECT to_regclass('public.\"Clients\"') AS name")
        exists=cur.fetchone()['name']
    if not exists: setup_demo.install()

@pytest.fixture
def viewer():
    login='test_'+uuid.uuid4().hex[:12]
    client=db.addUser(login,'ExamplePass2026')
    db.authenticate(login,'ExamplePass2026')
    return login,client

def show(capacity=1):
    with db.transaction() as cur:
        cur.execute('''INSERT INTO "Show_Details" ("ID_Production","Show_Date","Start_time","Hall_number")
         SELECT min("ID_Production"),CURRENT_DATE+60,%s,1 FROM "Productions" RETURNING "ID_ShowDetails"''',
                    (f'{uuid.uuid4().int%24:02}:{uuid.uuid4().int%60:02}:{uuid.uuid4().int%60:02}',))
        sid=cur.fetchone()['ID_ShowDetails']
        cur.execute('INSERT INTO "ShowSeats" ("ShowDetails_ID","SeatType","TotalSeats") VALUES (%s,\'партер\',%s)',(sid,capacity))
        return sid

def test_registration_hash_and_duplicate(viewer):
    login,client=viewer
    with db.transaction() as cur:
        cur.execute('SELECT "Password","Email","Phone_number" FROM "Clients" WHERE "ID_Client"=%s',(client,))
        row=cur.fetchone()
    assert row['Password'].startswith('pbkdf2_sha256$') and row['Email'] is None
    assert db.verify_password('ExamplePass2026',row['Password'])
    with pytest.raises(psycopg2.errors.UniqueViolation): db.addUser(login.upper(),'ExamplePass2026')
    with pytest.raises(ValueError): db.authenticate(login,'incorrect password')
    with pytest.raises(PermissionError): db.getAllTickets()
    assert db.authenticate(login,'ExamplePass2026')['ID_Client']==client

def test_return_releases_seat_and_keeps_history(viewer):
    _,client=viewer; sid=show()
    ticket=db.addTicket(client,sid,'партер')
    assert db.getTotalAvailableSeats(sid,'партер')==0
    db.deleteTicket(ticket)
    assert db.getTotalAvailableSeats(sid,'партер')==1
    assert next(t for t in db.getTicketsInfo(client) if t['id']==ticket)['status']=='cancelled'
    with pytest.raises(ValueError): db.deleteTicket(ticket)
    assert db.getTotalAvailableSeats(sid,'партер')==1

def test_cannot_return_other_clients_ticket(viewer):
    login,client=viewer; sid=show(); ticket=db.addTicket(client,sid,'партер')
    other='other_'+uuid.uuid4().hex[:10]; db.addUser(other,'ExamplePass2026'); db.authenticate(other,'ExamplePass2026')
    with pytest.raises(ValueError): db.deleteTicket(ticket)
    with pytest.raises(PermissionError): db.getTicketsInfo(client)
    with pytest.raises(PermissionError): db.addTicket(client,sid,'партер')
    assert db.getTotalAvailableSeats(sid,'партер')==0

def test_two_requests_for_last_seat(viewer):
    login,client=viewer; sid=show()
    from threading import Barrier
    barrier=Barrier(2)
    def buy(_):
        db.authenticate(login,'ExamplePass2026'); barrier.wait(timeout=10)
        try: return db.addTicket(client,sid,'партер')
        except psycopg2.errors.RaiseException: return None
    with ThreadPoolExecutor(2) as executor: results=list(executor.map(buy,range(2)))
    assert sum(t is not None for t in results)==1
    assert db.getTotalAvailableSeats(sid,'партер')==0

def test_failed_insert_rolls_back_counter(viewer):
    _,client=viewer; sid=show()
    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        with db.transaction() as cur:
            cur.execute('INSERT INTO "Tickets" ("ID_Client","ID_ShowDetails","SeatType") VALUES (-1,%s,\'партер\')',(sid,))
    assert db.getTotalAvailableSeats(sid,'партер')==1
    assert db.addTicket(client,sid,'партер')

def test_show_and_capacities_are_atomic(viewer):
    with pytest.raises(PermissionError): db.addShowByNames('Вечер комедии','Учебный театр','2090-01-01','19:00')
    db.authenticate('admin','AdminPass2026')
    with db.transaction() as cur:
        cur.execute('SELECT count(*) AS n FROM "Show_Details"'); before=cur.fetchone()['n']
    with pytest.raises(psycopg2.errors.CheckViolation):
        db.addShowByNames('Вечер комедии','Учебный театр','2090-01-01','19:00',{'партер':5,'балкон':-1})
    with db.transaction() as cur:
        cur.execute('SELECT count(*) AS n FROM "Show_Details"'); assert cur.fetchone()['n']==before
    with pytest.raises(ValueError): db.addShowByNames('Вечер комедии','Другой театр','2090-01-01','19:00')
    sid=db.addShowByNames('Вечер комедии','Учебный театр','2090-01-01',f'19:{uuid.uuid4().int%60:02}:{uuid.uuid4().int%60:02}')
    assert len(db.getSeatTypes(sid))==3

def test_reviews_constraints(viewer):
    _,client=viewer
    with pytest.raises(psycopg2.errors.CheckViolation): db.addReview(1,client,'Текст',11)
    db.addReview(1,client,'Учебный отзыв',8)
    with pytest.raises(psycopg2.errors.UniqueViolation): db.addReview(1,client,'Повтор',7)

def test_past_show_cannot_be_purchased(viewer):
    _,client=viewer; sid=show()
    with db.transaction() as cur: cur.execute('UPDATE "Show_Details" SET "Show_Date"=CURRENT_DATE-1 WHERE "ID_ShowDetails"=%s',(sid,))
    with pytest.raises(psycopg2.errors.RaiseException): db.addTicket(client,sid,'партер')
    assert db.getTotalAvailableSeats(sid,'партер')==1
