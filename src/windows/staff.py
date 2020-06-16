import tkinter as tk
from tkinter import ttk
import random
import sqlite3
import bcrypt

from .. import config
from ..utils import treeview_sort_column, enableWindow, disableWindow, accesslevel, center
from ..sql import loadDatabase, executeSQL
from ..validation import validatePhone


class staffWindow:
    # Creates view staff window
    def __init__(self, root):
        self.root = root
        self.root.title('View Staff')
        self.root.iconbitmap(config.icon)
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill='both', expand=True)
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.closeWindow())
        # Creates title label, 'View Staff Records'
        self.titleLabel = tk.Label(
            self.frame, text='View Staff Records', font='none 11')
        # Creates refresh button, to reload data from the database,
        # And the return button, to close the staff window and return the user to the main menu
        self.refreshButton = ttk.Button(
            self.frame, text='↺', command=lambda: loadDatabase(self.tree, 'staffTbl', True))
        self.returnButton = ttk.Button(
            self.frame, text='Main Menu', command=lambda: self.closeWindow())
        # Saves input search value from searchBox as searchVar
        self.searchVar = tk.StringVar()
        self.searchBox = ttk.Entry(self.frame, textvariable=self.searchVar)
        # Creates a dropdown menu, with all the fields listed, set to staffID by default
        self.searchFieldVar = tk.StringVar()
        self.searchField = ttk.OptionMenu(self.frame, self.searchFieldVar, 'StaffID', 'StaffID',
                                          'Surname', 'Forename', 'Contact', 'AccessLevel')
        # Creates a 'Search' button, which calls the search function when pressed
        self.searchButton = ttk.Button(
            self.frame, text='Search', command=lambda: self.search())
        # Grids the above labels, buttons and entry boxes to the frame
        self.titleLabel.grid(row=0, column=1, sticky='ns')
        self.refreshButton.grid(row=0, column=4, pady=10)
        self.returnButton.grid(row=0, column=0, pady=10,
                               padx=10, ipadx=10, ipady=2, sticky='w')
        self.searchField.grid(row=1, column=0, padx=10, sticky='ew')
        self.searchBox.grid(row=1, column=1, sticky='ew')
        self.searchButton.grid(row=1, column=2, pady=10,
                               padx=(10, 0), ipadx=10)
        # Creates the treeview, defining each column and naming its heading with the relevant field name
        columns = ('StaffID', 'Surname', 'Forename', 'Contact', 'AccessLevel')
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
        # Creates the add, edit and delete staff buttons, which call their respective functions when clicked
        self.addStaffButton = ttk.Button(
            self.frame, text='Add Staff', command=lambda: self.addStaff())
        self.editStaffButton = ttk.Button(
            self.frame, text='Edit Staff', command=lambda: self.editStaff())
        self.delStaffButton = ttk.Button(
            self.frame, text='Delete Staff', command=lambda: self.delStaff())
        # Grids the add, edit and delete buttons to the frame
        self.addStaffButton.grid(
            row=2, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.editStaffButton.grid(
            row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delStaffButton.grid(
            row=4, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        # Runs the search function when the user presses the 'enter' button (same as searchButton)
        self.root.bind('<Return>', lambda event: self.search())
        # Calls function to load the records from the database
        loadDatabase(self.tree, 'staffTbl', False)

        # Checks access level and disables relevant buttons
        accesslevel(3, self.addStaffButton,
                    self.editStaffButton, self.delStaffButton)

        self.tree.bind('<<TreeviewSelect>>', lambda event: self.on_select())

        center(self.root)

    def on_select(self):
        if self.tree.set(self.tree.selection()[0], '#1') == config.userID:
            self.editStaffButton['state'] = 'normal'
            self.delStaffButton['state'] = 'normal'
        else:
            accesslevel(3, self.delStaffButton, self.editStaffButton)

    # Destroys staffWindow, opens main menu
    def closeWindow(self):
        self.root.destroy()
        config.app.enableMenu()

    def search(self):
        # Retrieves the search value and search field from the inputs
        # Adds a wildcard symbol to the end of the search value
        search = '%' + str(self.searchVar.get().strip().upper()) + '%'
        searchFieldVar = self.searchFieldVar.get()
        if searchFieldVar == 'StaffID':
            searchField = 'staffID'
        elif searchFieldVar == 'Surname':
            searchField = 'staffSurname'
        elif searchFieldVar == 'Forename':
            searchField = 'staffForename'
        elif searchFieldVar == 'Contact':
            searchField = 'staffContact'
        elif searchFieldVar == 'AccessLevel':
            searchField = 'accessLevel'
        # Clears treeview of all other records
        self.tree.delete(*self.tree.get_children())
        # Selects records from staffTbl where the search field matches the search value
        records = executeSQL(
            'SELECT * FROM staffTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records fetched into the treeview
            self.tree.insert('', 0, values=(i[0], i[1], i[2], i[3], i[4]))

    # Creates add staff window
    def addStaff(self):
        disableWindow(self.returnButton, self.addStaffButton,
                      self.editStaffButton, self.delStaffButton)
        self.staffWin = tk.Toplevel(self.root)
        self.staffWin.title('Add Staff')
        self.staffWin.iconbitmap(config.icon)
        self.staffWin.protocol('WM_DELETE_WINDOW',
                               lambda: (enableWindow(self.staffWin, self.returnButton, self.addStaffButton,
                                                     self.editStaffButton, self.delStaffButton),
                                        accesslevel(3, self.addStaffButton, self.editStaffButton,
                                                    self.delStaffButton)))
        self.addStaffFrame = tk.Frame(self.staffWin)
        self.addStaffFrame.pack()
        # Creates all the labels and entry boxes for each field
        self.detailLabel = tk.Label(
            self.addStaffFrame, text='Enter Staff Details:', font='none 11 bold')
        self.forenameLabel = tk.Label(
            self.addStaffFrame, text='Forename:', font='none 11')
        self.forenameVar = tk.StringVar()
        self.forenameBox = ttk.Entry(
            self.addStaffFrame, textvariable=self.forenameVar)
        self.surnameLabel = tk.Label(
            self.addStaffFrame, text='Surname:', font='none 11')
        self.surnameVar = tk.StringVar()
        self.surnameBox = ttk.Entry(
            self.addStaffFrame, textvariable=self.surnameVar)
        self.contactLabel = tk.Label(
            self.addStaffFrame, text='Phone No.:', font='none 11')
        self.contactVar = tk.StringVar()
        self.contactBox = ttk.Entry(
            self.addStaffFrame, textvariable=self.contactVar)
        self.accessLevelLabel = tk.Label(
            self.addStaffFrame, text='Access Level:', font='none 11')
        # Creates a dropdown for the accesslevel to be selected from the given options
        self.accessLevelVar = tk.StringVar()
        self.accessLevelVar.set('Select...')
        self.accessLevelDropdown = ttk.OptionMenu(
            self.addStaffFrame, self.accessLevelVar, '1', '1', '2', '3')
        self.passwordLabel = tk.Label(
            self.addStaffFrame, text='Password:', font='none 11')
        self.passwordVar = tk.StringVar()
        # Both the password and password confirmation show *s for any input characters, to prevent
        # shoulder surfers from seeing the input password
        self.passwordBox = ttk.Entry(
            self.addStaffFrame, show='•', textvariable=self.passwordVar)
        self.passConfirmLabel = tk.Label(
            self.addStaffFrame, text='Confirm Password:', font='none 11')
        self.passConfirmVar = tk.StringVar()
        self.passConfirmBox = ttk.Entry(
            self.addStaffFrame, show='•', textvariable=self.passConfirmVar)
        self.errorVar = tk.StringVar()
        # Creates error label to display any errors
        self.errorLabel = tk.Label(
            self.addStaffFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
        # Creates save button, which calls the function saveStaff when pressed
        self.saveButton = ttk.Button(
            self.addStaffFrame, text='Save New Staff', command=lambda: self.saveStaff())
        # Grids all labels, entry boxes, dropdowns and buttons that we have created
        self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
        self.forenameLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
        self.forenameBox.grid(row=1, column=1, padx=(0, 10))
        self.surnameLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
        self.surnameBox.grid(row=2, column=1, padx=(0, 10))
        self.contactLabel.grid(row=3, column=0, sticky='E', padx=(10, 0))
        self.contactBox.grid(row=3, column=1, padx=(0, 10))
        self.accessLevelLabel.grid(row=4, column=0, sticky='E', padx=(10, 0))
        self.accessLevelDropdown.grid(
            row=4, column=1, padx=(0, 10), sticky='ew')
        self.passwordLabel.grid(row=5, column=0, sticky='E', padx=(10, 0))
        self.passwordBox.grid(row=5, column=1, padx=(0, 10))
        self.passConfirmLabel.grid(row=6, column=0, sticky='E', padx=(10, 0))
        self.passConfirmBox.grid(row=6, column=1, padx=(0, 10))
        self.errorLabel.grid(row=7, column=0, columnspan=2)
        self.saveButton.grid(row=8, column=0, columnspan=2, pady=(0, 10))
        # Runs the save function when the user presses the 'enter' button (same as saveButton)
        self.staffWin.bind('<Return>', lambda event: self.saveStaff())

        center(self.staffWin)

    # Performs validation on inputs and
    # Saves staff as a new record in staffTbl
    def saveStaff(self):
        # Retrieves all inputs from add staff form
        forename = self.forenameVar.get().title().strip()
        surname = self.surnameVar.get().title().strip()
        contact = self.contactVar.get().replace(' ', '')
        staffAccessLevel = self.accessLevelVar.get()
        password = self.passwordVar.get()
        passConfirm = self.passConfirmVar.get()
        # Checks that all fields have been filled
        if forename and surname and contact and password and staffAccessLevel != 'Select...':
            # Checks that contact is of correct format for a phone
            if validatePhone(contact):
                # Checks that password and confimation are the same
                if password == passConfirm:
                    # Generates random salt and hashes password
                    salt = bcrypt.gensalt()
                    hashedPass = bcrypt.hashpw(password.encode('utf-8'), salt)
                    # Generates a random staffID, using the random module
                    staffID = 'ST' + \
                        str(''.join(['%s' % random.randint(0, 9)
                            for num in range(0, 5)]))
                    if tk.messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nStaffID:\t\t' + staffID +
                                              '\nName:\t\t' + forename + ' ' + surname +
                                              '\nContact:\t\t' + contact +
                                              '\nAccess Level:\t' + staffAccessLevel):
                        try:
                            executeSQL('INSERT INTO staffTbl VALUES (?,?,?,?,?,?,?)',
                                       (staffID, surname, forename, contact, staffAccessLevel, hashedPass, salt), False)
                            # Reloads records into treeview
                            loadDatabase(self.tree, 'staffTbl', False)
                            # Destroys add staff window and returns to view staff window
                            enableWindow(self.staffWin, self.returnButton, self.addStaffButton, self.editStaffButton,
                                         self.delStaffButton)
                            accesslevel(3, self.addStaffButton,
                                        self.editStaffButton, self.delStaffButton)
                            tk.messagebox.showinfo(
                                'Success!', 'Staff Details Saved')
                        except sqlite3.IntegrityError:  # Outputs error if staffID is not unique
                            self.errorVar.set(
                                'Error: Failed To Update Database.\nPlease Try Again')
                else:  # Outputs error if passwords don't match
                    self.errorVar.set("Error: Passwords Don't Match")
            else:  # Outputs error if contact is invalid
                self.errorVar.set('Error: Invalid Phone Number')
        else:  # Outputs error if not all fields are filled
            self.errorVar.set('Error: Please Fill All Fields')

    # Creates edit staff window
    def editStaff(self):
        if self.tree.selection():  # Runs IF a record is selected from treeview
            disableWindow(self.returnButton, self.addStaffButton,
                          self.editStaffButton, self.delStaffButton)
            for selected_item in self.tree.selection():
                # Finds record from database that matches selected record
                record = executeSQL('SELECT * FROM staffTbl WHERE staffID=?', (self.tree.set(selected_item, '#1'),),
                                    False)
                staffID = record[0]
                surname = record[1]
                forename = record[2]
                contact = record[3]
                staffAccessLevel = record[4]
                password = record[5]
                salt = record[6]
            self.staffWin = tk.Toplevel(self.root)
            self.staffWin.title('Edit Staff')
            self.staffWin.iconbitmap(config.icon)
            self.staffWin.protocol('WM_DELETE_WINDOW',
                                   lambda: (enableWindow(self.staffWin, self.returnButton, self.addStaffButton,
                                                         self.editStaffButton, self.delStaffButton),
                                            accesslevel(3, self.addStaffButton, self.editStaffButton,
                                                        self.delStaffButton)))
            self.editStaffFrame = tk.Frame(self.staffWin)
            self.editStaffFrame.pack()
            # Creates all the labels and entry boxes where necessary for each field
            self.detailLabel = tk.Label(
                self.editStaffFrame, text='Edit Staff Details:', font='none 11 bold')
            self.staffIDLabel = tk.Label(
                self.editStaffFrame, text='StaffID:', font='none 11')
            # staffID is only a label, so it cannot be edited by the user
            self.staffIDInsert = tk.Label(
                self.editStaffFrame, text=staffID, font='none 11')
            self.forenameLabel = tk.Label(
                self.editStaffFrame, text='Forename:', font='none 11')
            self.forenameVar = tk.StringVar()
            self.forenameBox = ttk.Entry(
                self.editStaffFrame, textvariable=self.forenameVar)
            self.surnameLabel = tk.Label(
                self.editStaffFrame, text='Surname:', font='none 11')
            self.surnameVar = tk.StringVar()
            self.surnameBox = ttk.Entry(
                self.editStaffFrame, textvariable=self.surnameVar)
            self.contactLabel = tk.Label(
                self.editStaffFrame, text='Phone No.:', font='none 11')
            self.contactVar = tk.StringVar()
            self.contactBox = ttk.Entry(
                self.editStaffFrame, textvariable=self.contactVar)
            # Creates a dropdown for the accesslevel to be selected from the given options
            self.accessLevelLabel = tk.Label(
                self.editStaffFrame, text='Access Level:', font='none 11')
            self.accessLevelVar = tk.StringVar()
            self.accessLevelDropdown = ttk.OptionMenu(
                self.editStaffFrame, self.accessLevelVar, '1', '1', '2', '3')
            if config.accessLevel < 3:
                self.accessLevelDropdown['state'] = 'disabled'
            self.passwordLabel = tk.Label(
                self.editStaffFrame, text='Password:', font='none 11')
            self.passwordVar = tk.StringVar()
            # Both password and new password only show *s for any input characters to
            # prevent shoulder surfers from seeing the input password
            self.passwordBox = ttk.Entry(
                self.editStaffFrame, show='•', textvariable=self.passwordVar)
            # Creates button (text only) to change password
            self.changePass = tk.Label(
                self.editStaffFrame, text='Change Password?', fg='blue', cursor='hand2')
            self.newPasswordLabel = tk.Label(
                self.editStaffFrame, text='New Password:', font='none 11')
            self.newPasswordVar = tk.StringVar()
            self.newPasswordBox = ttk.Entry(
                self.editStaffFrame, show='•', textvariable=self.newPasswordVar)
            self.errorVar = tk.StringVar()
            # Creates error label to display any errors
            self.errorLabel = tk.Label(
                self.editStaffFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
            # Creates save button, which calls the function saveEditsStaff
            self.saveButton = ttk.Button(self.editStaffFrame, text='Update Staff',
                                         command=lambda: self.saveEditStaff(staffID, password, salt))
            # Grids all the labels, entry boxes, dropdowns and buttons to the frame
            self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
            self.staffIDLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
            self.staffIDInsert.grid(row=1, column=1, padx=(0, 10))
            self.forenameLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
            self.forenameBox.grid(row=2, column=1, padx=(0, 10))
            self.surnameLabel.grid(row=3, column=0, sticky='E', padx=(10, 0))
            self.surnameBox.grid(row=3, column=1, padx=(0, 10))
            self.contactLabel.grid(row=4, column=0, sticky='E', padx=(10, 0))
            self.contactBox.grid(row=4, column=1, padx=(0, 10))
            self.accessLevelLabel.grid(
                row=5, column=0, sticky='E', padx=(10, 0))
            self.accessLevelDropdown.grid(
                row=5, column=1, padx=(0, 10), sticky='ew')
            self.passwordLabel.grid(row=6, column=0, sticky='E', padx=(10, 0))
            self.passwordBox.grid(row=6, column=1, padx=(0, 10))
            self.changePass.grid(row=7, column=0, columnspan=2)
            self.changePassVar = False
            self.changePass.bind('<Button-1>', lambda x: self.changePassword())
            self.errorLabel.grid(row=9, column=0, columnspan=2)
            self.saveButton.grid(row=10, column=0, columnspan=2, pady=(0, 10))
            # Inserts the currect fields into the boxes/ dropdowns
            self.forenameBox.insert(tk.INSERT, forename)
            self.surnameBox.insert(tk.INSERT, surname)
            self.contactBox.insert(tk.INSERT, contact)
            self.accessLevelVar.set(staffAccessLevel)
            # Runs the save function when the user presses the 'enter' button (same as saveButton)
            self.staffWin.bind(
                '<Return>', lambda event: self.saveEditStaff(staffID, password, salt))

            center(self.staffWin)

        else:  # Outputs error message if not record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')

    # Removes 'change password' option
    # Grids a new password label/entry box to the form
    def changePassword(self):
        self.changePass.grid_remove()
        self.newPasswordLabel.grid(row=7, column=0, sticky='E', padx=(10, 0))
        self.newPasswordBox.grid(row=7, column=1, padx=(0, 10))
        self.changePassVar = True

    # Performs validation on inputs and
    # Updates record in staffTbl
    def saveEditStaff(self, staffID, password, salt):
        # Retrieves all inputs from edit staff form
        newForename = self.forenameVar.get().title().strip()
        newSurname = self.surnameVar.get().title().strip()
        newContact = self.contactVar.get().replace(' ', '')
        newAccessLevel = self.accessLevelVar.get()
        oldPassword = self.passwordVar.get()
        if not self.changePassVar:
            newPassword = oldPassword
        else:
            newPassword = self.newPasswordVar.get()
        newPassword = bcrypt.hashpw(newPassword.encode('utf-8'), salt)
        # Checks that all fields have been filled
        if newForename and newSurname and newContact and newAccessLevel and (
                (self.changePassVar and newPassword) or (not self.changePassVar)):
            # Checks that contact is of the correct format
            if validatePhone(newContact):
                # Checks that password entered is the same as the password on record
                oldPassword = bcrypt.hashpw(oldPassword.encode('utf-8'), salt)
                if oldPassword == password:
                    # Creates confirmation dialogue to confirm details are correct
                    if tk.messagebox.askyesno('Confirm Changes', 'Are these details correct?\n\nStaffID:\t\t' + staffID +
                                              '\nName:\t\t' + newForename + ' ' + newSurname +
                                              '\nContact:\t\t' + newContact +
                                              '\nAccess Level:\t' + newAccessLevel):
                        # Updates record where the staffID matches the staffID selected
                        executeSQL('''UPDATE staffTbl SET staffSurname=?, staffForename=?, staffContact=?,
                                       accessLevel=?, password=? WHERE staffID=?''',
                                   (newSurname, newForename, newContact, newAccessLevel, newPassword, staffID), False)
                        # Reloads the records into the treeview, with the updated details
                        loadDatabase(self.tree, 'staffTbl', False)
                        # Destroys edit staff window and returns to view staff window
                        enableWindow(self.staffWin, self.returnButton, self.addStaffButton, self.editStaffButton,
                                     self.delStaffButton)
                        accesslevel(3, self.addStaffButton,
                                    self.editStaffButton, self.delStaffButton)
                        # Outputs success dialogue box
                        tk.messagebox.showinfo(
                            'Success!', 'Staff Details Updated')
                else:
                    # Outputs error if input password doesn't match password on record
                    self.errorVar.set('Error: Password Incorrect')
            else:
                # Outputs error if contact is invalid
                self.errorVar.set('Error: Invalid Phone Number')
        else:
            # Outputs error if not all fields are filled
            self.errorVar.set('Error: Please Fill All Fields')

    # Removes the selected record from the database
    # Only if it is not used in other records
    def delStaff(self):
        if self.tree.selection():
            for selected_item in self.tree.selection():
                staffID = self.tree.set(selected_item, '#1')
                staffAccessLevel = self.tree.set(selected_item, '#5')
            if not staffAccessLevel == 'x':
                # Searches tables where staffID might be used as a foreign key
                existsForeign = executeSQL(
                    'SELECT * FROM donationsTbl WHERE staffID = ?', (staffID,), True)
                existsForeign += executeSQL(
                    'SELECT * FROM orderTbl WHERE staffID = ?', (staffID,), True)
                existsForeign += executeSQL(
                    'SELECT * FROM foodDonatTbl WHERE staffID = ?', (staffID,), True)
                existsForeign += executeSQL(
                    'SELECT * FROM giveFoodTbl WHERE staffID = ?', (staffID,), True)
                existsForeign += executeSQL(
                    'SELECT * FROM expenditureTbl WHERE staffID = ?', (staffID,), True)
                # If staffID is NOT stored in any other tables
                if not existsForeign:
                    # Confirms that user wants to delete the record
                    if tk.messagebox.askokcancel('Delete', 'Are you sure you want to permanantly delete this record?'):
                        for selected_item in self.tree.selection():
                            # Delete the record from the database
                            executeSQL(
                                'DELETE FROM staffTbl WHERE staffID=?', (staffID,), False)
                            # Remove the item from the treeview
                            self.tree.delete(selected_item)
                else:  # If staffID is stored in other tables
                    if tk.messagebox.askokcancel('Delete',
                                                 'Error: Record is in use in other tables.\nRemove Login from System?'):
                        # Change access level to 'x'
                        executeSQL('UPDATE staffTbl SET accessLevel=?, password=? WHERE staffID=?', ('x', '', staffID),
                                   False)
                        # Reload records from database into treeview
                        loadDatabase(self.tree, 'staffTbl', False)
            else:
                tk.messagebox.showerror(
                    'Error', 'Record Already Removed From System')
        else:
            tk.messagebox.showerror('Error', 'No Record Selected')
