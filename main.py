# Python 3.8.1
# Requires prettytable, fpdf, tkcalendar, bcrypt to be installed

import tkinter as tk

from src.windows.login import loginWin
from src.windows.mainmenu import mainMenu
from src.sql import createDatabase
from src import config


def main():
    while True:
        win = tk.Tk()
        login = loginWin(win)
        win.mainloop()
        if login.authenticated:
            root = tk.Tk()
            config.app = mainMenu(root)
            root.mainloop()
        else:
            break


# First checks that the database file exists (function from SQL module)
# Creates DB if necessary,
# Then runs the main program

if __name__ == "__main__":
    createDatabase()
    main()
