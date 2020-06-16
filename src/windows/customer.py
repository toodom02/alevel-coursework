import tkinter as tk
from tkinter import ttk
import random
import sqlite3

from .. import config
from ..sql import loadDatabase, executeSQL
from ..utils import treeview_sort_column, center, accesslevel, enableWindow, disableWindow
from ..validation import validateEmail, validatePhone


class customerWindow:
    def __init__(self, root, parent):
        self.root = root
        self.root.title('View Customers')
        self.root.iconbitmap(config.icon)
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill='both', expand=True)
        self.root.protocol('WM_DELETE_WINDOW',
                           lambda: self.closeWindow(parent))
        # Creates title label, 'View Customer Records'
        self.titleLabel = tk.Label(
            self.frame, text='View Customer Records', font='none 11')
        # Creates refresh button, to reload data from the database, and the return button, to close the customer window
        # and return the user to the main menu
        self.refreshButton = ttk.Button(self.frame, text='↺',
                                        command=lambda: loadDatabase(self.tree, 'customerTbl', True))
        self.returnButton = ttk.Button(
            self.frame, text='Return to Orders', command=lambda: self.closeWindow(parent))
        # Saves input search value from searchBox as searchVar
        self.searchVar = tk.StringVar()
        self.searchBox = ttk.Entry(self.frame, textvariable=self.searchVar)
        # Creates a dropdown menu, with all the fields listed, set to customerID by default
        self.searchFieldVar = tk.StringVar()
        self.searchField = ttk.OptionMenu(self.frame, self.searchFieldVar, 'CustomerID', 'CustomerID', 'Surname',
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
        columns = ('CustomerID', 'Surname', 'Forename', 'Contact')
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
        # Creates the add, edit and delete customer buttons, which calls their respective functions when clicked
        self.addCustomerButton = ttk.Button(
            self.frame, text='Add Customer', command=lambda: self.addCustomer())
        self.editCustomerButton = ttk.Button(
            self.frame, text='Edit Customer', command=lambda: self.editCustomer())
        self.delCustomerButton = ttk.Button(
            self.frame, text='Delete Customer', command=lambda: self.delCustomer())
        # Grids the add, edit and delete customer buttons to the frame
        self.addCustomerButton.grid(
            row=2, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.editCustomerButton.grid(
            row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delCustomerButton.grid(
            row=4, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        # Runs the search function when the user presses the 'enter' button (same as searchButton)
        self.root.bind('<Return>', lambda event: self.search())
        # Calls function to load the records from the database
        loadDatabase(self.tree, 'customerTbl', False)

        # Checks access level and disables relevant buttons
        accesslevel(2, self.addCustomerButton, self.editCustomerButton)
        accesslevel(3, self.delCustomerButton)

        center(self.root)

    def closeWindow(self, parent):  # destroys CustomerWindow, opens orderwindow
        self.root.destroy()
        parent.deiconify()

    def search(self):
        # Retrieves the search value and search field from the inputs
        # Adds a wildcard symbol, %, to the end of the search value
        search = '%' + str(self.searchVar.get().strip().upper()) + '%'
        searchFieldVar = self.searchFieldVar.get()
        if searchFieldVar == 'CustomerID':
            searchField = 'customerID'
        elif searchFieldVar == 'Surname':
            searchField = 'customerSurname'
        elif searchFieldVar == 'Forename':
            searchField = 'customerForename'
        elif searchFieldVar == 'Contact':
            searchField = 'customerContact'
        # Clears the treeview of all other records
        self.tree.delete(*self.tree.get_children())
        # Selects records from customerTbl where the search field matches the search value
        records = executeSQL(
            'SELECT * FROM customerTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records found into the treeview
            self.tree.insert('', 0, values=(i[0], i[1], i[2], i[3]))

    def addCustomer(self):
        disableWindow(self.returnButton, self.addCustomerButton,
                      self.editCustomerButton, self.delCustomerButton)
        self.customerWin = tk.Toplevel(self.root)
        self.customerWin.title('Add Customer')
        self.customerWin.iconbitmap(config.icon)
        self.customerWin.protocol('WM_DELETE_WINDOW',
                                  lambda: (enableWindow(self.customerWin, self.returnButton, self.addCustomerButton,
                                                        self.editCustomerButton, self.delCustomerButton),
                                           accesslevel(
                                               2, self.addCustomerButton, self.editCustomerButton),
                                           accesslevel(3, self.delCustomerButton)))
        self.addCustomerFrame = tk.Frame(self.customerWin)
        self.addCustomerFrame.pack()
        # Creates all the labels and entry boxes for each field
        self.detailLabel = tk.Label(
            self.addCustomerFrame, text='Enter Customer Details:', font='none 11 bold')
        self.forenameLabel = tk.Label(
            self.addCustomerFrame, text='Forename:', font='none 11')
        self.forenameVar = tk.StringVar()
        self.forenameBox = ttk.Entry(
            self.addCustomerFrame, textvariable=self.forenameVar)
        self.surnameLabel = tk.Label(
            self.addCustomerFrame, text='Surname:', font='none 11')
        self.surnameVar = tk.StringVar()
        self.surnameBox = ttk.Entry(
            self.addCustomerFrame, textvariable=self.surnameVar)
        self.contactLabel = tk.Label(
            self.addCustomerFrame, text='Contact:', font='none 11')
        self.contactVar = tk.StringVar()
        self.contactBox = ttk.Entry(
            self.addCustomerFrame, textvariable=self.contactVar)
        # Creates text variable and error label to output any error messages
        self.errorVar = tk.StringVar()
        self.errorLabel = tk.Label(
            self.addCustomerFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
        # Creates save button, which calls the function saveCustomer when pressed
        self.saveButton = ttk.Button(self.addCustomerFrame, text='Save New Customer',
                                     command=lambda: self.saveCustomer())
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
        # Runs the saveCustomer function when the user presses the 'enter' button (same as saveButton)
        self.customerWin.bind('<Return>', lambda event: self.saveCustomer())

        center(self.customerWin)

    def saveCustomer(self):
        # Retrieves name and contact details from the previous form
        forename = self.forenameVar.get().title().strip()
        surname = self.surnameVar.get().title().strip()
        contact = self.contactVar.get().replace(' ', '')
        # Checks that all fields have been filled
        if forename and surname and contact:
            # Checks that contact is valid phoneNo OR email
            if validatePhone(contact) or validateEmail(contact):
                # Generates a random customerID, using the random module
                customerID = 'CU' + \
                    str(''.join(['%s' % random.randint(0, 9)
                        for num in range(0, 5)]))
                # Asks for user confimation of the input details
                if tk.messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nCustomerID:\t' + customerID +
                                          '\nName:\t\t' + forename + ' ' + surname +
                                          '\nContact:\t\t' + contact):
                    try:
                        # Inserts record into customerTbl
                        executeSQL('INSERT INTO customerTbl VALUES (?,?,?,?)', (customerID, surname, forename, contact),
                                   False)
                        # Reloads records into treeview
                        loadDatabase(self.tree, 'customerTbl', False)
                        # Destroys add customer toplevel and returns to view customers window
                        enableWindow(self.customerWin, self.returnButton, self.addCustomerButton,
                                     self.editCustomerButton, self.delCustomerButton)
                        accesslevel(2, self.addCustomerButton,
                                    self.editCustomerButton)
                        accesslevel(3, self.delCustomerButton)
                        tk.messagebox.showinfo(
                            'Success!', 'New Customer Saved')
                    except sqlite3.IntegrityError:  # Outputs error message if customerID is not unique
                        self.errorVar.set(
                            'Error: Failed To Update Database.\nPlease Try Again')
            else:
                self.errorVar.set(
                    'Error: Please Enter a\nValid Phone No. Or Email')
        else:  # Outputs error if not all fields are filled
            self.errorVar.set('Error: Please Fill All Fields')

    def editCustomer(self):
        if self.tree.selection():  # Runs IF a record is selected from treeview
            disableWindow(self.returnButton, self.addCustomerButton,
                          self.editCustomerButton, self.delCustomerButton)
            for selected_item in self.tree.selection():
                # Finds record from database that matches selected record
                customer = executeSQL('SELECT * FROM customerTbl WHERE customerID=?',
                                      (self.tree.set(selected_item, '#1'),), False)
                customerID = customer[0]
                forename = customer[1]
                surname = customer[2]
                contact = customer[3]
            self.customerWin = tk.Toplevel(self.root)
            self.customerWin.title('Edit Customer')
            self.customerWin.iconbitmap(config.icon)
            self.customerWin.protocol('WM_DELETE_WINDOW',
                                      lambda: (enableWindow(self.customerWin, self.returnButton, self.addCustomerButton,
                                                            self.editCustomerButton, self.delCustomerButton),
                                               accesslevel(
                                                   2, self.addCustomerButton, self.editCustomerButton),
                                               accesslevel(3, self.delCustomerButton)))
            self.editCustomerFrame = tk.Frame(self.customerWin)
            self.editCustomerFrame.pack()
            # Creates all the labels and entry boxes where necessary for each field (no entry box for customerID)
            self.detailLabel = tk.Label(
                self.editCustomerFrame, text='Edit Customer Details:', font='none 11 bold')
            self.customerIDLabel = tk.Label(
                self.editCustomerFrame, text='CustomerID:', font='none 11')
            self.customerIDInsert = tk.Label(
                self.editCustomerFrame, text=customerID, font='none 11')
            self.forenameLabel = tk.Label(
                self.editCustomerFrame, text='Forename:', font='none 11')
            self.forenameVar = tk.StringVar()
            self.forenameBox = ttk.Entry(
                self.editCustomerFrame, textvariable=self.forenameVar)
            self.surnameLabel = tk.Label(
                self.editCustomerFrame, text='Surname:', font='none 11')
            self.surnameVar = tk.StringVar()
            self.surnameBox = ttk.Entry(
                self.editCustomerFrame, textvariable=self.surnameVar)
            self.contactLabel = tk.Label(
                self.editCustomerFrame, text='Contact:', font='none 11')
            self.contactVar = tk.StringVar()
            self.contactBox = ttk.Entry(
                self.editCustomerFrame, textvariable=self.contactVar)
            # Creates text variable and error label to output error messages to
            self.errorVar = tk.StringVar()
            self.errorLabel = tk.Label(
                self.editCustomerFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
            # Creates save button, which calls the function saveEditCustomer
            self.saveButton = ttk.Button(self.editCustomerFrame, text='Update Customer',
                                         command=lambda: self.saveEditCustomer(customerID))
            # Grids all the labels, entry boxes and buttons to the frame
            self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
            self.customerIDLabel.grid(
                row=1, column=0, sticky='E', padx=(10, 0))
            self.customerIDInsert.grid(row=1, column=1, padx=(0, 10))
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
            self.customerWin.bind(
                '<Return>', lambda event: self.saveEditCustomer(customerID))

            center(self.customerWin)

        else:  # Outputs error message if no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')

    def saveEditCustomer(self, customerID):
        # Retrieves name, contact from form
        newForename = self.forenameVar.get().title().strip()
        newSurname = self.surnameVar.get().title().strip()
        newContact = self.contactVar.get().replace(' ', '')
        # Checks that all fields have been filled
        if newForename and newSurname and newContact:
            # Checks that contact is valid phoneNo OR email
            if validatePhone(newContact) or validateEmail(newContact):
                # Creates confirmation dialogue to confirm details are correct
                if tk.messagebox.askyesno('Confirm Changes', 'Are these details correct?\n\nCustomerID:\t'
                                                          + customerID + '\nName:\t\t' + newForename + ' ' + newSurname
                                                          + '\nContact:\t\t' + newContact):
                    # Updates record where the customerID matches the record selected
                    executeSQL('''UPDATE customerTbl SET customerForename=?, customerSurname = ?, customerContact=?
                                   WHERE customerID=?''', (newForename, newSurname, newContact, customerID), False)
                    # Reloads the records into the treeview, with the updated details
                    loadDatabase(self.tree, 'customerTbl', False)
                    # Destroys edit customer window and returns to view customers window
                    enableWindow(self.customerWin, self.returnButton, self.addCustomerButton, self.editCustomerButton,
                                 self.delCustomerButton)
                    accesslevel(2, self.addCustomerButton,
                                self.editCustomerButton)
                    accesslevel(3, self.delCustomerButton)
                    tk.messagebox.showinfo('Success!', 'Customer Details Updated')
            else:
                self.errorVar.set(
                    'Error: Please Enter a\nValid Phone No. Or Email')
        else:  # Outputs error if not all fields have been filled
            self.errorVar.set('Error: Please Fill All Fields')

    def delCustomer(self):
        if self.tree.selection():
            for selected_item in self.tree.selection():
                customerID = self.tree.set(selected_item, '#1')
            # Searches through the table where the
            # customerID might be stored as a foreign key
            existsForeign = executeSQL(
                'SELECT * FROM orderTbl WHERE customerID = ?', (customerID,), False)
            # If customerID is not stored in any other tables
            if not existsForeign:
                # Confirms that the user wants to permanently delete the record
                if tk.messagebox.askokcancel('Delete', 'Are you sure you want to permanently delete this record?'):
                    for selected_item in self.tree.selection():
                        # Deletes the record from customerTbl
                        executeSQL(
                            'DELETE FROM customerTbl WHERE customerID=?', (customerID,), False)
                        # Removes the record from the treeview
                        self.tree.delete(selected_item)
            else:
                # If customerID is a foreign key in other tables, output error as the record cannot be deleted
                tk.messagebox.showerror(
                    'Error', 'Error: Record in use by other tables')
        else:  # Outputs error message if no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')
