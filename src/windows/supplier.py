import tkinter as tk
from tkinter import ttk
import random
import sqlite3

from .. import config
from ..utils import treeview_sort_column, enableWindow, disableWindow, accesslevel, center
from ..sql import loadDatabase, executeSQL
from ..validation import validatePhone, validateEmail


class supplierWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('View Suppliers')
        self.root.iconbitmap(config.icon)
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill='both', expand=True)
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.closeWindow())
        # Creates title label, 'View Supplier Records'
        self.titleLabel = tk.Label(
            self.frame, text='View Supplier Records', font='none 11')
        # Creates refresh button, to reload data from the database, and the return button, to close the supplier window
        # and return the user to the main menu
        self.refreshButton = ttk.Button(self.frame, text='↺',
                                        command=lambda: loadDatabase(self.tree, 'supplierTbl', True))
        self.returnButton = ttk.Button(
            self.frame, text='Main Menu', command=lambda: self.closeWindow())
        # Saves input search value from searchBox as searchVar
        self.searchVar = tk.StringVar()
        self.searchBox = ttk.Entry(self.frame, textvariable=self.searchVar)
        # Creates a dropdown menu, with all the fields listed, set to supplierID by default
        self.searchFieldVar = tk.StringVar()
        self.searchField = ttk.OptionMenu(self.frame, self.searchFieldVar, 'SupplierID', 'SupplierID', 'Name',
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
        columns = ('SupplierID', 'Name', 'Contact')
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
        # Creates the add, edit and delete supplier buttons, which calls their respective functions when clicked
        self.addSupplierButton = ttk.Button(
            self.frame, text='Add Supplier', command=lambda: self.addSupplier())
        self.editSupplierButton = ttk.Button(
            self.frame, text='Edit Supplier', command=lambda: self.editSupplier())
        self.delSupplierButton = ttk.Button(
            self.frame, text='Delete Supplier', command=lambda: self.delSupplier())
        # Grids the add, edit and delete supplier buttons to the frame
        self.addSupplierButton.grid(
            row=2, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.editSupplierButton.grid(
            row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delSupplierButton.grid(
            row=4, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        # Runs the search function when the user presses the 'enter' button (same as searchButton)
        self.root.bind('<Return>', lambda event: self.search())
        # Calls function to load the records from the database
        loadDatabase(self.tree, 'supplierTbl', False)

        # Checks access level and disables relevant buttons
        accesslevel(2, self.addSupplierButton, self.editSupplierButton)
        accesslevel(3, self.delSupplierButton)

        center(self.root)

    def closeWindow(self):  # destroys SupplierWindow, opens main menu
        self.root.destroy()
        config.app.enableMenu()

    def search(self):
        # Retrieves the search value and search field from the inputs
        # Adds a wildcard symbol, %, to the end of the search value
        search = '%' + str(self.searchVar.get().strip().upper()) + '%'
        searchFieldVar = self.searchFieldVar.get()
        if searchFieldVar == 'SupplierID':
            searchField = 'supplierID'
        elif searchFieldVar == 'Name':
            searchField = 'supplierName'
        elif searchFieldVar == 'Contact':
            searchField = 'supplierContact'
        # Clears the treeview of all other records
        self.tree.delete(*self.tree.get_children())
        # Selects records from supplierTbl where the search field matches the search value
        records = executeSQL(
            'SELECT * FROM supplierTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records found into the treeview
            self.tree.insert('', 0, values=(i[0], i[1], i[2]))

    def addSupplier(self):
        disableWindow(self.returnButton, self.addSupplierButton,
                      self.editSupplierButton, self.delSupplierButton)
        self.supplierWin = tk.Toplevel(self.root)
        self.supplierWin.title('Add Supplier')
        self.supplierWin.iconbitmap(config.icon)
        self.supplierWin.protocol('WM_DELETE_WINDOW',
                                  lambda: (enableWindow(self.supplierWin, self.returnButton, self.addSupplierButton,
                                                        self.editSupplierButton, self.delSupplierButton),
                                           accesslevel(
                                               2, self.addSupplierButton, self.editSupplierButton),
                                           accesslevel(3, self.delSupplierButton)))
        self.addSupplierFrame = tk.Frame(self.supplierWin)
        self.addSupplierFrame.pack()
        # Creates all the labels and entry boxes for each field
        self.detailLabel = tk.Label(
            self.addSupplierFrame, text='Enter Supplier Details:', font='none 11 bold')
        self.nameLabel = tk.Label(self.addSupplierFrame,
                                  text='Name:', font='none 11')
        self.nameVar = tk.StringVar()
        self.nameBox = ttk.Entry(
            self.addSupplierFrame, textvariable=self.nameVar)
        self.contactLabel = tk.Label(
            self.addSupplierFrame, text='Contact:', font='none 11')
        self.contactVar = tk.StringVar()
        self.contactBox = ttk.Entry(
            self.addSupplierFrame, textvariable=self.contactVar)
        # Creates text variable and error label to output any error messages
        self.errorVar = tk.StringVar()
        self.errorLabel = tk.Label(
            self.addSupplierFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
        # Creates save button, which calls the function saveSupplier when pressed
        self.saveButton = ttk.Button(self.addSupplierFrame, text='Save New Supplier',
                                     command=lambda: self.saveSupplier())
        # Grids all the labels, entry boxes and buttons that we have created to the frame
        self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
        self.nameLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
        self.nameBox.grid(row=1, column=1, padx=(0, 10))
        self.contactLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
        self.contactBox.grid(row=2, column=1, padx=(0, 10))
        self.errorLabel.grid(row=3, column=0, columnspan=2)
        self.saveButton.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        # Runs the saveSupplier function when the user presses the 'enter' button (same as saveButton)
        self.supplierWin.bind('<Return>', lambda event: self.saveSupplier())

        center(self.supplierWin)

    def saveSupplier(self):
        # Retrieves name and contact details from the previous form
        name = self.nameVar.get().title().strip()
        contact = self.contactVar.get().replace(' ', '')
        # Checks that all fields have been filled
        if name and contact:
            # Checks that contact is valid phoneNo OR email
            if validatePhone(contact) or validateEmail(contact):
                # Generates a random supplierID, using the random module
                supplierID = 'SU' + \
                    str(''.join(['%s' % random.randint(0, 9)
                        for num in range(0, 5)]))
                # Asks for user confimation of the input details
                if tk.messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nSupplierID:\t' + supplierID +
                                          '\nName:\t\t' + name + '\nContact:\t\t' + contact):
                    try:
                        # Inserts record into supplierTbl
                        executeSQL('INSERT INTO supplierTbl VALUES (?,?,?)',
                                   (supplierID, name, contact), False)
                        # Reloads records into treeview
                        loadDatabase(self.tree, 'supplierTbl', False)
                        # Destroys add supplier toplevel and returns to view suppliers window
                        enableWindow(self.supplierWin, self.returnButton, self.addSupplierButton,
                                     self.editSupplierButton, self.delSupplierButton)
                        accesslevel(2, self.addSupplierButton,
                                    self.editSupplierButton)
                        accesslevel(3, self.delSupplierButton)
                        tk.messagebox.showinfo(
                            'Success!', 'New Supplier Saved')
                    except sqlite3.IntegrityError:  # Outputs error message if supplierID is not unique
                        self.errorVar.set(
                            'Error: Failed To Update Database.\nPlease Try Again')
            else:
                self.errorVar.set(
                    'Error: Please Enter a\nValid Phone No. Or Email')
        else:  # Outputs error if not all fields are filled
            self.errorVar.set('Error: Please Fill All Fields')

    def editSupplier(self):
        if self.tree.selection():  # Runs IF a record is selected from treeview
            disableWindow(self.returnButton, self.addSupplierButton,
                          self.editSupplierButton, self.delSupplierButton)
            for selected_item in self.tree.selection():
                # Finds record from database that matches selected record
                supplier = executeSQL('SELECT * FROM supplierTbl WHERE supplierID=?',
                                      (self.tree.set(selected_item, '#1'),), False)
                supplierID = supplier[0]
                name = supplier[1]
                contact = supplier[2]
            self.supplierWin = tk.Toplevel(self.root)
            self.supplierWin.title('Edit Supplier')
            self.supplierWin.iconbitmap(config.icon)
            self.supplierWin.protocol('WM_DELETE_WINDOW',
                                      lambda: (enableWindow(self.supplierWin, self.returnButton, self.addSupplierButton,
                                                            self.editSupplierButton, self.delSupplierButton),
                                               accesslevel(
                                                   2, self.addSupplierButton, self.editSupplierButton),
                                               accesslevel(3, self.delSupplierButton)))
            self.editSupplierFrame = tk.Frame(self.supplierWin)
            self.editSupplierFrame.pack()
            # Creates all the labels and entry boxes where necessary for each field (no entry box for supplierID)
            self.detailLabel = tk.Label(
                self.editSupplierFrame, text='Edit Supplier Details:', font='none 11 bold')
            self.supplierIDLabel = tk.Label(
                self.editSupplierFrame, text='SupplierID:', font='none 11')
            self.supplierIDInsert = tk.Label(
                self.editSupplierFrame, text=supplierID, font='none 11')
            self.nameLabel = tk.Label(
                self.editSupplierFrame, text='Name:', font='none 11')
            self.nameVar = tk.StringVar()
            self.nameBox = ttk.Entry(
                self.editSupplierFrame, textvariable=self.nameVar)
            self.contactLabel = tk.Label(
                self.editSupplierFrame, text='Contact:', font='none 11')
            self.contactVar = tk.StringVar()
            self.contactBox = ttk.Entry(
                self.editSupplierFrame, textvariable=self.contactVar)
            # Creates text variable and error label to output error messages to
            self.errorVar = tk.StringVar()
            self.errorLabel = tk.Label(
                self.editSupplierFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
            # Creates save button, which calls the function saveEditSupplier
            self.saveButton = ttk.Button(self.editSupplierFrame, text='Update Supplier',
                                         command=lambda: self.saveEditSupplier(supplierID))
            # Grids all the labels, entry boxes and buttons to the frame
            self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
            self.supplierIDLabel.grid(
                row=1, column=0, sticky='E', padx=(10, 0))
            self.supplierIDInsert.grid(row=1, column=1, padx=(0, 10))
            self.nameLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
            self.nameBox.grid(row=2, column=1, padx=(0, 10))
            self.contactLabel.grid(row=3, column=0, sticky='E', padx=(10, 0))
            self.contactBox.grid(row=3, column=1, padx=(0, 10))
            self.errorLabel.grid(row=4, column=0, columnspan=2)
            self.saveButton.grid(row=5, column=0, columnspan=2, pady=(0, 10))
            # Inserts the current fields into the entry boxes
            self.nameBox.insert(tk.INSERT, name)
            self.contactBox.insert(tk.INSERT, contact)
            # Runs the save function when the user presses the 'enter' button (same as saveButton)
            self.supplierWin.bind(
                '<Return>', lambda event: self.saveEditSupplier(supplierID))

            center(self.supplierWin)

        else:  # Outputs error message if no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')

    def saveEditSupplier(self, supplierID):
        # Retrieves name, contact from form
        newName = self.nameVar.get().title().strip()
        newContact = self.contactVar.get().replace(' ', '')
        # Checks that all fields have been filled
        if newName and newContact:
            # Checks that contact is valid phoneNo OR email
            if validatePhone(newContact) or validateEmail(newContact):
                # Creates confirmation dialogue to confirm details are correct
                if tk.messagebox.askyesno('Confirm Changes', 'Are these details correct?\n\nSupplierID:\t'
                                          + supplierID + '\nName:\t\t' + newName
                                          + '\nContact:\t\t' + newContact):
                    # Updates record where the supplierID matches the record selected
                    executeSQL('''UPDATE supplierTbl SET supplierName=?, supplierContact=?
                                   WHERE supplierID=?''', (newName, newContact, supplierID), False)
                    # Reloads the records into the treeview, with the updated details
                    loadDatabase(self.tree, 'supplierTbl', False)
                    # Destroys edit supplier window and returns to view suppliers window
                    enableWindow(self.supplierWin, self.returnButton, self.addSupplierButton, self.editSupplierButton,
                                 self.delSupplierButton)
                    accesslevel(2, self.addSupplierButton,
                                self.editSupplierButton)
                    accesslevel(3, self.delSupplierButton)
                    tk.messagebox.showinfo(
                        'Success!', 'Supplier Details Updated')
            else:
                self.errorVar.set(
                    'Error: Please Enter a\nValid Phone No. Or Email')
        else:  # Outputs error if not all fields have been filled
            self.errorVar.set('Error: Please Fill All Fields')

    def delSupplier(self):
        if self.tree.selection():
            for selected_item in self.tree.selection():
                supplierID = self.tree.set(selected_item, '#1')
            # Searches through the table where the
            # supplierID might be stored as a foreign key
            existsForeign = executeSQL(
                'SELECT * FROM itemTbl WHERE supplierID = ?', (supplierID,), False)
            # If supplierID is not stored in any other tables
            if not existsForeign:
                # Confirms that the user wants to permanently delete the record
                if tk.messagebox.askokcancel('Delete', 'Are you sure you want to permanently delete this record?'):
                    for selected_item in self.tree.selection():
                        # Deletes the record from supplierTbl
                        executeSQL(
                            'DELETE FROM supplierTbl WHERE supplierID=?', (supplierID,), False)
                        # Removes the record from the treeview
                        self.tree.delete(selected_item)
            else:
                # If supplierID is a foreign key in other tables, output error as the record cannot be deleted
                tk.messagebox.showerror(
                    'Error', 'Error: Record in use by other tables')
        else:  # Outputs error message if no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')
