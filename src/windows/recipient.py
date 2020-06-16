import tkinter as tk
from tkinter import ttk
import random
import sqlite3

from .. import config
from ..utils import treeview_sort_column, enableWindow, disableWindow, accesslevel, center
from ..sql import loadDatabase, executeSQL


class recipientWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('View Recipients')
        self.root.iconbitmap(config.icon)
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill='both', expand=True)
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.closeWindow())
        # Creates title label, 'View Recipient Records'
        self.titleLabel = tk.Label(
            self.frame, text='View Recipient Records', font='none 11')
        # Creates refresh button, to reload data from the database, and the return button, to close the recipient window
        # and return the user to the main menu
        self.refreshButton = ttk.Button(self.frame, text='↺',
                                        command=lambda: loadDatabase(self.tree, 'recipientTbl', True))
        self.returnButton = ttk.Button(
            self.frame, text='Main Menu', command=lambda: self.closeWindow())
        # Saves input search value from searchBox as searchVar
        self.searchVar = tk.StringVar()
        self.searchBox = ttk.Entry(self.frame, textvariable=self.searchVar)
        # Creates a dropdown menu, with all the fields listed, set to recipientID by default
        self.searchFieldVar = tk.StringVar()
        self.searchField = ttk.OptionMenu(self.frame, self.searchFieldVar, 'RecipientID', 'RecipientID', 'Surname',
                                          'Forename', 'Contact')
        # Creates a 'Search' button, which calls the search function when pressed
        self.searchButton = ttk.Button(
            self.frame, text='Search', command=lambda: self.search())
        # Grids all the above labels, buttons and entry boxes to the frame
        self.titleLabel.grid(row=0, column=1, sticky='ns')
        self.refreshButton.grid(row=0, column=4, pady=10)
        self.returnButton.grid(row=0, column=0, pady=10,
                               padx=10, ipadx=10, ipady=2, sticky='w')
        self.searchField.grid(row=1, column=0, padx=10, sticky='ew')
        self.searchBox.grid(row=1, column=1, sticky='ew')
        self.searchButton.grid(row=1, column=2, pady=10,
                               padx=(10, 0), ipadx=10)
        # Creates the treeview, defining each column and naming its heading with the relevant field name
        columns = ('RecipientID', 'Surname', 'Forename', 'Contact')
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        for col in columns:
            self.tree.column(col, width=100, minwidth=100)
            self.tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(
                self.tree, _col, False))
        self.tree.grid(row=2, column=0, sticky='nesw', rowspan=3,
                       columnspan=3, padx=(10, 0), pady=(10, 0))
        self.frame.columnconfigure(1, weight=1)  # column with treeview
        self.frame.rowconfigure([2, 3, 4], weight=1)  # row with treeview
        # Creates vertical and horizontal scrollbars, linking them to the treeview
        self.scrollbar = ttk.Scrollbar(
            self.frame, orient='vertical', command=self.tree.yview)
        self.scrollbar.grid(row=2, column=3, sticky='ns', rowspan=3, pady=10)
        self.tree.configure(
            yscrollcommand=self.scrollbar.set, selectmode='browse')
        self.xscrollbar = ttk.Scrollbar(
            self.frame, orient='horizontal', command=self.tree.xview)
        self.xscrollbar.grid(row=5, column=0, sticky='ew',
                             columnspan=4, pady=(0, 10))
        self.tree.configure(
            xscrollcommand=self.xscrollbar.set, selectmode='browse')
        # Creates the add, edit and delete recipient buttons, which calls their respective functions when clicked
        self.addRecipientButton = ttk.Button(
            self.frame, text='Add Recipient', command=lambda: self.addRecipient())
        self.editRecipientButton = ttk.Button(
            self.frame, text='Edit Recipient', command=lambda: self.editRecipient())
        self.delRecipientButton = ttk.Button(
            self.frame, text='Delete Recipient', command=lambda: self.delRecipient())
        # Grids the add, edit and delete recipient buttons to the frame
        self.addRecipientButton.grid(
            row=2, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.editRecipientButton.grid(
            row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delRecipientButton.grid(
            row=4, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        # Runs the search function when the user presses the 'enter' button (same as searchButton)
        self.root.bind('<Return>', lambda event: self.search())
        # Calls function to load the records from the database
        loadDatabase(self.tree, 'recipientTbl', False)

        # Checks access level and disables relevant buttons
        accesslevel(2, self.addRecipientButton, self.editRecipientButton)
        accesslevel(3, self.delRecipientButton)

        center(self.root)

    def closeWindow(self):  # destroys RecipientWindow, opens main menu
        self.root.destroy()
        config.app.enableMenu()

    def search(self):
        # Retrieves the search value and search field from the inputs
        # Adds a wildcard symbol, %, to the end of the search value
        search = '%' + str(self.searchVar.get().strip().upper()) + '%'
        searchFieldVar = self.searchFieldVar.get()
        if searchFieldVar == 'RecipientID':
            searchField = 'recipientID'
        elif searchFieldVar == 'Surname':
            searchField = 'recipientSurname'
        elif searchFieldVar == 'Forename':
            searchField = 'recipientForename'
        elif searchFieldVar == 'Contact':
            searchField = 'recipientContact'
        # Clears the treeview of all other records
        self.tree.delete(*self.tree.get_children())
        # Selects records from recipientTbl where the search field matches the search value
        records = executeSQL(
            'SELECT * FROM recipientTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records found into the treeview
            self.tree.insert('', 0, values=(i[0], i[1], i[2], i[3]))

    def addRecipient(self):
        disableWindow(self.returnButton, self.addRecipientButton,
                      self.editRecipientButton, self.delRecipientButton)
        self.recipientWin = tk.Toplevel(self.root)
        self.recipientWin.title('Add Recipient')
        self.recipientWin.iconbitmap(config.icon)
        self.recipientWin.protocol('WM_DELETE_WINDOW',
                                   lambda: (enableWindow(self.recipientWin, self.returnButton, self.addRecipientButton,
                                                         self.editRecipientButton, self.delRecipientButton),
                                            accesslevel(
                                                2, self.addRecipientButton, self.editRecipientButton),
                                            accesslevel(3, self.delRecipientButton)))
        self.addRecipientFrame = tk.Frame(self.recipientWin)
        self.addRecipientFrame.pack()
        # Creates all the labels and entry boxes for each field
        self.detailLabel = tk.Label(
            self.addRecipientFrame, text='Enter Recipient Details:', font='none 11 bold')
        self.forenameLabel = tk.Label(
            self.addRecipientFrame, text='Forename:', font='none 11')
        self.forenameVar = tk.StringVar()
        self.forenameBox = ttk.Entry(
            self.addRecipientFrame, textvariable=self.forenameVar)
        self.surnameLabel = tk.Label(
            self.addRecipientFrame, text='Surname:', font='none 11')
        self.surnameVar = tk.StringVar()
        self.surnameBox = ttk.Entry(
            self.addRecipientFrame, textvariable=self.surnameVar)
        self.contactLabel = tk.Label(
            self.addRecipientFrame, text='Contact:', font='none 11')
        self.contactVar = tk.StringVar()
        self.contactBox = ttk.Entry(
            self.addRecipientFrame, textvariable=self.contactVar)
        # Creates text variable and error label to output any error messages
        self.errorVar = tk.StringVar()
        self.errorLabel = tk.Label(
            self.addRecipientFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
        # Creates save button, which calls the function saveRecipient when pressed
        self.saveButton = ttk.Button(self.addRecipientFrame, text='Save New Recipient',
                                     command=lambda: self.saveRecipient())
        # Grids all the labels, entry boxes and buttons that we have created to the frame
        self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
        self.forenameLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
        self.forenameBox.grid(row=1, column=1, padx=(0, 10))
        self.surnameLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
        self.surnameBox.grid(row=2, column=1, padx=(0, 10))
        self.contactLabel.grid(row=3, column=0, sticky='E', padx=(10, 0))
        self.contactBox.grid(row=3, column=1, padx=(0, 10))
        self.errorLabel.grid(row=4, column=0, columnspan=2)
        self.saveButton.grid(row=5, column=0, columnspan=2, pady=(0, 10))
        # Runs the saveRecipient function when the user presses the 'enter' button (same as saveButton)
        self.recipientWin.bind('<Return>', lambda event: self.saveRecipient())

        center(self.recipientWin)

    def saveRecipient(self):
        # Retrieves forename, surname and contact details from the previous form
        forename = self.forenameVar.get().title().strip()
        surname = self.surnameVar.get().title().strip()
        contact = self.contactVar.get().strip()
        # Checks that all fields have been filled
        if forename:
            # Generates a random recipientID, using the random module
            recipientID = 'RE' + \
                str(''.join(['%s' % random.randint(0, 9)
                    for num in range(0, 5)]))
            # Asks for user confimation of the input details
            if tk.messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nRecipientID:\t' + recipientID +
                                      '\nName:\t\t' + forename + ' ' + surname +
                                      '\nContact:\t\t' + contact):
                try:
                    # Inserts record into recipientTbl
                    executeSQL('INSERT INTO recipientTbl VALUES (?,?,?,?)', (recipientID, surname, forename, contact),
                               False)
                    # Reloads records into treeview
                    loadDatabase(self.tree, 'recipientTbl', False)
                    # Destroys add recipient toplevel and returns to view recipients window
                    enableWindow(self.recipientWin, self.returnButton, self.addRecipientButton,
                                 self.editRecipientButton, self.delRecipientButton)
                    accesslevel(2, self.addRecipientButton,
                                self.editRecipientButton)
                    accesslevel(3, self.delRecipientButton)
                    tk.messagebox.showinfo('Success!', 'New Recipient Saved')
                except sqlite3.IntegrityError:  # Outputs error message if recipientID is not unique
                    self.errorVar.set(
                        'Error: Failed To Update Database.\nPlease Try Again')
        else:  # Outputs error if not all fields are filled
            self.errorVar.set('Error: Please Fill Forename Field')

    def editRecipient(self):
        if self.tree.selection():  # Runs IF a record is selected from treeview
            disableWindow(self.returnButton, self.addRecipientButton,
                          self.editRecipientButton, self.delRecipientButton)
            for selected_item in self.tree.selection():
                # Finds record from database that matches selected record
                recipient = executeSQL('SELECT * FROM recipientTbl WHERE recipientID=?',
                                       (self.tree.set(selected_item, '#1'),), False)
                recipientID = recipient[0]
                surname = recipient[1]
                forename = recipient[2]
                contact = recipient[3]
            self.recipientWin = tk.Toplevel(self.root)
            self.recipientWin.title('Edit Recipient')
            self.recipientWin.iconbitmap(config.icon)
            self.recipientWin.protocol('WM_DELETE_WINDOW', lambda: (
                enableWindow(self.recipientWin, self.returnButton, self.addRecipientButton,
                             self.editRecipientButton, self.delRecipientButton),
                accesslevel(2, self.addRecipientButton,
                            self.editRecipientButton),
                accesslevel(3, self.delRecipientButton)))
            self.editRecipientFrame = tk.Frame(self.recipientWin)
            self.editRecipientFrame.pack()
            # Creates all the labels and entry boxes where necessary for each field (no entry box for recipientID)
            self.detailLabel = tk.Label(
                self.editRecipientFrame, text='Edit Recipient Details:', font='none 11 bold')
            self.recipientIDLabel = tk.Label(
                self.editRecipientFrame, text='RecipientID:', font='none 11')
            self.recipientIDInsert = tk.Label(
                self.editRecipientFrame, text=recipientID, font='none 11')
            self.forenameLabel = tk.Label(
                self.editRecipientFrame, text='Forename:', font='none 11')
            self.forenameVar = tk.StringVar()
            self.forenameBox = ttk.Entry(
                self.editRecipientFrame, textvariable=self.forenameVar)
            self.surnameLabel = tk.Label(
                self.editRecipientFrame, text='Surname:', font='none 11')
            self.surnameVar = tk.StringVar()
            self.surnameBox = ttk.Entry(
                self.editRecipientFrame, textvariable=self.surnameVar)
            self.contactLabel = tk.Label(
                self.editRecipientFrame, text='Contact:', font='none 11')
            self.contactVar = tk.StringVar()
            self.contactBox = ttk.Entry(
                self.editRecipientFrame, textvariable=self.contactVar)
            # Creates text variable and error label to output error messages to
            self.errorVar = tk.StringVar()
            self.errorLabel = tk.Label(
                self.editRecipientFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
            # Creates save button, which calls the function saveEditRecipient
            self.saveButton = ttk.Button(self.editRecipientFrame, text='Update Recipient',
                                         command=lambda: self.saveEditRecipient(recipientID))
            # Grids all the labels, entry boxes and buttons to the frame
            self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
            self.recipientIDLabel.grid(
                row=1, column=0, sticky='E', padx=(10, 0))
            self.recipientIDInsert.grid(row=1, column=1, padx=(0, 10))
            self.forenameLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
            self.forenameBox.grid(row=2, column=1, padx=(0, 10))
            self.surnameLabel.grid(row=3, column=0, sticky='E', padx=(10, 0))
            self.surnameBox.grid(row=3, column=1, padx=(0, 10))
            self.contactLabel.grid(row=4, column=0, sticky='E', padx=(10, 0))
            self.contactBox.grid(row=4, column=1, padx=(0, 10))
            self.errorLabel.grid(row=5, column=0, columnspan=2)
            self.saveButton.grid(row=6, column=0, columnspan=2, pady=(0, 10))
            # Inserts the current fields into the entry boxes
            self.forenameBox.insert(tk.INSERT, forename)
            self.surnameBox.insert(tk.INSERT, surname)
            self.contactBox.insert(tk.INSERT, contact)
            # Runs the save function when the user presses the 'enter' button (same as saveButton)
            self.recipientWin.bind(
                '<Return>', lambda event: self.saveEditRecipient(recipientID))

            center(self.recipientWin)

        else:  # Outputs error message if no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')

    def saveEditRecipient(self, recipientID):
        # Retrieves forename, surname, contact from form
        newForename = self.forenameVar.get().title().strip()
        newSurname = self.surnameVar.get().title().strip()
        newContact = self.contactVar.get().replace(' ', '')
        # Checks that all fields have been filled
        if newForename:
            # Creates confirmation dialogue to confirm details are correct
            if tk.messagebox.askyesno('Confirm Changes', 'Are these details correct?\n\nRecipientID:\t'
                                      + recipientID + '\nName:\t\t' + newForename + ' ' + newSurname
                                                      + '\nContact:\t\t' + newContact):
                # Updates record where the recipientID matches the record selected
                executeSQL('''UPDATE recipientTbl SET recipientSurname=?, recipientForename=?, recipientContact=?
                               WHERE recipientID=?''', (newSurname, newForename, newContact, recipientID), False)
                # Reloads the records into the treeview, with the updated details
                loadDatabase(self.tree, 'recipientTbl', False)
                # Destroys edit recipient window and returns to view recipients window
                enableWindow(self.recipientWin, self.returnButton, self.addRecipientButton, self.editRecipientButton,
                             self.delRecipientButton)
                accesslevel(2, self.addRecipientButton,
                            self.editRecipientButton)
                accesslevel(3, self.delRecipientButton)
                tk.messagebox.showinfo('Success!', 'Recipient Details Updated')
        else:  # Outputs error if not all fields have been filled
            self.errorVar.set('Error: Please Fill Forename Field')

    def delRecipient(self):
        if self.tree.selection():
            for selected_item in self.tree.selection():
                recipientID = self.tree.set(selected_item, '#1')
            # Searches through the table where the
            # recipientID might be stored as a foreign key
            existsForeign = executeSQL(
                'SELECT * FROM giveFoodTbl WHERE recipientID = ?', (recipientID,), False)
            # If recipientID is not stored in any other tables
            if not existsForeign:
                # Confirms that the user wants to permanently delete the record
                if tk.messagebox.askokcancel('Delete', 'Are you sure you want to permanently delete this record?'):
                    for selected_item in self.tree.selection():
                        # Deletes the record from recipientTbl
                        executeSQL(
                            'DELETE FROM recipientTbl WHERE recipientID=?', (recipientID,), False)
                        # Removes the record from the treeview
                        self.tree.delete(selected_item)
            else:
                # If recipientID is a foreign key in other tables, output error as the record cannot be deleted
                tk.messagebox.showerror(
                    'Error', 'Error: Record in use by other tables')
        else:  # Outputs error message if no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')
