import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime
import sqlite3
import random

from .. import config
from ..sql import loadDatabase, executeSQL
from ..utils import enableWindow, disableWindow, accesslevel, treeview_sort_column, center
from ..validation import validateFloat, validateDate
from ..report import donationReport


class donationWindow:
    # Creates view donations window for financial and food donations
    def __init__(self, root):
        self.root = root
        self.root.title('View Donations')
        self.root.iconbitmap(config.icon)
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.X)
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.closeWindow())

        # Creates title label, 'View Staff Records'
        self.titleLabel = tk.Label(
            self.frame, text='View Donation Records', font='none 11')
        # Creates refresh button, to reload data from the database, and the return button, to close the staff window
        # and return the user to the main menu
        self.refreshButton = ttk.Button(
            self.frame, text='↺', command=lambda: self.checkTab())
        self.returnButton = ttk.Button(
            self.frame, text='Main Menu', command=lambda: self.closeWindow())

        self.titleLabel.grid(row=0, column=1, sticky='ns')
        self.refreshButton.grid(row=0, column=2, pady=10, padx=40, sticky='e')
        self.returnButton.grid(row=0, column=0, pady=10,
                               padx=10, ipadx=10, ipady=2, sticky='w')

        self.frame.columnconfigure(1, weight=1)

        self.notebookFrame = tk.Frame(self.root)
        self.notebookFrame.pack(fill='both', expand=True)
        self.notebook = ttk.Notebook(self.notebookFrame)
        self.moneyTab = tk.Frame(self.notebook)
        self.foodTab = tk.Frame(self.notebook)
        self.notebook.add(self.moneyTab, text='Money')
        self.notebook.add(self.foodTab, text='Food')
        self.notebook.pack(fill='both', expand=True, pady=10, padx=10)

        ################# MONEY DONATION TAB ##################
        # Saves input search value from searchBox as searchVar
        self.searchVar = tk.StringVar()
        self.searchBox = ttk.Entry(self.moneyTab, textvariable=self.searchVar)
        # Creates a dropdown menu, with all the fields listed to search, set to donationID by default
        self.searchFieldVar = tk.StringVar()
        self.searchField = ttk.OptionMenu(self.moneyTab, self.searchFieldVar, 'DonationID', 'DonationID', 'Amount',
                                          'Cash/Bank', 'Reference No', 'Date', 'DonorID', 'StaffID')
        # Creates a 'search' button, which calls the search function when pressed
        self.searchButton = ttk.Button(
            self.moneyTab, text='Search', command=lambda: self.search())
        # Creates a 'Create report' button, which launches the report function
        self.reportButton = ttk.Button(
            self.moneyTab, text='Create Report', command=lambda: self.report())
        # Grids all the above labels, buttons and entry boxes to the frame
        self.searchField.grid(row=1, column=0, pady=10, padx=10, sticky='ew')
        self.searchBox.grid(row=1, column=1, pady=10, sticky='ew')
        self.searchButton.grid(row=1, column=2, pady=10,
                               padx=(10, 0), ipadx=10)
        self.reportButton.grid(row=1, column=4, padx=10,
                               ipadx=10, ipady=2, sticky='ew')

        # Creates the treeview, defining each column and naming its heading with the relevant field name
        columns = ('DonationID', 'Amount', 'Cash/Bank',
                   'Reference No', 'Date', 'DonorID', 'StaffID')
        self.tree = ttk.Treeview(
            self.moneyTab, columns=columns, show='headings')
        for col in columns:
            self.tree.column(col, width=100, minwidth=100)
            self.tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(
                self.tree, _col, False))
        self.tree.grid(row=2, column=0, sticky='ewns', rowspan=3,
                       columnspan=3, padx=(10, 0), pady=(10, 0))

        self.moneyTab.rowconfigure([2, 3, 4], weight=1)
        self.moneyTab.columnconfigure(1, weight=1)
        # Creates vertical and horizontal scrollbars, linking them to the treeview
        self.scrollbar = ttk.Scrollbar(
            self.moneyTab, orient='vertical', command=self.tree.yview)
        self.scrollbar.grid(row=2, column=3, sticky='ns', rowspan=3, pady=10)
        self.tree.configure(
            yscrollcommand=self.scrollbar.set, selectmode='browse')
        self.xscrollbar = ttk.Scrollbar(
            self.moneyTab, orient='horizontal', command=self.tree.xview)
        self.xscrollbar.grid(row=5, column=0, sticky='ew',
                             columnspan=4, pady=(0, 10))
        self.tree.configure(
            xscrollcommand=self.xscrollbar.set, selectmode='browse')
        # Creates the add, edit and delete donation buttons, which call their respective functions when clicked
        self.addDonationButton = ttk.Button(
            self.moneyTab, text='Add Donation', command=lambda: self.addDonation())
        self.editDonationButton = ttk.Button(
            self.moneyTab, text='Edit Donation', command=lambda: self.editDonation())
        self.delDonationButton = ttk.Button(
            self.moneyTab, text='Delete Donation', command=lambda: self.delDonation())
        # Grids the add, edit and delete buttons to the frame
        self.addDonationButton.grid(
            row=2, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.editDonationButton.grid(
            row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delDonationButton.grid(
            row=4, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        # Runs the search function when the user presses the 'enter' button (same as searchButton)
        self.root.bind('<Return>', lambda event: self.search())
        # Calls the function to load the records from the database
        loadDatabase(self.tree, 'donationsTbl', False)

        # Checks access level and disables relevant buttons
        accesslevel(2, self.addDonationButton, self.editDonationButton)
        accesslevel(3, self.delDonationButton)

        ################# FOOD DONATION TAB ###################
        # Saves input search value from searchBox as searchVar
        self.searchFoodVar = tk.StringVar()
        self.searchFoodBox = ttk.Entry(
            self.foodTab, textvariable=self.searchFoodVar)
        # Creates a dropdown menu, with all the fields listed to search, set to FoodID by default
        self.searchFoodFieldVar = tk.StringVar()
        self.searchFoodField = ttk.OptionMenu(self.foodTab, self.searchFoodFieldVar, 'FoodID', 'FoodID', 'Name',
                                              'DonationDate', 'ExpiryDate', 'GivenAway', 'DonorID', 'StaffID')
        # Creates a 'search' button, which calls the search function when pressed
        self.searchFoodButton = ttk.Button(
            self.foodTab, text='Search', command=lambda: self.foodSearch())
        # Grids all the above labels, buttons and entry boxes to the frame
        self.searchFoodField.grid(
            row=1, column=0, pady=10, padx=10, sticky='ew')
        self.searchFoodBox.grid(row=1, column=1, pady=10, sticky='ew')
        self.searchFoodButton.grid(
            row=1, column=2, pady=10, padx=(10, 0), ipadx=10)

        # Creates the treeview, defining each column and naming its heading with the relevant field name
        columns = ('FoodID', 'Name', 'DonationDate', 'ExpiryDate',
                   'GivenAway', 'DonorID', 'StaffID')
        self.foodTree = ttk.Treeview(
            self.foodTab, columns=columns, show='headings')
        for col in columns:
            self.foodTree.column(col, width=100, minwidth=100)
            self.foodTree.heading(col, text=col,
                                  command=lambda _col=col: treeview_sort_column(self.foodTree, _col, False))
        self.foodTree.grid(row=2, column=0, sticky='ewns',
                           rowspan=3, columnspan=3, padx=(10, 0), pady=(10, 0))

        self.foodTab.rowconfigure([2, 3, 4], weight=1)
        self.foodTab.columnconfigure(1, weight=1)
        # Creates vertical and horizontal scrollbars, linking them to the treeview
        self.scrollbarFood = ttk.Scrollbar(
            self.foodTab, orient='vertical', command=self.foodTree.yview)
        self.scrollbarFood.grid(
            row=2, column=3, sticky='ns', rowspan=3, pady=10)
        self.foodTree.configure(
            yscrollcommand=self.scrollbarFood.set, selectmode='browse')
        self.xscrollbarFood = ttk.Scrollbar(
            self.foodTab, orient='horizontal', command=self.foodTree.xview)
        self.xscrollbarFood.grid(
            row=5, column=0, sticky='ew', columnspan=4, pady=(0, 10))
        self.foodTree.configure(
            xscrollcommand=self.xscrollbarFood.set, selectmode='browse')
        # Creates the add, edit and delete donation buttons, which call their respective functions when clicked
        self.giveFoodButton = ttk.Button(
            self.foodTab, text='Give Away Food', command=lambda: self.giveFood())
        self.addFoodButton = ttk.Button(
            self.foodTab, text='Add Donation', command=lambda: self.addFood())
        self.editFoodButton = ttk.Button(
            self.foodTab, text='Edit Donation', command=lambda: self.editFood())
        self.delFoodButton = ttk.Button(
            self.foodTab, text='Delete Donation', command=lambda: self.delFood())
        # Grids the add, edit and delete buttons to the frame
        self.giveFoodButton.grid(
            row=1, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.addFoodButton.grid(row=2, column=4, padx=10,
                                ipadx=10, ipady=2, sticky='ew')
        self.editFoodButton.grid(
            row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delFoodButton.grid(row=4, column=4, padx=10,
                                ipadx=10, ipady=2, sticky='ew')
        # Calls the function to load the records from the database
        loadDatabase(self.foodTree, 'foodDonatTbl', False)

        # Checks access level and disables relevant buttons
        accesslevel(2, self.addFoodButton,
                    self.editFoodButton, self.giveFoodButton)
        accesslevel(3, self.delFoodButton)

        center(self.root)

    def checkTab(self):
        if self.notebook.tab(self.notebook.select(), 'text') == 'Money':
            currentTree = self.tree
            table = 'donationsTbl'
        else:
            table = 'foodDonatTbl'
            currentTree = self.foodTree
        loadDatabase(currentTree, table, True)

    def closeWindow(self):  # destroys Donation window, opens main menu
        self.root.destroy()
        config.app.enableMenu()

    def foodSearch(self):
        # Retrieves the search value and search field from the inputs
        # Adds a wildcard symbol, %, to the end of the search value
        search = '%' + str(self.searchFoodVar.get().strip().upper()) + '%'
        searchFieldVar = self.searchFoodFieldVar.get()
        if searchFieldVar == 'FoodID':
            searchField = 'foodID'
        elif searchFieldVar == 'Name':
            searchField = 'foodName'
        elif searchFieldVar == 'DonationDate':
            searchField = 'donatDate'
        elif searchFieldVar == 'ExpiryDate':
            searchField = 'expiryDate'
        elif searchFieldVar == 'GivenAway':
            searchField = 'givenAway'
        elif searchFieldVar == 'DonorID':
            searchField = 'donorID'
        elif searchFieldVar == 'StaffID':
            searchField = 'staffID'
        # Clears the treeview of all other records
        self.foodTree.delete(*self.foodTree.get_children())
        # Selects records from donationsTbl where the search field matches the search value
        records = executeSQL(
            'SELECT * FROM foodDonatTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records found into the treeview
            self.foodTree.insert('', 0, values=(
                i[0], i[1], i[2], i[3], i[4], i[5], i[6]))

    def giveFood(self):
        if self.foodTree.selection():  # Runs IF a record is selected from treeview
            for selected_item in self.foodTree.selection():
                # Finds records from donationsTbl that match the selected record
                donations = executeSQL('SELECT * FROM foodDonatTbl WHERE foodID=?',
                                       (self.foodTree.set(selected_item, '#1'),), False)
                foodID = donations[0]
                name = donations[1]
                givenAway = donations[4]
            if not givenAway:
                self.notebook.tab(0, state='disabled')
                disableWindow(self.returnButton, self.giveFoodButton, self.addFoodButton, self.editFoodButton,
                              self.delFoodButton)
                # Selects all recipientIDs, forenames and surnames, and saves them to a list
                recipients = executeSQL('SELECT recipientID,recipientForename,recipientSurname FROM recipientTbl', (),
                                        True)
                recipientIDs = [(item[0:3]) for item in recipients]
                self.donationWin = tk.Toplevel(self.root)
                self.donationWin.lift(self.root)
                self.donationWin.title('Edit Food Donation')
                self.donationWin.iconbitmap(config.icon)
                self.donationWin.protocol('WM_DELETE_WINDOW', lambda: (self.notebook.tab(0, state='normal'),
                                                                       enableWindow(self.donationWin,
                                                                                    self.giveFoodButton,
                                                                                    self.returnButton,
                                                                                    self.addFoodButton,
                                                                                    self.editFoodButton,
                                                                                    self.delFoodButton),
                                                                       accesslevel(2, self.addFoodButton,
                                                                                   self.editFoodButton,
                                                                                   self.giveFoodButton),
                                                                       accesslevel(3, self.delFoodButton)))
                self.giveFoodFrame = tk.Frame(self.donationWin)
                self.giveFoodFrame.pack()
                # Creates all the labels and entry boxes for each field
                self.detailLabel = tk.Label(
                    self.giveFoodFrame, text='Give Away Food Details:', font='none 11 bold')
                self.foodIDLabel = tk.Label(
                    self.giveFoodFrame, text='FoodID:', font='none 11')
                self.foodIDInsert = tk.Label(
                    self.giveFoodFrame, text=foodID, font='none 11')
                self.nameLabel = tk.Label(
                    self.giveFoodFrame, text='Food Name:', font='none 11')
                self.nameInsert = tk.Label(
                    self.giveFoodFrame, text=name, font='none 11')
                self.recipientIDLabel = tk.Label(
                    self.giveFoodFrame, text='RecipientID:', font='none 11')
                # Creates a dropdown menu populated with all the recipientIDs that we retrieved earlier
                self.recipientIDVar = tk.StringVar()
                # self.recipientIDVar.set('Anonymous')
                if recipientIDs:
                    self.recipientIDDropdown = ttk.OptionMenu(self.giveFoodFrame, self.recipientIDVar, 'Anonymous',
                                                              *recipientIDs,
                                                              command=lambda x: (self.recipientIDVar.set(
                                                                  self.recipientIDVar.get()[2:9])))
                else:
                    self.recipientIDDropdown = tk.Label(self.giveFoodFrame, textvariable=self.recipientIDVar,
                                                        font='none 11')
                self.staffIDLabel = tk.Label(
                    self.giveFoodFrame, text='StaffID:', font='none 11')
                self.staffIDInsert = tk.Label(
                    self.giveFoodFrame, text=config.userID, font='none 11')
                # Creates text variable and error label to output any errors
                self.errorVar = tk.StringVar()
                self.errorLabel = tk.Label(
                    self.giveFoodFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
                # Creates save button, which calls the function saveGiveFood when pressed
                self.saveButton = ttk.Button(self.giveFoodFrame, text='Save Record',
                                             command=lambda: self.saveGiveFood(foodID, name))
                # Grids all the labels, entry boxes, buttons and dropdowns to the frame
                self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
                self.foodIDLabel.grid(
                    row=1, column=0, sticky='E', padx=(10, 0))
                self.foodIDInsert.grid(row=1, column=1, padx=(0, 10))
                self.nameLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
                self.nameInsert.grid(row=2, column=1, padx=(0, 10))
                self.recipientIDLabel.grid(
                    row=3, column=0, sticky='E', padx=(10, 0))
                self.recipientIDDropdown.grid(
                    row=3, column=1, padx=(0, 10), sticky='ew')
                self.staffIDLabel.grid(
                    row=4, column=0, sticky='E', padx=(10, 0))
                self.staffIDInsert.grid(row=4, column=1, padx=(0, 10))
                self.errorLabel.grid(row=5, column=0, columnspan=2)
                self.saveButton.grid(
                    row=6, column=0, columnspan=2, pady=(0, 10))

                # Runs the save function when the user presses the 'enter' button (same as saveButton)
                self.donationWin.bind(
                    '<Return>', lambda event: self.saveGiveFood(foodID, name))

                center(self.donationWin)

            else:
                tk.messagebox.showerror('Error', 'Item already given away')

        else:
            # Outputs error message is no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')

    def saveGiveFood(self, foodID, name):
        recipientID = self.recipientIDVar.get()
        staffID = config.userID
        if tk.messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nFoodID:\t\t' +
                                  foodID + '\nName:\t\t' + name + '\nRecipientID:\t' + recipientID +
                                  '\nStaffID:\t\t' + staffID):
            try:
                # Insert record into donationsTbl
                executeSQL('INSERT INTO giveFoodTbl VALUES (?,?,?)',
                           (foodID, recipientID, staffID), False)
                executeSQL(
                    'UPDATE foodDonatTbl SET givenAway=? WHERE foodID = ?', (1, foodID), False)
                # Reloads records into treeview
                loadDatabase(self.foodTree, 'foodDonatTbl', False)
                # Destroys add donation window and returns to view donations window
                self.notebook.tab(0, state='normal')
                enableWindow(self.donationWin, self.giveFoodButton, self.returnButton, self.addFoodButton,
                             self.editFoodButton, self.delFoodButton)
                accesslevel(2, self.addFoodButton,
                            self.editFoodButton, self.giveFoodButton)
                accesslevel(3, self.delFoodButton)
                tk.messagebox.showinfo('Success!', 'Given Away')
            except sqlite3.IntegrityError:
                # Outputs error if donationID is not unique
                self.errorVar.set(
                    'Error: Failed To Update Database.\nPlease Try Again')

    def addFood(self):
        self.notebook.tab(0, state='disabled')
        disableWindow(self.returnButton, self.giveFoodButton, self.addFoodButton, self.editFoodButton,
                      self.delFoodButton)
        # Selects all donorIDs, forenames and surnames, and saves them to a list
        donors = executeSQL(
            'SELECT donorID,donorForename,donorSurname FROM donorTbl', (), True)
        donorIDs = [(item[0:3]) for item in donors]
        self.donationWin = tk.Toplevel(self.root)
        self.donationWin.lift(self.root)
        self.donationWin.title('Add Food Donation')
        self.donationWin.iconbitmap(config.icon)
        self.donationWin.protocol('WM_DELETE_WINDOW', lambda: (self.notebook.tab(0, state='normal'),
                                                               enableWindow(self.donationWin, self.giveFoodButton,
                                                                            self.returnButton,
                                                                            self.addFoodButton, self.editFoodButton,
                                                                            self.delFoodButton),
                                                               accesslevel(2, self.addFoodButton, self.editFoodButton,
                                                                           self.giveFoodButton),
                                                               accesslevel(3, self.delFoodButton)))
        self.addDonationFrame = tk.Frame(self.donationWin)
        self.addDonationFrame.pack()
        # Creates all the labels and entry boxes for each field
        self.detailLabel = tk.Label(
            self.addDonationFrame, text='Enter Donation Details:', font='none 11 bold')
        self.nameLabel = tk.Label(self.addDonationFrame,
                                  text='Food Name:', font='none 11')
        self.nameVar = tk.StringVar()
        self.nameBox = ttk.Entry(
            self.addDonationFrame, textvariable=self.nameVar)
        self.dateLabel = tk.Label(self.addDonationFrame,
                                  text='Date:', font='none 11')
        self.dateVar = tk.StringVar()
        # Creates a calendar widget to pick the date from
        self.calendar = DateEntry(self.addDonationFrame, state='readonly',
                                  date_pattern='DD/MM/YYYY', textvariable=self.dateVar,
                                  showweeknumbers=False, maxdate=datetime.today())
        self.expiryDateLabel = tk.Label(
            self.addDonationFrame, text='Expiry Date:', font='none 11')
        self.expiryDateVar = tk.StringVar()
        # Creates a calendar widget to pick the date from
        self.expiryCalendar = DateEntry(self.addDonationFrame, state='readonly',
                                        date_pattern='DD/MM/YYYY', textvariable=self.expiryDateVar,
                                        showweeknumbers=False, mindate=datetime.today())
        self.donorIDLabel = tk.Label(
            self.addDonationFrame, text='DonorID:', font='none 11')
        # Creates a dropdown menu populated with all the donorIDs that we retrieved earlier
        self.donorIDVar = tk.StringVar()
        # self.donorIDVar.set('Anonymous')
        if donorIDs:
            self.donorIDDropdown = ttk.OptionMenu(self.addDonationFrame, self.donorIDVar, 'Anonymous', *donorIDs,
                                                  command=lambda x: (self.donorIDVar.set(self.donorIDVar.get()[2:9])))
        else:
            self.donorIDDropdown = tk.Label(
                self.addDonationFrame, textvariable=self.donorIDVar, font='none 11')
        # Creates text variable and error label to output any errors
        self.errorVar = tk.StringVar()
        self.errorLabel = tk.Label(
            self.addDonationFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
        # Creates save button, which calls the function saveDonation when pressed
        self.saveButton = ttk.Button(self.addDonationFrame, text='Save Food Donation',
                                     command=lambda: self.saveFoodDonation())
        # Grids all the labels, entry boxes, buttons and dropdowns to the frame
        self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
        self.nameLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
        self.nameBox.grid(row=1, column=1, padx=(0, 10))
        self.dateLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
        self.calendar.grid(row=2, column=1, padx=(0, 10), sticky='ew')
        self.expiryDateLabel.grid(row=3, column=0, sticky='E', padx=(10, 0))
        self.expiryCalendar.grid(row=3, column=1, padx=(0, 10), sticky='ew')
        self.donorIDLabel.grid(row=4, column=0, sticky='E', padx=(10, 0))
        self.donorIDDropdown.grid(row=4, column=1, padx=(0, 10), sticky='ew')
        self.errorLabel.grid(row=5, column=0, columnspan=2)
        self.saveButton.grid(row=6, column=0, columnspan=2, pady=(0, 10))
        # Runs the save function when the user presses the 'enter' button (same as saveButton)
        self.donationWin.bind(
            '<Return>', lambda event: self.saveFoodDonation())

        center(self.donationWin)

    def saveFoodDonation(self):
        # Retrieves all inputs from the form
        name = self.nameVar.get().title().strip()
        date = self.dateVar.get()
        expiryDate = self.expiryDateVar.get()
        donorID = self.donorIDVar.get()
        # Checks that all fields have been entered
        if name:
            staffID = config.userID
            foodID = 'FD' + \
                str(''.join(['%s' % random.randint(0, 9)
                    for num in range(0, 5)]))
            # Comfirmation box asks user to confirm that inputs are all correct
            if tk.messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nFoodID:\t\t' +
                                      foodID + '\nName:\t\t' + name + '\nDate Donated:\t' +
                                      date + '\nExpiry Date:\t' + expiryDate + '\nDonorID:\t\t' +
                                      donorID + '\nStaffID:\t\t' + staffID):
                try:
                    # Insert record into donationsTbl
                    executeSQL('INSERT INTO foodDonatTbl VALUES (?,?,?,?,?,?,?)',
                               (foodID, name, date, expiryDate, False, donorID, staffID), False)
                    # Reloads records into treeview
                    loadDatabase(self.foodTree, 'foodDonatTbl', False)
                    # Destroys add donation window and returns to view donations window
                    self.notebook.tab(0, state='normal')
                    enableWindow(self.donationWin, self.giveFoodButton, self.returnButton, self.addFoodButton,
                                 self.editFoodButton, self.delFoodButton)
                    accesslevel(2, self.addFoodButton,
                                self.editFoodButton, self.giveFoodButton)
                    accesslevel(3, self.delFoodButton)
                    tk.messagebox.showinfo('Success!', 'New Donation Saved')
                except sqlite3.IntegrityError:
                    # Outputs error if donationID is not unique
                    self.errorVar.set(
                        'Error: Failed To Update Database.\nPlease Try Again')
        else:
            # Outputs error if not all fields are filled
            self.errorVar.set('Error: Please Fill All Fields')

    def editFood(self):
        if self.foodTree.selection():  # Runs IF a record is selected from treeview
            self.notebook.tab(0, state='disabled')
            disableWindow(self.returnButton, self.giveFoodButton, self.addFoodButton, self.editFoodButton,
                          self.delFoodButton)
            for selected_item in self.foodTree.selection():
                # Finds records from donationsTbl that match the selected record
                donations = executeSQL('SELECT * FROM foodDonatTbl WHERE foodID=?',
                                       (self.foodTree.set(selected_item, '#1'),), False)
                foodID = donations[0]
                name = donations[1]
                date = donations[2]
                expiryDate = donations[3]
                donorID = donations[5]
                staffID = donations[6]

            # Selects all donorIDs, forenames and surnames, and saves them to a list
            donors = executeSQL(
                'SELECT donorID,donorForename,donorSurname FROM donorTbl', (), True)
            donorIDs = [(item[0:3]) for item in donors]
            self.donationWin = tk.Toplevel(self.root)
            self.donationWin.lift(self.root)
            self.donationWin.title('Edit Food Donation')
            self.donationWin.iconbitmap(config.icon)
            self.donationWin.protocol('WM_DELETE_WINDOW', lambda: (self.notebook.tab(0, state='normal'),
                                                                   enableWindow(self.donationWin, self.giveFoodButton,
                                                                                self.returnButton,
                                                                                self.addFoodButton, self.editFoodButton,
                                                                                self.delFoodButton),
                                                                   accesslevel(2, self.addFoodButton,
                                                                               self.editFoodButton,
                                                                               self.giveFoodButton),
                                                                   accesslevel(3, self.delFoodButton)))
            self.editDonationFrame = tk.Frame(self.donationWin)
            self.editDonationFrame.pack()
            # Creates all the labels and entry boxes for each field
            self.detailLabel = tk.Label(
                self.editDonationFrame, text='Edit Donation Details:', font='none 11 bold')
            self.foodIDLabel = tk.Label(
                self.editDonationFrame, text='FoodID:', font='none 11')
            self.foodIDInsert = tk.Label(
                self.editDonationFrame, text=foodID, font='none 11')
            self.nameLabel = tk.Label(
                self.editDonationFrame, text='Food Name:', font='none 11')
            self.nameVar = tk.StringVar()
            self.nameBox = ttk.Entry(
                self.editDonationFrame, textvariable=self.nameVar)
            self.dateLabel = tk.Label(
                self.editDonationFrame, text='Date:', font='none 11')
            self.dateVar = tk.StringVar()
            # Creates a calendar widget to pick the date from
            self.calendar = DateEntry(self.editDonationFrame, state='readonly',
                                      date_pattern='DD/MM/YYYY', textvariable=self.dateVar,
                                      showweeknumbers=False, maxdate=datetime.today())
            self.expiryDateLabel = tk.Label(
                self.editDonationFrame, text='Expiry Date:', font='none 11')
            self.expiryDateVar = tk.StringVar()
            # Creates a calendar widget to pick the date from
            self.expiryCalendar = DateEntry(self.editDonationFrame, state='readonly',
                                            date_pattern='DD/MM/YYYY', textvariable=self.expiryDateVar,
                                            showweeknumbers=False, mindate=datetime.today())
            self.donorIDLabel = tk.Label(
                self.editDonationFrame, text='DonorID:', font='none 11')
            # Creates a dropdown menu populated with all the donorIDs that we retrieved earlier
            self.donorIDVar = tk.StringVar()
            if donorIDs:
                self.donorIDDropdown = ttk.OptionMenu(self.editDonationFrame, self.donorIDVar, 'Anonymous', *donorIDs,
                                                      command=lambda x: (
                                                          self.donorIDVar.set(self.donorIDVar.get()[2:9])))
            else:
                self.donorIDDropdown = tk.Label(
                    self.editDonationFrame, textvariable=self.donorIDVar, font='none 11')
            self.staffIDLabel = tk.Label(
                self.editDonationFrame, text='StaffID:', font='none 11')
            self.staffIDInsert = tk.Label(
                self.editDonationFrame, text=staffID, font='none 11')
            # Creates text variable and error label to output any errors
            self.errorVar = tk.StringVar()
            self.errorLabel = tk.Label(
                self.editDonationFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
            # Creates save button, which calls the function saveDonation when pressed
            self.saveButton = ttk.Button(self.editDonationFrame, text='Update Donation',
                                         command=lambda: self.saveEditFoodDonation(foodID, staffID))
            # Grids all the labels, entry boxes, buttons and dropdowns to the frame
            self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
            self.foodIDLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
            self.foodIDInsert.grid(row=1, column=1, padx=(0, 10))
            self.nameLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
            self.nameBox.grid(row=2, column=1, padx=(0, 10))
            self.dateLabel.grid(row=3, column=0, sticky='E', padx=(10, 0))
            self.calendar.grid(row=3, column=1, padx=(0, 10), sticky='ew')
            self.expiryDateLabel.grid(
                row=4, column=0, sticky='E', padx=(10, 0))
            self.expiryCalendar.grid(
                row=4, column=1, padx=(0, 10), sticky='ew')
            self.donorIDLabel.grid(row=5, column=0, sticky='E', padx=(10, 0))
            self.donorIDDropdown.grid(
                row=5, column=1, padx=(0, 10), sticky='ew')
            self.staffIDLabel.grid(row=6, column=0, sticky='E', padx=(10, 0))
            self.staffIDInsert.grid(row=6, column=1, padx=(0, 10))
            self.errorLabel.grid(row=7, column=0, columnspan=2)
            self.saveButton.grid(row=8, column=0, columnspan=2, pady=(0, 10))

            self.nameBox.insert(tk.INSERT, name)
            self.calendar.set_date(date)
            self.expiryCalendar.set_date(expiryDate)
            self.donorIDVar.set(donorID)
            # Runs the save function when the user presses the 'enter' button (same as saveButton)
            self.donationWin.bind(
                '<Return>', lambda event: self.saveEditFoodDonation(foodID, staffID))

            center(self.donationWin)

        else:
            # Outputs error message is no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')

    def saveEditFoodDonation(self, foodID, staffID):
        # Retrieves all inputs from the form
        name = self.nameVar.get().title().strip()
        date = self.dateVar.get()
        expiryDate = self.expiryDateVar.get()
        donorID = self.donorIDVar.get()
        # Checks that all fields have been entered
        if name:
            # Comfirmation box asks user to confirm that inputs are all correct
            if tk.messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nFoodID:\t\t' +
                                      foodID + '\nName:\t\t' + name + '\nDate Donated:\t' +
                                      date + '\nExpiry Date:\t' + expiryDate + '\nDonorID:\t\t' +
                                      donorID + '\nStaffID:\t\t' + staffID):
                try:
                    # Insert record into donationsTbl
                    executeSQL('''UPDATE foodDonatTbl SET foodName = ?, donatDate = ?,
                                    expiryDate = ?, donorID = ? WHERE foodID = ?''',
                               (name, date, expiryDate, donorID, foodID), False)
                    # Reloads records into treeview
                    loadDatabase(self.foodTree, 'foodDonatTbl', False)
                    # Destroys add donation window and returns to view donations window
                    self.notebook.tab(0, state='normal')
                    enableWindow(self.donationWin, self.giveFoodButton, self.returnButton, self.addFoodButton,
                                 self.editFoodButton, self.delFoodButton)
                    accesslevel(2, self.addFoodButton,
                                self.editFoodButton, self.giveFoodButton)
                    accesslevel(3, self.delFoodButton)
                    tk.messagebox.showinfo('Success!', 'Donation Updated')
                except sqlite3.IntegrityError:
                    # Outputs error if donationID is not unique
                    self.errorVar.set(
                        'Error: Failed To Update Database.\nPlease Try Again')
        else:
            # Outputs error if not all fields are filled
            self.errorVar.set('Error: Please Fill All Fields')

    def delFood(self):
        if self.foodTree.selection():
            # Retreives the donationID from the record selected in the treeview
            for selected_item in self.foodTree.selection():
                foodID = self.foodTree.set(selected_item, '#1')
            existsForeign = executeSQL(
                'SELECT * FROM giveFoodTbl WHERE foodID = ?', (foodID,), False)
            if not existsForeign:
                # Asks the user for confimation that they want to permanently delete this record
                if tk.messagebox.askokcancel('Delete', 'Are you sure you want to permanently delete this record?'):
                    # Removes the recird from foodDonatTbl
                    executeSQL(
                        'DELETE FROM foodDonatTbl WHERE foodID=?', (foodID,), False)
                    # Removes the record from the treeview
                    self.foodTree.delete(selected_item)
            else:
                tk.messagebox.showerror(
                    'Error', 'Food Item Already Given Away')
        else:
            # Outputs error message is no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')

    def search(self):
        # Retrieves the search value and search field from the inputs
        # Adds a wildcard symbol, %, to the end of the search value
        search = '%' + str(self.searchVar.get().strip().upper()) + '%'
        searchFieldVar = self.searchFieldVar.get()
        if searchFieldVar == 'DonationID':
            searchField = 'donationID'
        elif searchFieldVar == 'Amount':
            searchField = 'amount'
        elif searchFieldVar == 'Cash/Bank':
            searchField = 'cashorbank'
        elif searchFieldVar == 'Reference No':
            searchField = 'referenceNo'
        elif searchFieldVar == 'Date':
            searchField = 'date'
        elif searchFieldVar == 'DonorID':
            searchField = 'donorID'
        elif searchFieldVar == 'StaffID':
            searchField = 'staffID'
        # Clears the treeview of all other records
        self.tree.delete(*self.tree.get_children())
        # Selects records from donationsTbl where the search field matches the search value
        records = executeSQL(
            'SELECT * FROM donationsTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records found into the treeview
            self.tree.insert('', 0, values=(
                i[0], i[1], i[2], i[3], i[4], i[5], i[6]))

    def addDonation(self):
        self.notebook.tab(1, state='disabled')
        disableWindow(self.reportButton, self.returnButton, self.addDonationButton, self.editDonationButton,
                      self.delDonationButton)
        # Selects all donorIDs, forenames and surnames, and saves them to a list
        donors = executeSQL(
            'SELECT donorID,donorForename,donorSurname FROM donorTbl', (), True)
        donorIDs = [(item[0:3]) for item in donors]
        if donorIDs:
            self.donationWin = tk.Toplevel(self.root)
            self.donationWin.lift(self.root)
            self.donationWin.title('Add Donations')
            self.donationWin.iconbitmap(config.icon)
            self.donationWin.protocol('WM_DELETE_WINDOW', lambda: (self.notebook.tab(1, state='normal'),
                                                                   enableWindow(self.donationWin, self.reportButton,
                                                                                self.returnButton,
                                                                                self.addDonationButton,
                                                                                self.editDonationButton,
                                                                                self.delDonationButton),
                                                                   accesslevel(2, self.addDonationButton,
                                                                               self.editDonationButton),
                                                                   accesslevel(3, self.delDonationButton)))
            self.addDonationFrame = tk.Frame(self.donationWin)
            self.addDonationFrame.pack()
            # Creates all the labels and entry boxes for each field
            self.detailLabel = tk.Label(
                self.addDonationFrame, text='Enter Donation Details:', font='none 11 bold')
            self.amountLabel = tk.Label(
                self.addDonationFrame, text='Amount:', font='none 11')
            self.amountVar = tk.StringVar()
            self.amountBox = ttk.Entry(
                self.addDonationFrame, textvariable=self.amountVar)
            self.cashbankLabel = tk.Label(
                self.addDonationFrame, text='Cash or Bank?', font='none 11')
            self.cashbankVar = tk.IntVar()
            # Creates radio buttons, and gives them commands to show/hide the reference no. label and entry box
            self.cashRadio = ttk.Radiobutton(self.addDonationFrame, text='Cash', variable=self.cashbankVar, value=0,
                                             command=lambda: (self.referenceBox.delete(0, tk.END),
                                                              self.referenceBox.config(state='readonly')))
            self.bankRadio = ttk.Radiobutton(self.addDonationFrame, text='Bank', variable=self.cashbankVar, value=1,
                                             command=lambda: (self.referenceBox.config(state='normal')))
            self.referenceLabel = tk.Label(
                self.addDonationFrame, text='Reference No:', font='none 11')
            self.referenceVar = tk.StringVar()
            self.referenceBox = ttk.Entry(
                self.addDonationFrame, textvariable=self.referenceVar)
            self.dateLabel = tk.Label(self.addDonationFrame,
                                      text='Date:', font='none 11')
            self.dateVar = tk.StringVar()
            # Creates a calendar widget to pick the date from
            self.calendar = DateEntry(self.addDonationFrame, state='readonly',
                                      date_pattern='DD/MM/YYYY', textvariable=self.dateVar,
                                      showweeknumbers=False, maxdate=datetime.today())
            self.donorIDLabel = tk.Label(
                self.addDonationFrame, text='DonorID:', font='none 11')
            # Creates a dropdown menu populated with all the donorIDs that we retrieved earlier
            self.donorIDVar = tk.StringVar()
            self.donorIDDropdown = ttk.OptionMenu(self.addDonationFrame, self.donorIDVar, 'Select...', *donorIDs,
                                                  command=lambda x: (self.donorIDVar.set(self.donorIDVar.get()[2:9])))
            # self.donorIDVar.set('Select...')
            self.staffIDLabel = tk.Label(
                self.addDonationFrame, text='staffID:', font='none 11')
            self.staffIDEntered = tk.Label(
                self.addDonationFrame, text=config.userID, font='none 11')
            # Creates text variable and error label to output any errors
            self.errorVar = tk.StringVar()
            self.errorLabel = tk.Label(
                self.addDonationFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
            # Creates save button, which calls the function saveDonation when pressed
            self.saveButton = ttk.Button(self.addDonationFrame, text='Save New Donation',
                                         command=lambda: self.saveDonation())
            # Grids all the labels, entry boxes, buttons and dropdowns to the frame
            self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
            self.amountLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
            self.amountBox.grid(row=1, column=1, padx=(0, 10))
            self.cashbankLabel.grid(
                row=2, column=0, rowspan=2, sticky='E', padx=(10, 0))
            self.cashRadio.grid(row=2, column=1)
            self.bankRadio.grid(row=3, column=1)
            self.referenceLabel.grid(
                row=4, column=0, sticky='E', padx=(10, 0)),
            self.referenceBox.grid(row=4, column=1, padx=(0, 10))
            self.referenceBox.config(state='readonly')
            self.dateLabel.grid(row=5, column=0, sticky='E', padx=(10, 0))
            self.calendar.grid(row=5, column=1, padx=(0, 10), sticky='ew')
            self.donorIDLabel.grid(row=6, column=0, sticky='E', padx=(10, 0))
            self.donorIDDropdown.grid(
                row=6, column=1, padx=(0, 10), sticky='ew')
            self.staffIDLabel.grid(row=7, column=0, sticky='E', padx=(10, 0))
            self.staffIDEntered.grid(row=7, column=1, padx=(0, 10))
            self.errorLabel.grid(row=8, column=0, columnspan=2)
            self.saveButton.grid(row=9, column=0, columnspan=2, pady=(0, 10))
            # Runs the save function when the user presses the 'enter' button (same as saveButton)
            self.donationWin.bind(
                '<Return>', lambda event: self.saveDonation())

            center(self.donationWin)
        else:
            tk.messagebox.showerror('Error', 'No donors registered')
            self.closeWindow()

    def saveDonation(self):
        # Retrieves all inputs from the form
        cashorbankVar = self.cashbankVar.get()
        cashorbank = 'Cash' if cashorbankVar == 0 else 'Bank'
        referenceNo = self.referenceVar.get().strip()
        date = self.dateVar.get()

        # Checks that amount is valid
        amount, amountValid = validateFloat(self.amountVar.get().strip())

        if not amountValid:
            self.errorVar.set('Error: Invalid Amount Input')

        # Checks that date is in the correct format
        dateValid = validateDate(date, self.errorVar)

        # Checks that all fields have been entered
        if dateValid and amountValid:
            donorID = self.donorIDVar.get()
            staffID = config.userID
            # Checks whether a reference no is required
            refneeded = True if cashorbankVar == 1 else False
            # Checks that reference no. is given if required
            refgood = True if (refneeded and referenceNo) or (
                not refneeded) else False
            if refgood and cashorbank and donorID != 'Select...':
                # Generates a random donationID, using the random module
                donationID = 'DN' + \
                    str(''.join(['%s' % random.randint(0, 9)
                        for num in range(0, 5)]))
                # Comfirmation box asks user to confirm that inputs are all correct
                if tk.messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nDonationID:\t' +
                                          donationID + '\nAmount:\t\t' + str(amount) +
                                          '\nCash or Bank?\t' + cashorbank + '\nReference No:\t' +
                                          referenceNo + '\nDate:\t\t' + date +
                                          '\nDonorID:\t\t' + donorID + '\nStaffID:\t\t' + staffID):
                    try:
                        # Insert record into donationsTbl
                        executeSQL('INSERT INTO donationsTbl VALUES (?,?,?,?,?,?,?)',
                                   (donationID, float(amount), cashorbank, referenceNo, date, donorID, staffID), False)
                        # Reloads records into treeview
                        loadDatabase(self.tree, 'donationsTbl', False)
                        # Destroys add donation window and returns to view donations window
                        self.notebook.tab(1, state='normal')
                        enableWindow(self.donationWin, self.reportButton, self.returnButton, self.addDonationButton,
                                     self.editDonationButton, self.delDonationButton)
                        accesslevel(2, self.addDonationButton,
                                    self.editDonationButton)
                        accesslevel(3, self.delDonationButton)
                        tk.messagebox.showinfo(
                            'Success!', 'New Donation Saved')
                    except sqlite3.IntegrityError:
                        # Outputs error if donationID is not unique
                        self.errorVar.set(
                            'Error: Failed To Update Database.\nPlease Try Again')
            else:
                # Outputs error if not all fields are filled
                self.errorVar.set('Error: Please Fill All Fields')

    def editDonation(self):
        if self.tree.selection():  # Runs IF a record is selected from treeview
            self.notebook.tab(1, state='disabled')
            disableWindow(self.reportButton, self.returnButton, self.addDonationButton, self.editDonationButton,
                          self.delDonationButton)
            for selected_item in self.tree.selection():
                # Finds records from donationsTbl that match the selected record
                donations = executeSQL('SELECT * FROM donationsTbl WHERE donationID=?',
                                       (self.tree.set(selected_item, '#1'),), False)
                donationID = donations[0]
                amount = donations[1]
                cashorbank = donations[2]
                referenceNo = donations[3]
                date = donations[4]
                donorID = donations[5]
                staffID = donations[6]
            # Selects all donorIDs and saves them to a list
            donors = executeSQL(
                'SELECT donorID,donorForename,donorSurname FROM donorTbl', (), True)
            donorIDs = [(item[0:3]) for item in donors]
            cashorbank = 0 if cashorbank == 'Cash' else 1
            self.donationWin = tk.Toplevel(self.root)
            self.donationWin.title('Edit Donation')
            self.donationWin.iconbitmap(config.icon)
            self.donationWin.protocol('WM_DELETE_WINDOW', lambda: (self.notebook.tab(1, state='normal'),
                                                                   enableWindow(self.donationWin, self.reportButton,
                                                                                self.returnButton,
                                                                                self.addDonationButton,
                                                                                self.editDonationButton,
                                                                                self.delDonationButton),
                                                                   accesslevel(2, self.addDonationButton,
                                                                               self.editDonationButton),
                                                                   accesslevel(3, self.delDonationButton)))
            self.editDonationFrame = tk.Frame(self.donationWin)
            self.editDonationFrame.pack()
            # Creates all the labels and entry boxes for each field
            self.detailLabel = tk.Label(
                self.editDonationFrame, text='Edit Donation Details:', font='none 11 bold')
            self.donationIDLabel = tk.Label(
                self.editDonationFrame, text='DonationID:', font='none 11')
            self.donationIDEntered = tk.Label(
                self.editDonationFrame, text=donationID, font='none 11')
            self.amountLabel = tk.Label(
                self.editDonationFrame, text='Amount:', font='none 11')
            self.amountVar = tk.StringVar()
            self.amountBox = ttk.Entry(
                self.editDonationFrame, textvariable=self.amountVar)
            self.cashbankLabel = tk.Label(
                self.editDonationFrame, text='Cash or Bank?', font='none 11')
            # Creates radio buttons, and gives them commands to show/hide the reference no. label and entry boxes
            # depending on which option is selected.
            self.cashbankVar = tk.IntVar()
            self.cashRadio = ttk.Radiobutton(self.editDonationFrame, text='Cash', variable=self.cashbankVar, value=0,
                                             command=lambda: (self.referenceBox.delete(0, tk.END),
                                                              self.referenceBox.config(state='readonly')))
            self.bankRadio = ttk.Radiobutton(self.editDonationFrame, text='Bank', variable=self.cashbankVar, value=1,
                                             command=lambda: (self.referenceBox.config(state='normal')))
            self.referenceLabel = tk.Label(
                self.editDonationFrame, text='Reference No:', font='none 11')
            self.referenceVar = tk.StringVar()
            self.referenceBox = ttk.Entry(
                self.editDonationFrame, textvariable=self.referenceVar)
            self.dateLabel = tk.Label(
                self.editDonationFrame, text='Date:', font='none 11')
            self.dateVar = tk.StringVar()
            # Creates a calendar widget to pick the date from
            self.calendar = DateEntry(self.editDonationFrame, state='readonly',
                                      date_pattern='DD/MM/YYYY', textvariable=self.dateVar,
                                      showweeknumbers=False, maxdate=datetime.today())
            self.donorIDLabel = tk.Label(
                self.editDonationFrame, text='DonorID:', font='none 11')
            # Creates a dropdown menu populated with all the donorIDs that we retrieved earlier
            self.donorIDVar = tk.StringVar()
            self.donorIDDropdown = ttk.OptionMenu(self.editDonationFrame, self.donorIDVar, 'Select...', *donorIDs,
                                                  command=lambda x: (self.donorIDVar.set(self.donorIDVar.get()[2:9])))
            # self.donorIDVar.set('Select...')
            self.staffIDLabel = tk.Label(
                self.editDonationFrame, text='StaffID:', font='none 11')
            self.staffIDEntered = tk.Label(
                self.editDonationFrame, text=staffID, font='none 11')
            # Creates a text variable and error label to output any errors to
            self.errorVar = tk.StringVar()
            self.errorLabel = tk.Label(
                self.editDonationFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
            # Creaets a save button, which calls the function saveEditDonation when pressed
            self.saveButton = ttk.Button(self.editDonationFrame, text='Update Donation',
                                         command=lambda: self.saveEditDonation(donationID, staffID))
            # Grids all the labels, entry boxes, buttons and dropdowns to the frame
            self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
            self.donationIDLabel.grid(
                row=1, column=0, sticky='E', padx=(10, 0))
            self.donationIDEntered.grid(row=1, column=1, padx=(0, 10))
            self.amountLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
            self.amountBox.grid(row=2, column=1, padx=(0, 10))
            self.cashbankLabel.grid(
                row=3, column=0, rowspan=2, sticky='E', padx=(10, 0))
            self.cashRadio.grid(row=3, column=1)
            self.bankRadio.grid(row=4, column=1)
            self.referenceLabel.grid(
                row=5, column=0, sticky='E', padx=(10, 0)),
            self.referenceBox.grid(row=5, column=1, padx=(0, 10))
            self.referenceBox.config(state='readonly')
            self.dateLabel.grid(row=6, column=0, sticky='E', padx=(10, 0))
            self.calendar.grid(row=6, column=1, padx=(0, 10), sticky='ew')
            self.donorIDLabel.grid(row=7, column=0, sticky='E', padx=(10, 0))
            self.donorIDDropdown.grid(
                row=7, column=1, padx=(0, 10), sticky='ew')
            self.staffIDLabel.grid(row=8, column=0, sticky='E', padx=(10, 0))
            self.staffIDEntered.grid(row=8, column=1, padx=(0, 10))
            self.errorLabel.grid(row=9, column=0, columnspan=2)
            self.saveButton.grid(row=10, column=0, columnspan=2, pady=(0, 10))
            # Inserts all the current values into the entry boxes
            self.amountBox.insert(tk.INSERT, amount)
            self.cashbankVar.set(cashorbank)
            self.referenceVar.set(referenceNo)
            self.calendar.set_date(date)
            self.donorIDVar.set(donorID)
            # Grids the reference no. label and entry box if 'bank' is selected
            if cashorbank == 1:
                self.referenceBox.config(state='normal')
            # Runs the save function when the user presses the 'enter' key (same as saveButton)
            self.donationWin.bind(
                '<Return>', lambda event: self.saveEditDonation(donationID, staffID))

            center(self.donationWin)

        else:
            # Outputs error message is no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')

    def saveEditDonation(self, donationID, staffID):
        # Retrieves all inputs from the form
        cashorbankVar = self.cashbankVar.get()
        cashorbank = 'Cash' if cashorbankVar == 0 else 'Bank'
        referenceNo = self.referenceVar.get().strip()
        date = self.dateVar.get()

        # Checks that amount is valid
        amount, amountValid = validateFloat(self.amountVar.get().strip())

        if not amountValid:
            self.errorVar.set('Error: Invalid Amount Input')

        # Checks that date is valid
        dateValid = validateDate(date, self.errorVar)

        if dateValid and amountValid:
            donorID = self.donorIDVar.get()
            # Checks whether a reference no is required
            refneeded = True if cashorbankVar == 1 else False
            # Checks that reference no. is given if required
            refgood = True if (refneeded and referenceNo) or (
                not refneeded) else False
            if refgood:
                # Confirmation box asks user to confirm that inputs are all correct
                if tk.messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nDonationID:\t' +
                                          donationID + '\nAmount:\t\t' + str(amount) +
                                          '\nCash or Bank?\t' + cashorbank + '\nReference No:\t' +
                                          referenceNo + '\nDate:\t\t' + date +
                                          '\nDonorID:\t\t' + donorID + '\nStaffID:\t\t' + staffID):
                    # Updates record in donationsTbl
                    executeSQL('''UPDATE donationsTbl SET amount=?, cashorbank=?, referenceNo=?, date=?, donorID=?
                                   WHERE donationID=?''',
                               (float(amount), cashorbank, referenceNo, date, donorID, donationID), False)
                    # Reloads records into treeview, with updated values
                    loadDatabase(self.tree, 'donationsTbl', False)
                    # Destroys edit donation window and returns to view donations window
                    self.notebook.tab(1, state='normal')
                    enableWindow(self.donationWin, self.reportButton, self.returnButton, self.addDonationButton,
                                 self.editDonationButton, self.delDonationButton)
                    accesslevel(2, self.addDonationButton,
                                self.editDonationButton)
                    accesslevel(3, self.delDonationButton)
                    tk.messagebox.showinfo(
                        'Success!', 'Donation Details Updated')
            else:
                # Outputs error if not all fields are filled
                self.errorVar.set('Error: Please Fill All Fields')

    def delDonation(self):
        if self.tree.selection():
            # Retreives the donationID from the record selected in the treeview
            for selected_item in self.tree.selection():
                donationID = self.tree.set(selected_item, '#1')
            # Asks the user for confimation that they want to permanently delete this record
            if tk.messagebox.askokcancel('Delete', 'Are you sure you want to permanently delete this record?'):
                for selected_item in self.tree.selection():
                    # Removes the recird from donationsTbl
                    executeSQL(
                        'DELETE FROM donationsTbl WHERE donationID=?', (donationID,), False)
                    # Removes the record from the treeview
                    self.tree.delete(selected_item)
        else:
            # Outputs error message is no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')

    def report(self):
        self.notebook.tab(1, state='disabled')
        disableWindow(self.reportButton, self.returnButton, self.addDonationButton, self.editDonationButton,
                      self.delDonationButton)
        self.donationWin = tk.Toplevel(self.root)
        self.donationWin.title('Donation Report')
        self.donationWin.iconbitmap(config.icon)
        self.donationWin.protocol('WM_DELETE_WINDOW', lambda: (self.notebook.tab(1, state='normal'),
                                                               enableWindow(self.donationWin, self.reportButton,
                                                                            self.returnButton,
                                                                            self.addDonationButton,
                                                                            self.editDonationButton,
                                                                            self.delDonationButton),
                                                               accesslevel(2, self.addDonationButton,
                                                                           self.editDonationButton),
                                                               accesslevel(3, self.delDonationButton)))
        self.donationReportFrame = tk.Frame(self.donationWin)
        self.donationReportFrame.pack()
        # Creates labels and entry boxes for start/end date of report
        self.detailLabel = tk.Label(
            self.donationReportFrame, text='Enter Report Parameters', font='none 11 bold')
        self.startDateLabel = tk.Label(
            self.donationReportFrame, text='Start Date:', font='none 11')
        self.startDateVar = tk.StringVar()
        self.startCalendar = DateEntry(self.donationReportFrame, state='readonly',
                                       date_pattern='DD/MM/YYYY', textvariable=self.startDateVar,
                                       showweeknumbers=False, maxdate=datetime.today())
        self.endDateLabel = tk.Label(
            self.donationReportFrame, text='End Date:', font='none 11')
        self.endDateVar = tk.StringVar()
        self.endCalendar = DateEntry(self.donationReportFrame, state='readonly',
                                     date_pattern='DD/MM/YYYY', textvariable=self.endDateVar,
                                     showweeknumbers=False, maxdate=datetime.today())
        # Creates a text variable and error label to output any errors to
        self.errorVar = tk.StringVar()
        self.errorLabel = tk.Label(
            self.donationReportFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
        # Creates a button which runs the generateReport function when pressed
        self.enterButton = ttk.Button(self.donationReportFrame, text='Generate Report',
                                      command=lambda: self.generateReport())
        # Grids all the labels, entry boxes and button created above to the frame
        self.detailLabel.grid(row=0, column=0, columnspan=2, padx=10)
        self.startDateLabel.grid(row=1, column=0, padx=(10, 0))
        self.startCalendar.grid(row=1, column=1, padx=(0, 10), sticky='ew')
        self.endDateLabel.grid(row=2, column=0, padx=(10, 0))
        self.endCalendar.grid(row=2, column=1, padx=(0, 10), sticky='ew')
        self.errorLabel.grid(row=3, column=0, columnspan=2)
        self.enterButton.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        # Runs the generateReport function when the user presses the 'enter' key (same as enterButton)
        self.donationWin.bind('<Return>', lambda event: self.generateReport())

        center(self.donationWin)

    def generateReport(self):
        try:
            # Retrieves the start and end dates entered from the form
            self.startDate = datetime.strptime(
                self.startDateVar.get().strip(), '%d/%m/%Y')
            self.endDate = datetime.strptime(
                self.endDateVar.get().strip(), '%d/%m/%Y')
            # Clears any error messages
            self.errorVar.set('')
            disableWindow(self.enterButton)
            # Creates a new toplevel window to display the report
            self.donationReportWin = tk.Toplevel(self.root)
            self.donationReportWin.title('Donation Report')
            self.donationReportWin.iconbitmap(config.icon)
            self.donationReportFrame = tk.Frame(self.donationReportWin)
            self.donationReportFrame.pack(fill='both', expand=True)
            self.donationReportWin.protocol('WM_DELETE_WINDOW',
                                            lambda: enableWindow(self.donationReportWin, self.enterButton))
            self.titleLabel = tk.Label(self.donationReportFrame, text='Kingfisher Trust', font='algerian 14 bold',
                                       fg='#2380b7')
            self.detailLabel = tk.Label(
                self.donationReportFrame, text='Donation Report', font='none 12 bold')
            # Creates a label detailing the date constraints of the report, as input by the user
            self.datesLabel = tk.Label(self.donationReportFrame,
                                       text='From ' +
                                       str(datetime.isoformat(
                                           self.startDate)[:10])
                                       + ' to ' + str(datetime.isoformat(self.endDate)[:10]) + ':')
            # Creates a button allowing the user to save the report as a PDF file
            self.pdfButton = ttk.Button(self.donationReportFrame, text='Save to PDF',
                                        command=lambda: (disableWindow(self.pdfButton),
                                                         donationReport(self.startDate, self.endDate,
                                                                        records, self.totalDonat)))
            # Grids the above labels and buttons
            self.titleLabel.grid(row=0, column=0, columnspan=3, pady=10)
            self.detailLabel.grid(row=1, column=0, columnspan=3)
            self.datesLabel.grid(row=2, column=0, padx=10, sticky='w')
            self.pdfButton.grid(row=2, column=2, padx=10, sticky='E')
            # Creates a treeview to insert all the relevant donation records
            columns = ('DonationID', 'Amount', 'Cash/Bank',
                       'Reference No', 'Date', 'DonorID', 'Donor Name', 'StaffID')
            self.reporttree = ttk.Treeview(self.donationReportFrame, columns=columns, show='headings',
                                           selectmode='none')
            for col in columns:
                self.reporttree.column(col, width=100, minwidth=100)
                self.reporttree.heading(col, text=col)
            self.reporttree.grid(row=4, column=0, sticky='ewns',
                                 columnspan=3, padx=(10, 0), pady=10)
            self.donationReportFrame.columnconfigure(
                [0, 1, 2], weight=1)  # column with treeview
            self.donationReportFrame.rowconfigure(
                4, weight=1)  # row with treeview
            # Connects to database and selects all records from donationsTbl
            self.records = executeSQL('''SELECT donationsTbl.*,donorTbl.donorForename,donorTbl.donorSurname
                            FROM donationsTbl,donorTbl
                            WHERE donationsTbl.donorID = donorTbl.donorID''', (), True)
            self.totalDonat = 0
            records = []
            # Finds records which fall within the given dates
            for i in self.records:
                date = datetime.strptime(i[4], '%d/%m/%Y')
                if self.startDate <= date <= self.endDate:
                    # Tallys the total amount donated within the time period
                    self.totalDonat += float(i[1])
                    # Inserts the record into the treeview
                    record = i[0], i[1], i[2], i[3], i[4], i[5], (
                        i[7] + ' ' + i[8]), i[6]
                    records.append(record)
                    self.reporttree.insert('', 0, values=record)
            # Creates a label with the total amount donated
            self.donatedLabel = tk.Label(self.donationReportFrame,
                                         text=str('Total Donated = £{:.2f}'.format(self.totalDonat)))
            self.donatedLabel.grid(row=3, column=0, padx=10, sticky='w')

            self.scrollbar = ttk.Scrollbar(
                self.donationReportFrame, orient='vertical', command=self.reporttree.yview)
            self.scrollbar.grid(row=4, column=3, sticky='ns',
                                pady=10, padx=(0, 10))
            self.reporttree.configure(
                yscrollcommand=self.scrollbar.set, selectmode='browse')

            center(self.donationReportWin)

        except ValueError:
            # Outputs an error if the dates input are invalid
            self.errorVar.set('Error: Invalid Input\nDD/MM/YYYY')
