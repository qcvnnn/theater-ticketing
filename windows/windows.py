import hashlib
from datetime import date, datetime
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox, QAbstractItemView, QVBoxLayout, QHeaderView, \
    QComboBox, QSpinBox, QListWidget, QListWidgetItem
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import db


class BaseWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.authWindow = Authorization()
        self.authWindow.show()

    def exit(self):
        self.authWindow.show()
        self.close()


class Authorization(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initActivity()
        self.apply_styles()

    def initUI(self):
        uic.loadUi('ui/auth.ui', self)

    def apply_styles(self):
        with open('styles/auth.css', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def initActivity(self):
        self.loginButton.clicked.connect(self.signIn)
        self.registrationButton.clicked.connect(self.register)

    def userWindow(self):
        self.userWindow = UserMain(username)
        self.userWindow.show()
        self.close()

    def register(self):
        self.regWindow = Registration()
        self.regWindow.show()
        self.close()

    def adminWindow(self):
        self.adminWindow = UserAdmin(username)
        self.adminWindow.show()
        self.close()

    def signIn(self):
        global username
        try:
            user = db.authenticate(self.loginInput.text(), self.passwordInput.text())
            username = user['Login']
            if user['is_admin']:
                self.adminWindow()
            else:
                self.userWindow()
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка', db.friendly_error(exc))


class UserAdmin(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()
        self.initActivity()
        self.apply_styles()

        self.usernameLabel.setText(self.username)

        # Настройка таблицы (билеты пользователей)
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels([
            'ID билета', 'Клиент', 'Спектакль', 'Театр', 'Дата', 'Время', 'Тип места'
        ])
        self.tableWidget.setColumnWidth(0, 90)
        self.tableWidget.setColumnWidth(1, 120)
        self.tableWidget.setColumnWidth(2, 180)
        self.tableWidget.setColumnWidth(3, 180)
        self.tableWidget.setColumnWidth(4, 100)
        self.tableWidget.setColumnWidth(5, 70)
        self.tableWidget.setColumnWidth(6, 100)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.loadTickets()

    def initUI(self):
        uic.loadUi('ui/main_admin.ui', self)

    def initActivity(self):
        self.logoutButton.clicked.connect(self.logout)
        self.searchButton.clicked.connect(self.search)
        self.addButton.clicked.connect(self.addShow)

    def apply_styles(self):
        with open('styles/admin_menu.css', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def loadTickets(self, query=""):
        self.clearTable()
        tickets = db.getAllTickets(query)

        if not tickets:
            self.tableWidget.setRowCount(1)
            self.tableWidget.setItem(0, 0, QTableWidgetItem("Нет данных"))
            return

        for i, row in enumerate(tickets):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            self.tableWidget.setItem(i, 0, QTableWidgetItem(str(row.get('id', ''))))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(str(row.get('client_login', ''))))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(str(row.get('production_name', ''))))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(str(row.get('theater_name', ''))))
            self.tableWidget.setItem(i, 4, QTableWidgetItem(str(row.get('show_date', ''))))

            show_time = row.get('show_time')
            if show_time:
                self.tableWidget.setItem(i, 5, QTableWidgetItem(str(show_time)[:5]))
            else:
                self.tableWidget.setItem(i, 5, QTableWidgetItem(''))

            self.tableWidget.setItem(i, 6, QTableWidgetItem(str(row.get('seat_type', ''))))

    def search(self):
        text = self.lineEdit.text()
        self.loadTickets(text)

    def clearTable(self):
        while self.tableWidget.rowCount():
            self.tableWidget.removeRow(0)

    def addShow(self):
        self.addResWindow = AddShow(self.username)
        self.addResWindow.show()
        self.close()

    def logout(self):
        db.logout()
        self.authWindow = Authorization()
        self.authWindow.show()
        self.close()


class AddShow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()
        self.initActivity()
        self.apply_styles()

    def apply_styles(self):
        with open('styles/add_showt.css', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def initUI(self):
        uic.loadUi('ui/add_showt.ui', self)
        self.setWindowTitle("Добавление показа")

    def initActivity(self):
        self.pushButton.clicked.connect(self.back)
        self.addRestaurantButton.clicked.connect(self.addShow)

    def addShow(self):
        try:
            db.addShowByNames(self.selectNameLine.text().strip(),
                self.selectNameLine_2.text().strip(), self.selectDescriptionLine.text().strip(),
                self.timeEdit.time().toString('HH:mm:ss'))
            QMessageBox.information(self, 'Успех', 'Показ и категории мест добавлены')
            self.back()
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка', db.friendly_error(exc))

    def back(self):
        self.adminWindow = UserAdmin(self.username)
        self.adminWindow.show()
        self.close()


class UserMain(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.initUI()
        self.initActivity()
        self.reservations = []
        self.userInfo = db.getUserInfo(username)
        self.apply_styles()

        self.label.setText(username)

        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Театр', 'Постановка', 'Дата', 'ПоказID'])
        self.tableWidget.setColumnWidth(0, 0)
        self.tableWidget.setColumnWidth(1, 230)
        self.tableWidget.setColumnWidth(2, 309)
        self.tableWidget.setColumnWidth(3, 171)
        self.tableWidget.setColumnWidth(4, 0)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.cellClicked.connect(self.tablewidgetClicked)
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setFixedSize(750, 620)
        self.reservationsList.setSpacing(5)

        self.loadInfo()
        self.currentReservations()
        self.currentArchiveTickets()
        self.archiveTabWidget.setCurrentIndex(0)

    def initUI(self):
        uic.loadUi('ui/user_menu.ui', self)

    def refreshTickets(self):
        self.reservations.clear()
        self.reservationsList.clear()
        self.currentReservations()
        self.currentArchiveTickets()

    def tablewidgetClicked(self, row):
        production_id = self.tableWidget.item(row, 0).text()
        show_id = self.tableWidget.item(row, 4).text()
        self.reservation(production_id, show_id)

    def reservation(self, production_id, show_id):
        self.resWindow = Reservation(production_id, show_id)
        self.resWindow.show()
        self.close()

    def initActivity(self):
        self.logoutButton.clicked.connect(self.logout)
        self.searchButton.clicked.connect(self.search)
        self.reservationsList.itemClicked.connect(self.clickHandler)

    def clearTable(self):
        while self.tableWidget.rowCount():
            self.tableWidget.removeRow(0)

    def clickHandler(self, item):
        ticket_id = item.data(Qt.UserRole)
        ticket = next((t for t in self.reservations if t[3] == ticket_id), None)
        if ticket:
            text = (f'Спектакль: {ticket[0]}\nТеатр: {ticket[1]}\n'
                    f'Дата: {ticket[2]}\nАдрес: {ticket[4]}\nНомер билета: {ticket[3]}')
            self.infoWindow = ReservationInfo(text, ticket[3])
            self.infoWindow.show()
            self.close()

    def search(self):
        text = self.lineEdit.text()
        self.loadInfo(text)

    def loadInfo(self, query=""):
        self.clearTable()
        info = db.searchPerformances(query)
        for i, row in enumerate(info):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            self.tableWidget.setItem(i, 0, QTableWidgetItem(str(row['id'])))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(row['theater_name']))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(row['production_name']))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(str(row['show_date'])))
            self.tableWidget.setItem(i, 4, QTableWidgetItem(str(row['show_id'])))

    def logout(self):
        db.logout()
        self.authWindow = Authorization()
        self.authWindow.show()
        self.close()

    def apply_styles(self):
        with open('styles/user_menu.css', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def currentReservations(self):
        tickets = db.getTicketsInfo(self.userInfo['ID_Client'])

        for ticket in tickets:
            ticket_id = ticket['id']
            production_name = ticket['production_name']
            theater_name = ticket['theater_name']
            show_date = ticket['show_date']
            address = ticket.get('address', '')
            if ticket['status'] != 'active' or datetime.combine(show_date, ticket['show_time']) <= datetime.now():
                continue

            self.reservations.append([production_name, theater_name, show_date, ticket_id, address])

        self.reservations = sorted(self.reservations, key=lambda x: x[2])

        for item in self.reservations:
            list_item = QListWidgetItem(
                f'Спектакль: "{item[0]}"\n'
                f'Театр: {item[1]}\n'
                f'Дата: {item[2]}\n'
                f'Номер заказа: {item[3]}'
            )
            list_item.setData(Qt.UserRole, item[3])
            self.reservationsList.addItem(list_item)

    def currentArchiveTickets(self):
        tickets = db.getTicketsInfo(self.userInfo['ID_Client'])
        archive_tickets = []

        for ticket in tickets:
            ticket_id = ticket['id']
            production_name = ticket['production_name']
            theater_name = ticket['theater_name']
            show_date = ticket['show_date']
            show_time = ticket['show_time']
            address = ticket.get('address', '')

            if ticket['status'] == 'active' and datetime.combine(show_date, show_time) > datetime.now():
                continue

            archive_tickets.append([production_name, theater_name, show_date, show_time, ticket_id, address, ticket['status']])

        archive_tickets = sorted(archive_tickets, key=lambda x: x[2])

        self.archiveList.clear()

        for item in archive_tickets:
            self.archiveList.addItem(
                f'Спектакль: "{item[0]}"\n'
                f'Театр: {item[1]}\n'
                f'Дата: {item[2]} в {item[3]}\n'
                f'Номер заказа: {item[4]} — ' + ('возвращён' if item[6] == 'cancelled' else 'показ завершён')
            )


class Reservation(QMainWindow):
    def __init__(self, production_id, show_id):
        super().__init__()
        self.production_id = production_id
        self.show_id = show_id
        self.info = db.getProductionsInfo(production_id, show_id)
        self.initUI()
        self.initActivity()
        self.apply_styles()

    def load_image(self, path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            return pixmap

        # Пробуем через QImage
        image = QImage(path)
        if not image.isNull():
            return QPixmap.fromImage(image)

        # Если ничего не работает — серая заглушка
        pixmap = QPixmap(200, 200)
        pixmap.fill(Qt.gray)
        return pixmap

    def initUI(self):
        uic.loadUi('ui/purchase.ui', self)

        pixmap = self.load_image(self.info['Image'] or '')
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setScaledContents(True)

        self.nameLabel.setText(self.info['Title'])
        if self.info['Show_Date'] and self.info['Start_time']:
            date_str = self.info['Show_Date'].strftime('%d.%m.%Y')
            time_str = str(self.info['Start_time'])[:5]
            self.dateTimeLabel.setText(f"Дата: {date_str} в {time_str}")

        info_text = ""
        if self.info.get('Annotation'):
            info_text += f"{self.info['Annotation']}\n\n"
        if self.info.get('Genre'):
            info_text += f"Жанр: {self.info['Genre']}\n\n"
        if self.info.get('Author'):
            info_text += f"Автор: {self.info['Author']}\n\n"
        if self.info.get('Duration'):
            info_text += f"Длительность: {self.info['Duration']} минут\n\n"
        if self.info.get('Actors'):
            info_text += f"Актёры: {self.info['Actors']}\n\n"
        if self.info.get('Address'):
            info_text += f"Адрес театра: {self.info['Address']}"

        self.infoPlain.setPlainText(info_text)
        self.infoPlain.setReadOnly(True)

        self.timeBox.clear()
        seat_types = db.getSeatTypes(self.show_id)
        for st in seat_types:
            self.timeBox.addItem(st['SeatType'])

        self.updateAvailableSeats()
        self.timeBox.currentIndexChanged.connect(self.updateAvailableSeats)

    def initActivity(self):
        self.backButton.clicked.connect(self.backPage)
        self.resButton.clicked.connect(self.buyTicket)
        self.reviewsButton.clicked.connect(self.showReviews)

    def apply_styles(self):
        with open('styles/purchase.css', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def showReviews(self):
        self.reviewsWindow = Reviews(self.production_id, self.info['Title'])
        self.reviewsWindow.show()
        self.close()

    def buyTicket(self):
        seat_type = self.timeBox.currentText()
        userInfo = db.getUserInfo(username)
        if not userInfo:
            QMessageBox.critical(self, "Ошибка", "Пользователь не найден")
            return

        try:
            db.addTicket(userInfo['ID_Client'], self.show_id, seat_type)
            self.updateAvailableSeats()
            QMessageBox.information(self, "Успех!", "Билет куплен")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", db.friendly_error(e))

    def updateAvailableSeats(self):
        seat_type = self.timeBox.currentText()
        available = db.getTotalAvailableSeats(self.show_id, seat_type)
        self.amountLabel.setText(f'Свободных мест "{seat_type}": {available}')

    def backPage(self):
        self.userWindow = UserMain(username)
        self.userWindow.show()
        self.close()


class ReservationInfo(QMainWindow):
    def __init__(self, text, ticket_id):
        super().__init__()
        self.text = text
        self.ticket_id = ticket_id
        self.initUI()
        self.initActivity()
        self.apply_styles()

        self.infoText.setText(self.text)
        self.infoLabel.setText('Информация о билете №' + str(self.ticket_id))

    def initUI(self):
        uic.loadUi('ui/purchaseInfo.ui', self)

    def apply_styles(self):
        with open('styles/purchaseInfo.css', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def initActivity(self):
        self.backButton.clicked.connect(self.backPage)
        self.deleteButton.clicked.connect(self.deleteTicket)

    def backPage(self):
        self.userWindow = UserMain(username)
        self.userWindow.show()
        self.close()

    def deleteTicket(self):
        reply = QMessageBox.question(self, 'Подтверждение', 'Вернуть билет?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                db.deleteTicket(self.ticket_id)
                QMessageBox.information(self, 'Успешно', 'Билет возвращён, место освобождено')
                self.backPage()
            except Exception as exc:
                QMessageBox.critical(self, 'Ошибка', db.friendly_error(exc))


class Reviews(QMainWindow):
    def __init__(self, production_id, production_name):
        super().__init__()
        self.production_id = production_id
        self.production_name = production_name
        self.initUI()
        self.initActivity()
        self.apply_styles()

    def initUI(self):
        uic.loadUi('ui/reviews.ui', self)
        self.spinBox.setRange(1, 10)
        self.label.setText(self.production_name)
        self.listWidget.setSpacing(6)
        self.load_reviews()

    def apply_styles(self):
        with open('styles/reviews.css', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def load_reviews(self):
        self.listWidget.clear()
        reviews = db.getReviewsByProduction(self.production_id)
        if not reviews:
            self.listWidget.addItem("Нет отзывов")
            return

        for data in reviews:
            login = data.get('client_login') or data.get('Login')
            text = data.get('review_content') or data.get('Review_content')
            stars = data.get('assessment') or data.get('Assessment')
            if login and text and stars:
                self.listWidget.addItem(f"Пользователь {login}\n{text}\nОценка: {stars}")

    def initActivity(self):
        self.backButton.clicked.connect(self.back)
        self.addReviewButton.clicked.connect(self.add_review)

    def back(self):
        self.userWindow = UserMain(username)
        self.userWindow.show()
        self.close()

    def add_review(self):
        try:
            user = db.require_user()
            db.addReview(self.production_id, user['ID_Client'], self.lineEdit.text(), self.spinBox.value())
            self.load_reviews()
            self.lineEdit.clear()
            QMessageBox.information(self, 'Успешно', 'Отзыв добавлен')
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка', db.friendly_error(exc))


class Registration(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initActivity()
        self.apply_styles()

    def initUI(self):
        uic.loadUi('ui/registration.ui', self)

    def apply_styles(self):
        with open('styles/registration.css', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def initActivity(self):
        self.loginButton.clicked.connect(self.signIn)
        self.authButton.clicked.connect(self.login)

    def login(self):
        self.authWindow = Authorization()
        self.authWindow.show()
        self.close()

    def signIn(self):
        if self.passwordInput.text() != self.passwordInput2.text():
            QMessageBox.critical(self, 'Ошибка', 'Пароли не совпадают')
            return
        try:
            db.addUser(self.loginInput.text(), self.passwordInput.text())
            QMessageBox.information(self, 'Успешно', 'Учётная запись создана')
            self.login()
        except Exception as exc:
            QMessageBox.critical(self, 'Ошибка', db.friendly_error(exc))
