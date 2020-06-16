import tkinter as tk
from tkinter import ttk
import random
import sqlite3

from .. import config
from ..utils import treeview_sort_column, enableWindow, disableWindow, accesslevel, center
from ..sql import loadDatabase, executeSQL
from ..validation import validateEmail, validatePhone


class donorWindow:
    # Creates view donors window
    def __init__(self, root):
        self.root = root
        self.root.title('View Donors')
        self.root.iconbitmap(config.icon)
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill='both', expand=True)
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.closeWindow())
        # Creates title label, 'View Donor Records'
        self.titleLabel = tk.Label(
            self.frame, text='View Donor Records', font='none 11')
        # Creates refresh button, to reload data from the database, and the return button, to close the donor window
        # and return the user to the main menu
        self.refreshButton = ttk.Button(
            self.frame, text='↺', command=lambda: loadDatabase(self.tree, 'donorTbl', True))
        self.returnButton = ttk.Button(
            self.frame, text='Main Menu', command=lambda: self.closeWindow())
        # Saves input search value from searchBox as searchVar
        self.searchVar = tk.StringVar()
        self.searchBox = ttk.Entry(self.frame, textvariable=self.searchVar)
        # Creates a dropdown menu, with all the fields listed, set to donorID by default
        self.searchFieldVar = tk.StringVar()
        self.searchField = ttk.OptionMenu(self.frame, self.searchFieldVar, 'DonorID', 'DonorID', 'Surname', 'Forename',
                                          'Contact')
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
        columns = ('DonorID', 'Surname', 'Forename', 'Contact')
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        for col in columns:
            self.tree.column(col, width=100, minwidth=100)
            self.tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(
                self.tree, _col, False))
        self.tree.grid(row=2, column=0, sticky='ewns', rowspan=3,
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
        # Creates the add/edit/delete donor buttons, which calls their respective functions when clicked
        self.addDonorButton = ttk.Button(
            self.frame, text='Add Donor', command=lambda: self.addDonor())
        self.editDonorButton = ttk.Button(
            self.frame, text='Edit Donor', command=lambda: self.editDonor())
        self.delDonorButton = ttk.Button(
            self.frame, text='Delete Donor', command=lambda: self.delDonor())
        # Grids the add/edit/delete donor buttons to the frame
        self.addDonorButton.grid(
            row=2, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.editDonorButton.grid(
            row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delDonorButton.grid(
            row=4, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        # Runs the search function when the user presses the 'enter' button (same as searchButton)
        self.root.bind('<Return>', lambda event: self.search())
        # Calls function to load the records from the database
        loadDatabase(self.tree, 'donorTbl', False)

        # Checks access level and disables relevant buttons
        accesslevel(2, self.addDonorButton, self.editDonorButton)
        accesslevel(3, self.delDonorButton)

        center(self.root)

    # Destroys view Donor Window, opens main menu
    def closeWindow(self):
        self.root.destroy()
        config.app.enableMenu()

    def search(self):
        # Retrieves the search value and search field from the inputs
        # Adds a wildcard symbol, %, to the end of the search value
        search = '%' + str(self.searchVar.get().strip().upper()) + '%'
        searchFieldVar = self.searchFieldVar.get()
        if searchFieldVar == 'DonorID':
            searchField = 'donorID'
        elif searchFieldVar == 'Surname':
            searchField = 'donorSurname'
        elif searchFieldVar == 'Forename':
            searchField = 'donorForename'
        elif searchFieldVar == 'Contact':
            searchField = 'donorContact'
        # Clears the treeview of all other records
        self.tree.delete(*self.tree.get_children())
        # Selects records from donorTbl where the search field matches the search value
        records = executeSQL(
            'SELECT * FROM donorTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records found into the treeview
            self.tree.insert('', 0, values=(i[0], i[1], i[2], i[3]))

    # Creates add donor window
    def addDonor(self):
        disableWindow(self.returnButton, self.addDonorButton,
                      self.editDonorButton, self.delDonorButton)
        self.donorWin = tk.Toplevel(self.root)
        self.donorWin.title('Add Donor')
        self.donorWin.iconbitmap(config.icon)
        self.donorWin.protocol('WM_DELETE_WINDOW',
                               lambda: (enableWindow(self.donorWin, self.returnButton, self.addDonorButton,
                                                     self.editDonorButton, self.delDonorButton),
                                        accesslevel(
                                            2, self.addDonorButton, self.editDonorButton),
                                        accesslevel(3, self.delDonorButton)))
        self.addDonorFrame = tk.Frame(self.donorWin)
        self.addDonorFrame.pack()
        # Creates all the labels and entry boxes for each field
        self.detailLabel = tk.Label(
            self.addDonorFrame, text='Enter Donor Details:', font='none 11 bold')
        self.forenameLabel = tk.Label(
            self.addDonorFrame, text='Forename:', font='none 11')
        self.forenameVar = tk.StringVar()
        self.forenameBox = ttk.Entry(
            self.addDonorFrame, textvariable=self.forenameVar)
        self.surnameLabel = tk.Label(
            self.addDonorFrame, text='Surname:', font='none 11')
        self.surnameVar = tk.StringVar()
        self.surnameBox = ttk.Entry(
            self.addDonorFrame, textvariable=self.surnameVar)
        self.contactLabel = tk.Label(
            self.addDonorFrame, text='Contact:', font='none 11')
        self.contactVar = tk.StringVar()
        self.contactBox = ttk.Entry(
            self.addDonorFrame, textvariable=self.contactVar)
        # Creates text variable and error label to output any error messages
        self.errorVar = tk.StringVar()
        self.errorLabel = tk.Label(
            self.addDonorFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
        # Creates save button, which calls the function saveDonor when pressed
        self.saveButton = ttk.Button(
            self.addDonorFrame, text='Save New Donor', command=lambda: self.saveDonor())
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
        # Runs the saveDonor function when the user presses the 'enter' button (same as saveButton)
        self.donorWin.bind('<Return>', lambda event: self.saveDonor())

        center(self.donorWin)

    # Performs validation on inputs and
    # Saves new donor as a record in donorTbl
    def saveDonor(self):
        # Retrieves all inputs from the add donor form
        forename = self.forenameVar.get().title().strip()
        surname = self.surnameVar.get().title().strip()
        contact = self.contactVar.get().replace(' ', '')
        # Checks that all fields have been filled
        if forename and surname and contact:
            # Checks that contact is valid phoneNo OR email
            if validatePhone(contact) or validateEmail(contact):
                # Generates a random donorID, using the random module
                donorID = 'DO' + \
                    str(''.join(['%s' % random.randint(0, 9)
                        for num in range(0, 5)]))
                # Asks for user confirmation of the input details
                if tk.messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nDonorID:\t\t' + donorID +
                                          '\nName:\t\t' + forename + ' ' + surname +
                                          '\nContact:\t\t' + contact):
                    try:
                        # Inserts record into donorTbl
                        executeSQL('INSERT INTO donorTbl VALUES (?,?,?,?)', (donorID, surname, forename, contact),
                                   False)
                        # Reloads records into treeview
                        loadDatabase(self.tree, 'donorTbl', False)
                        # Destroys add donor toplevel and returns to view donors window
                        enableWindow(self.donorWin, self.returnButton, self.addDonorButton, self.editDonorButton,
                                     self.delDonorButton)
                        accesslevel(2, self.addDonorButton,
                                    self.editDonorButton)
                        accesslevel(3, self.delDonorButton)
                        tk.messagebox.showinfo('Success!', 'New Donor Saved')
                    except sqlite3.IntegrityError:  # Outputs error message if donorID is not unique
                        self.errorVar.set(
                            'Error: Failed To Update Database.\nPlease Try Again')
            else:
                self.errorVar.set(
                    'Error: Please Enter a\nValid Phone No. Or Email')
        else:  # Outputs error if not all fields are filled
            self.errorVar.set('Error: Please Fill All Fields')

    # Creates edit donor window
    def editDonor(self):
        # Runs IF a record is selected from treeview
        if self.tree.selection():
            disableWindow(self.returnButton, self.addDonorButton,
                          self.editDonorButton, self.delDonorButton)
            for selected_item in self.tree.selection():
                # Finds record from database that matches selected record
                donor = executeSQL('SELECT * FROM donorTbl WHERE donorID=?', (self.tree.set(selected_item, '#1'),),
                                   False)
                donorID = donor[0]
                surname = donor[1]
                forename = donor[2]
                contact = donor[3]
            self.donorWin = tk.Toplevel(self.root)
            self.donorWin.title('Edit Donor')
            self.donorWin.iconbitmap(config.icon)
            self.donorWin.protocol('WM_DELETE_WINDOW',
                                   lambda: (enableWindow(self.donorWin, self.returnButton, self.addDonorButton,
                                                         self.editDonorButton, self.delDonorButton),
                                            accesslevel(
                                                2, self.addDonorButton, self.editDonorButton),
                                            accesslevel(3, self.delDonorButton)))
            self.editDonorFrame = tk.Frame(self.donorWin)
            self.editDonorFrame.pack()
            # Creates all the labels and entry boxes where necessary for each field (no entry box for donorID)
            self.detailLabel = tk.Label(
                self.editDonorFrame, text='Edit Donor Details:', font='none 11 bold')
            self.donorIDLabel = tk.Label(
                self.editDonorFrame, text='DonorID:', font='none 11')
            self.donorIDInsert = tk.Label(
                self.editDonorFrame, text=donorID, font='none 11')
            self.forenameLabel = tk.Label(
                self.editDonorFrame, text='Forename:', font='none 11')
            self.forenameVar = tk.StringVar()
            self.forenameBox = ttk.Entry(
                self.editDonorFrame, textvariable=self.forenameVar)
            self.surnameLabel = tk.Label(
                self.editDonorFrame, text='Surname:', font='none 11')
            self.surnameVar = tk.StringVar()
            self.surnameBox = ttk.Entry(
                self.editDonorFrame, textvariable=self.surnameVar)
            self.contactLabel = tk.Label(
                self.editDonorFrame, text='Contact:', font='none 11')
            self.contactVar = tk.StringVar()
            self.contactBox = ttk.Entry(
                self.editDonorFrame, textvariable=self.contactVar)
            # Creates text variable and error label to output error messages to
            self.errorVar = tk.StringVar()
            self.errorLabel = tk.Label(
                self.editDonorFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
            # Creates save button, which calls the function saveEditDonor
            self.saveButton = ttk.Button(self.editDonorFrame, text='Update Donor',
                                         command=lambda: self.saveEditDonor(donorID))
            # Grids all the labels, entry boxes and buttons to the frame
            self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
            self.donorIDLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
            self.donorIDInsert.grid(row=1, column=1, padx=(0, 10))
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
            self.donorWin.bind(
                '<Return>', lambda event: self.saveEditDonor(donorID))

            center(self.donorWin)

        else:  # Outputs error message if no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')

    # Performs validation on the inputs and
    # Updates the record in the database
    def saveEditDonor(self, donorID):
        # Retrieves forename, surname, contact from form
        newForename = self.forenameVar.get().title().strip()
        newSurname = self.surnameVar.get().title().strip()
        newContact = self.contactVar.get().replace(' ', '')
        # Checks that all fields have been filled
        if newForename and newSurname and newContact:
            # Checks that contact is valid phoneNo OR email
            if validatePhone(newContact) or validateEmail(newContact):
                # Creates confirmation dialogue to confirm details are correct
                if tk.messagebox.askyesno('Confirm Changes', 'Are these details correct?\n\nDonorID:\t\t'
                                          + donorID + '\nName:\t\t' + newForename + ' ' + newSurname
                                          + '\nContact:\t\t' + newContact):
                    # Updates record where the donorID matches the record selected
                    executeSQL('''UPDATE donorTbl SET donorSurname=?, donorForename=?, donorContact=?
                                   WHERE donorID=?''', (newSurname, newForename, newContact, donorID), False)
                    # Reloads the records into the treeview, with the updated details
                    loadDatabase(self.tree, 'donorTbl', False)
                    # Destroys edit donor window and returns to view donors window
                    enableWindow(self.donorWin, self.returnButton, self.addDonorButton, self.editDonorButton,
                                 self.delDonorButton)
                    accesslevel(2, self.addDonorButton, self.editDonorButton)
                    accesslevel(3, self.delDonorButton)
                    tk.messagebox.showinfo('Success!', 'Donor Details Updated')
            else:
                self.errorVar.set(
                    'Error: Please Enter a\nValid Phone No. Or Email')
        else:  # Outputs error if not all fields have been filled
            self.errorVar.set('Error: Please Fill All Fields')

    # Deletes the selected record from the database,
    # Unless it is a foreign key in other tables
    def delDonor(self):
        if self.tree.selection():
            for selected_item in self.tree.selection():
                donorID = self.tree.set(selected_item, '#1')
            # Searches through the table where the
            # donorID might be stored as a foreign key
            existsForeign = executeSQL(
                'SELECT * FROM donationsTbl WHERE donorID = ?', (donorID,), True)
            existsForeign += executeSQL(
                'SELECT * FROM foodDonatTbl WHERE donorID = ?', (donorID,), True)
            # If donorID is not stored in any other tables
            if not existsForeign:
                # Confirms that the user wants to permanently delete the record
                if tk.messagebox.askokcancel('Delete', 'Are you sure you want to permanently delete this record?'):
                    for selected_item in self.tree.selection():
                        # Deletes the record from donorTbl
                        executeSQL(
                            'DELETE FROM donorTbl WHERE donorID=?', (donorID,), False)
                        # Removes the record from the treeview
                        self.tree.delete(selected_item)
            else:
                # If donorID is a foreign key in other tables, output error as the record cannot be deleted
                tk.messagebox.showerror(
                    'Error', 'Error: Record in use by other tables')
        else:  # Outputs error message if no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')
