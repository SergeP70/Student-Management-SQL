import sys
import os
import sqlite3
import mysql.connector
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, QLineEdit, QPushButton, QComboBox, QMainWindow, \
    QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QMessageBox, QToolBar, QStatusBar
from dotenv import load_dotenv

load_dotenv()
HOST = os.getenv("HOST")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


class DatabaseConnection:
    def __init__(self, host=HOST, user=USERNAME, password=PASSWORD, database='school' ):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user,
                                             password=self.password, database= self.database)
        return connection


# When using SQLite
# class DatabaseConnection:
#     def __init__(self, database = 'database.db'):
#         self.database = database
#
#     def connect(self):
#         connection = sqlite3.connect(self.database)
#         return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(600, 400)

        mnu_file = self.menuBar().addMenu("&File")
        action_add_student = QAction(QIcon('icons/add.png'), 'Add Student', self)
        action_add_student.triggered.connect(self.insert)
        mnu_file.addAction(action_add_student)

        mnu_edit = self.menuBar().addMenu("&Edit")
        action_search_student = QAction(QIcon('icons/search.png'), 'Search', self)
        action_search_student.triggered.connect(self.search)
        mnu_edit.addAction(action_search_student)

        mnu_help = self.menuBar().addMenu("&Help")
        about_action = QAction('About', self)
        mnu_help.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.about)

        # create toolbar and elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(action_add_student)
        toolbar.addAction(action_search_student)

        self.tblStudents = QTableWidget()
        self.tblStudents.setColumnCount(4)
        self.tblStudents.setHorizontalHeaderLabels(('Id', 'Name', 'Course', 'Mobile'))
        self.tblStudents.verticalHeader().setVisible(False)
        self.setCentralWidget(self.tblStudents)

        # create status bar and elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.hide()

        btnEdit = QPushButton('Edit record')
        btnEdit.clicked.connect(self.edit)
        btnDelete = QPushButton('Delete record')
        btnDelete.clicked.connect(self.delete)
        self.statusbar.addWidget(btnEdit)
        self.statusbar.addWidget(btnDelete)

        # Detect a cell click and activate toolbar buttons
        self.tblStudents.cellClicked.connect(self.showStatusBarButtons)
        self.tblStudents.itemChanged.connect(self.hideStatusBarButtons)
        self.tblStudents.focusOutEvent = self.tableFocusOutEvent

    def showStatusBarButtons(self):
        self.statusbar.show()

    def hideStatusBarButtons(self):
        self.statusbar.hide()

    def tableFocusOutEvent(self, event):
        # This method will be called when the table loses focus
        self.statusbar.hide()
        event.accept()

    def load_data(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        # content = cursor.execute("SELECT * FROM students")
        cursor.execute("SELECT * FROM students")
        content = cursor.fetchall()
        self.tblStudents.setRowCount(0)
        for row_id, row_data in enumerate(content):
            self.tblStudents.insertRow(row_id)
            for col_id, data in enumerate(row_data):
                self.tblStudents.setItem(row_id, col_id, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created by Serge Pille during the course "The Python Mega Course".
        Feel free to modify and use this app
        """
        self.setText(content)


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Add a student')
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        self.txtName = QLineEdit()
        self.txtName.setPlaceholderText('Name')
        layout.addWidget(self.txtName)

        self.cboCourse = QComboBox()
        courses = ['Biology', 'Astronomy', 'Math', 'Physics']
        self.cboCourse.addItems(courses)
        layout.addWidget(self.cboCourse)

        self.txtMobile = QLineEdit()
        self.txtMobile.setPlaceholderText('Mobile nr')
        layout.addWidget(self.txtMobile)

        btnSubmit = QPushButton('Submit')
        btnSubmit.clicked.connect(self.add_student)
        layout.addWidget(btnSubmit)

        btnCancel = QPushButton('Cancel')
        btnCancel.clicked.connect(self.closing)
        layout.addWidget(btnCancel)

        self.setLayout(layout)

    def add_student(self):
        name = self.txtName.text()
        course = self.cboCourse.currentText()
        mobile = self.txtMobile.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)',
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.accept()

    def closing(self):
        self.accept()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Search a student')
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        self.txtName = QLineEdit()
        self.txtName.setPlaceholderText('Name')
        layout.addWidget(self.txtName)

        self.btnSearch = QPushButton('Search')
        self.btnSearch.clicked.connect(self.search)
        layout.addWidget(self.btnSearch)

        self.setLayout(layout)

    def search(self):
        main_window.tblStudents.setCurrentItem(None)
        lookup = self.txtName.text()
        matching_items = main_window.tblStudents.findItems(lookup, Qt.MatchFlag.MatchContains)
        if matching_items:
            for item in matching_items:
                item.setSelected(True)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText('Data not found')
            msg.setWindowTitle('Warning')
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Edit a student')
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        layout = QVBoxLayout()

        # Get Student name from the selected row
        index = main_window.tblStudents.currentRow()
        student_name = main_window.tblStudents.item(index, 1).text()
        self.txtName = QLineEdit(student_name)
        self.txtName.setPlaceholderText('Name')
        layout.addWidget(self.txtName)

        self.student_id = main_window.tblStudents.item(index, 0).text()

        course_name = main_window.tblStudents.item(index, 2).text()
        self.cboCourse = QComboBox()
        courses = ['Biology', 'Astronomy', 'Math', 'Physics']
        self.cboCourse.addItems(courses)
        self.cboCourse.setCurrentText(course_name)
        layout.addWidget(self.cboCourse)

        mobile = main_window.tblStudents.item(index, 3).text()
        self.txtMobile = QLineEdit(mobile)
        self.txtMobile.setPlaceholderText('Mobile nr')
        layout.addWidget(self.txtMobile)

        btnSubmit = QPushButton('Update')
        btnSubmit.clicked.connect(self.update_student)
        layout.addWidget(btnSubmit)

        btnCancel = QPushButton('Cancel')
        btnCancel.clicked.connect(self.closing)
        layout.addWidget(btnCancel)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s",
                       (self.txtName.text(), self.cboCourse.currentText(), self.txtMobile.text(), self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.accept()

    def closing(self):
        self.accept()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Delete a student')

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        btn_yes = QPushButton("Yes")
        btn_no = QPushButton("No")
        layout.addWidget(confirmation, 0,0,1,2)
        layout.addWidget(btn_yes, 1, 0)
        layout.addWidget(btn_no, 1, 1)
        self.setLayout(layout)

        btn_yes.clicked.connect(self.delete_student)

    def delete_student(self):
        index = main_window.tblStudents.currentRow()
        student_id = main_window.tblStudents.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()

        confirmation = QMessageBox()
        confirmation.setWindowTitle("Success")
        confirmation.setText("The record was successfully deleted")
        confirmation.exec()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())