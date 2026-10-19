"""Database service for the local PyQt client. Every operation owns its transaction."""
import base64
import hashlib
import hmac
import os
import secrets
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

_session = ContextVar('theater_session', default=None)


def load_env():
    path = Path(__file__).with_name('.env')
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines():
            if line.strip() and not line.lstrip().startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())


@contextmanager
def transaction():
    load_env()
    connection = psycopg2.connect(
        host=os.getenv('PGHOST','localhost'), port=os.getenv('PGPORT','5432'),
        dbname=os.getenv('PGDATABASE','theater_portfolio'),
        user=os.getenv('PGUSER','theater_app'), password=os.getenv('PGPASSWORD',''),
        connect_timeout=5, cursor_factory=RealDictCursor)
    try:
        with connection:
            with connection.cursor() as cursor:
                yield cursor
    finally:
        connection.close()


def password_hash(password):
    if not 8 <= len(password) <= 256:
        raise ValueError('Пароль должен содержать от 8 до 256 символов')
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 600000)
    return 'pbkdf2_sha256$600000$' + base64.b64encode(salt).decode() + '$' + base64.b64encode(digest).decode()


def verify_password(password, encoded):
    try:
        algorithm, rounds, salt, expected = encoded.split('$')
        if algorithm != 'pbkdf2_sha256' or not 8 <= len(password) <= 256:
            return False
        if not 100000 <= int(rounds) <= 1000000:
            return False
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), base64.b64decode(salt), int(rounds))
        return hmac.compare_digest(actual, base64.b64decode(expected))
    except (ValueError, TypeError):
        return False


def logout():
    _session.set(None)


def require_user(client_id=None, admin=False):
    user = _session.get()
    if not user or (admin and not user['is_admin']):
        raise PermissionError('Недостаточно прав')
    if client_id is not None and user['ID_Client'] != int(client_id):
        raise PermissionError('Доступ к чужим билетам запрещён')
    return user


def authenticate(login, password):
    logout()
    with transaction() as cur:
        cur.execute('SELECT * FROM "Clients" WHERE "Login"=%s', (login.strip().lower(),))
        user = cur.fetchone()
    if not user or not verify_password(password, user['Password']):
        raise ValueError('Неверный логин или пароль')
    user.pop('Password')
    _session.set(dict(user))
    return user


def getUserInfo(username):
    with transaction() as cur:
        cur.execute('SELECT "ID_Client", "Login", "is_admin" FROM "Clients" WHERE "Login"=%s', (username.strip().lower(),))
        return cur.fetchone()


def addUser(login, password):
    login = login.strip().lower()
    if not 3 <= len(login) <= 64:
        raise ValueError('Логин должен содержать от 3 до 64 символов')
    encoded = password_hash(password)
    with transaction() as cur:
        cur.execute('INSERT INTO "Clients" ("Login","Password") VALUES (%s,%s) RETURNING "ID_Client"', (login, encoded))
        return cur.fetchone()['ID_Client']


def searchPerformances(query=''):
    require_user()
    with transaction() as cur:
        cur.execute('''SELECT p."ID_Production" AS id, s."ID_ShowDetails" AS show_id,
         th."Title" AS theater_name,p."Title" AS production_name,s."Show_Date" AS show_date
         FROM "Show_Details" s JOIN "Productions" p ON p."ID_Production"=s."ID_Production"
         JOIN "Theaters" th ON th."ID_Theater"=p."ID_Theater"
         WHERE s."Show_Date"+s."Start_time">LOCALTIMESTAMP AND
         (p."Title" ILIKE %s OR th."Title" ILIKE %s OR s."Show_Date"::text ILIKE %s)
         ORDER BY s."Show_Date",s."Start_time",p."Title"''', (f'%{query}%',)*3)
        return cur.fetchall()


def getProductionsInfo(production_id, show_id):
    require_user()
    with transaction() as cur:
        cur.execute('''SELECT p.*,s."Show_Date",s."Start_time",th."Address"
         FROM "Productions" p JOIN "Show_Details" s ON s."ID_Production"=p."ID_Production"
         JOIN "Theaters" th ON th."ID_Theater"=p."ID_Theater"
         WHERE p."ID_Production"=%s AND s."ID_ShowDetails"=%s''', (production_id,show_id))
        row = cur.fetchone()
        if not row:
            raise ValueError('Показ не найден')
        return row


def getSeatTypes(show_id):
    require_user()
    with transaction() as cur:
        cur.execute('SELECT "SeatType","TotalSeats" FROM "ShowSeats" WHERE "ShowDetails_ID"=%s ORDER BY "ID_ShowSeat"', (show_id,))
        return cur.fetchall()


def getTotalAvailableSeats(show_id, seat_type):
    require_user()
    with transaction() as cur:
        cur.execute('SELECT "TotalSeats"-"SoldSeats" AS available FROM "ShowSeats" WHERE "ShowDetails_ID"=%s AND "SeatType"=%s', (show_id,seat_type))
        row = cur.fetchone()
        return row['available'] if row else 0


def addTicket(client_id, show_id, seat_type):
    require_user(client_id)
    with transaction() as cur:
        cur.execute('''INSERT INTO "Tickets" ("ID_Client","ID_ShowDetails","SeatType")
         VALUES (%s,%s,%s) RETURNING "ID_Ticket"''', (client_id,show_id,seat_type))
        return cur.fetchone()['ID_Ticket']


def deleteTicket(ticket_id):
    user = require_user()
    with transaction() as cur:
        cur.execute('''UPDATE "Tickets" SET "Status"='cancelled'
         WHERE "ID_Ticket"=%s AND "ID_Client"=%s AND "Status"='active' RETURNING "ID_Ticket"''', (ticket_id,user['ID_Client']))
        if not cur.fetchone():
            raise ValueError('Билет не найден, уже возвращён или принадлежит другому пользователю')


def getTicketsInfo(user_id):
    require_user(user_id)
    with transaction() as cur:
        cur.execute('''SELECT t."ID_Ticket" AS id,p."Title" AS production_name,th."Title" AS theater_name,
         s."Show_Date" AS show_date,s."Start_time" AS show_time,th."Address" AS address,t."SeatType",
         t."Status" AS status FROM "Tickets" t
         JOIN "Show_Details" s ON s."ID_ShowDetails"=t."ID_ShowDetails"
         JOIN "Productions" p ON p."ID_Production"=s."ID_Production"
         JOIN "Theaters" th ON th."ID_Theater"=p."ID_Theater"
         WHERE t."ID_Client"=%s ORDER BY s."Show_Date" DESC,t."ID_Ticket" DESC''',(user_id,))
        return cur.fetchall()


def getAllTickets(query=''):
    require_user(admin=True)
    with transaction() as cur:
        cur.execute('''SELECT t."ID_Ticket" AS id,c."Login" AS client_login,p."Title" AS production_name,
         th."Title" AS theater_name,s."Show_Date" AS show_date,s."Start_time" AS show_time,
         t."SeatType" || CASE WHEN t."Status"='cancelled' THEN ' (возвращён)' ELSE '' END AS seat_type
         FROM "Tickets" t JOIN "Clients" c ON c."ID_Client"=t."ID_Client"
         JOIN "Show_Details" s ON s."ID_ShowDetails"=t."ID_ShowDetails"
         JOIN "Productions" p ON p."ID_Production"=s."ID_Production"
         JOIN "Theaters" th ON th."ID_Theater"=p."ID_Theater"
         WHERE concat_ws(' ',t."ID_Ticket",c."Login",p."Title",th."Title",s."Show_Date") ILIKE %s
         ORDER BY s."Show_Date" DESC,t."ID_Ticket" DESC''',(f'%{query}%',))
        return cur.fetchall()


def getReviewsByProduction(production_id):
    require_user()
    with transaction() as cur:
        cur.execute('''SELECT c."Login" AS client_login,r."Review_content",r."Assessment"
         FROM "Reviews" r JOIN "Clients" c ON c."ID_Client"=r."ID_Client"
         WHERE r."ID_Productions"=%s ORDER BY r."Date_of_writing" DESC,r."ID_Review" DESC''',(production_id,))
        return cur.fetchall()


def addReview(production_id, client_id, review_text, assessment):
    require_user(client_id)
    with transaction() as cur:
        cur.execute('''INSERT INTO "Reviews" ("ID_Productions","ID_Client","Review_content","Assessment")
         VALUES (%s,%s,%s,%s)''',(production_id,client_id,review_text.strip(),assessment))


def addShowByNames(production_name, theater_name, show_date, start_time, capacities=None):
    require_user(admin=True)
    moment = datetime.fromisoformat(f'{show_date}T{start_time}')
    if moment <= datetime.now():
        raise ValueError('Дата и время показа должны быть в будущем')
    capacities = capacities if capacities is not None else {'партер':50,'бельэтаж':30,'балкон':20}
    if not capacities:
        raise ValueError('Укажите вместимость показа')
    with transaction() as cur:
        cur.execute('''SELECT p."ID_Production" FROM "Productions" p
         JOIN "Theaters" th ON th."ID_Theater"=p."ID_Theater"
         WHERE p."Title"=%s AND th."Title"=%s''',(production_name,theater_name))
        row = cur.fetchone()
        if not row:
            raise ValueError('Постановка не найдена в указанном театре')
        cur.execute('''INSERT INTO "Show_Details" ("ID_Production","Show_Date","Start_time","Hall_number")
         VALUES (%s,%s,%s,1) RETURNING "ID_ShowDetails"''',(row['ID_Production'],show_date,start_time))
        show_id=cur.fetchone()['ID_ShowDetails']
        for kind, total in capacities.items():
            cur.execute('INSERT INTO "ShowSeats" ("ShowDetails_ID","SeatType","TotalSeats") VALUES (%s,%s,%s)',(show_id,kind,total))
        return show_id


def friendly_error(exc):
    if isinstance(exc, psycopg2.errors.UniqueViolation):
        return 'Такая запись уже существует: проверьте логин, отзыв или время показа.'
    if isinstance(exc, psycopg2.errors.RaiseException):
        return exc.diag.message_primary
    if isinstance(exc, psycopg2.Error):
        return 'Не удалось выполнить операцию с базой. Изменения отменены; проверьте подключение и данные.'
    if isinstance(exc, (ValueError, PermissionError)):
        return str(exc)
    return 'Не удалось выполнить операцию. Проверьте данные и повторите попытку.'
