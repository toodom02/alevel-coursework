import bcrypt
import os
import sqlite3
from tkinter import messagebox

DBFile = 'cafeDB.db'


# Establishes a connection with the database, and executes the
# SQL statement, with the given parameters passed.
def executeSQL(sqlStatement, parameters, fetchall):
    connection = sqlite3.connect(DBFile)
    cursor = connection.cursor()
    cursor.execute(sqlStatement, parameters)

    if fetchall:
        # returns array
        result = cursor.fetchall()
    else:
        # returns tuple
        result = cursor.fetchone()

    connection.commit()
    connection.close()

    # Returns an array or tuple with any fetched records
    return result


# This function fetches all the records from a specified table
# From the database, and inserts them into a specified treeview
def loadDatabase(tree, table, refresh):
    tree.delete(*tree.get_children())
    records = executeSQL('SELECT * FROM {}'.format(table), (), True)
    for i in records:
        tree.insert('', 0, values=i)

    # Shows messagebox to confirm only when the refresh button was pressed
    if refresh:
        messagebox.showinfo('Loaded', 'Data Refreshed!')


# Creates the database tables, unless they already exist
# And adds an admin user.
def createDatabase():
    if not os.path.isfile(DBFile):
        connection = sqlite3.connect(DBFile)
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS staffTbl(
                staffID         TEXT NOT NULL,
                staffSurname    TEXT NOT NULL,
                staffForename   TEXT NOT NULL,
                staffContact    TEXT NOT NULL,
                accessLevel     INTEGER NOT NULL,
                password        TEXT NOT NULL,
                salt            TEXT NOT NULL,
                PRIMARY KEY(staffID))
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS donationsTbl(
                donationID  TEXT NOT NULL,
                amount      REAL NOT NULL,
                cashorbank  TEXT NOT NULL,
                referenceNo TEXT,
                date        TEXT NOT NULL,
                donorID     TEXT NOT NULL,
                staffID     TEXT NOT NULL,
                PRIMARY KEY(donationID),
                FOREIGN KEY(donorID) REFERENCES donorTbl(donorID),
                FOREIGN KEY(staffID) REFERENCES staffTbl(staffID))
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS donorTbl(
                donorID         TEXT NOT NULL,
                donorSurname    REAL NOT NULL,
                donorForename   TEXT NOT NULL,
                donorContact    TEXT NOT NULL,
                PRIMARY KEY(donorID))
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customerTbl(
                customerID          TEXT NOT NULL,
                customerSurname     TEXT NOT NULL,
                customerForename    TEXT NOT NULL,
                customerContact     TEXT NOT NULL,
                PRIMARY KEY(customerID))
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orderTbl(
                orderNo     TEXT NOT NULL,
                customerID  TEXT NOT NULL,
                orderTotal  REAL NOT NULL,
                date        TEXT NOT NULL,
                staffID     TEXT NOT NULL,
                PRIMARY KEY(orderNO)
                FOREIGN KEY(customerID) REFERENCES customerTbl(customerID),
                FOREIGN KEY(staffID) REFERENCES staffTbl(staffID))
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orderItemTbl(
                orderNo     TEXT NOT NULL,
                itemID      TEXT NOT NULL,
                quantity    INTEGER NOT NULL,
                PRIMARY KEY (orderNo, itemID),
                FOREIGN KEY(orderNo) REFERENCES orderTbl(orderNo),
                FOREIGN KEY(itemID) REFERENCES itemTbl(itemID))
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS itemTbl(
                itemID          TEXT NOT NULL,
                itemName        TEXT NOT NULL,
                salePrice       REAL NOT NULL,
                quantity        INTEGER NOT NULL,
                supplierCost    REAL NOT NULL,
                supplierID      TEXT NOT NULL,
                PRIMARY KEY(itemID),
                FOREIGN KEY(supplierID) REFERENCES supplierTbl(supplierID))
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplierTbl(
                supplierID      TEXT NOT NULL,
                supplierName    TEXT NOT NULL,
                supplierContact TEXT NOT NULL,
                PRIMARY KEY(supplierID))
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS foodDonatTbl(
                foodID          TEXT NOT NULL,
                foodName        TEXT NOT NULL,
                donatDate       TEXT NOT NULL,
                expiryDate      TEXT NOT NULL,
                givenAway       INTEGER NOT NULL,
                donorID         TEXT NOT NULL,
                staffID         TEXT NOT NULL,
                PRIMARY KEY(foodID),
                FOREIGN KEY(donorID) REFERENCES donorTbl(donorID),
                FOREIGN KEY(staffID) REFERENCES staffTbl(staffID))
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS giveFoodTbl(
                foodID          TEXT NOT NULL,
                recipientID     TEXT NOT NULL,
                staffID         TEXT NOT NULL,
                PRIMARY KEY(foodID,recipientID),
                FOREIGN KEY(foodID) REFERENCES foodDonatTbl(foodID),
                FOREIGN KEY(recipientID) REFERENCES recipientTbl(recipientID),
                FOREIGN KEY(staffID) REFERENCES staffTbl(staffID))
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipientTbl(
                recipientID         TEXT NOT NULL,
                recipientSurname    TEXT NOT NULL,
                recipientForename   TEXT NOT NULL,
                recipientContact    TEXT,
                PRIMARY KEY(recipientID))
            ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenditureTbl(
                expenditureID   TEXT NOT NULL,
                amount          REAL NOT NULL,
                details         TEXT NOT NULL,
                date            TEXT NOT NULL,
                staffID         TEXT NOT NULL,
                PRIMARY KEY(expenditureID),
                FOREIGN KEY(staffID) REFERENCES staffTbl(staffID))
            ''')

        connection.commit()
        connection.close()

        # Checks whether there is an 'admin' user in the database
        exists = executeSQL('SELECT staffID FROM staffTBL WHERE staffID = ?', ('admin',), False)
        if not exists:
            # Creates hashed/salted password
            salt = bcrypt.gensalt()
            hashedPass = bcrypt.hashpw('admin'.encode('utf-8'), salt)
            executeSQL('INSERT INTO staffTbl VALUES (?,?,?,?,?,?,?)', ('admin', '', 'Admin', '', 3, hashedPass, salt),
                       False)
