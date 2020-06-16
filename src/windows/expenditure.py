import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime
import random
import sqlite3

from .. import config
from ..utils import treeview_sort_column, enableWindow, disableWindow, accesslevel, center
from ..sql import loadDatabase, executeSQL
from ..validation import validateFloat
from ..report import expenditureReport


class expenditureWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('View Expenditures')
        self.root.iconbitmap(config.icon)
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill='both', expand=True)
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.closeWindow())
        # Creates title label, 'View Expenditure Records'
        self.titleLabel = tk.Label(
            self.frame, text='View Expenditure Records', font='none 11')
        # Creates refresh button, to reload data from the database, and the return button,
        # to close the expenditure window and return the user to the main menu
        self.refreshButton = ttk.Button(self.frame, text='↺',
                                        command=lambda: loadDatabase(self.tree, 'expenditureTbl', True))
        self.returnButton = ttk.Button(
            self.frame, text='Main Menu', command=lambda: self.closeWindow())
        # Saves input search value from searchBox as searchVar
        self.searchVar = tk.StringVar()
        self.searchBox = ttk.Entry(self.frame, textvariable=self.searchVar)
        # Creates a dropdown menu, with all the fields listed, set to expenditureID by default
        self.searchFieldVar = tk.StringVar()
        self.searchField = ttk.OptionMenu(self.frame, self.searchFieldVar, 'ExpenditureID', 'ExpenditureID', 'Amount',
                                          'Details', 'Date', 'StaffID')
        # Creates a 'Search' button, which calls the search function when pressed
        self.searchButton = ttk.Button(
            self.frame, text='Search', command=lambda: self.search())
        # Creates a 'Create report' button, which launches the report function
        self.reportButton = ttk.Button(
            self.frame, text='Create Report', command=lambda: self.report())
        # Grids all the above labels, buttons and entry boxes to the frame
        self.titleLabel.grid(row=0, column=1, sticky='ns')
        self.refreshButton.grid(row=0, column=4, pady=10)
        self.returnButton.grid(row=0, column=0, pady=10,
                               padx=10, ipadx=10, ipady=2, sticky='w')
        self.searchField.grid(row=1, column=0, padx=10, sticky='ew')
        self.searchBox.grid(row=1, column=1, sticky='ew')
        self.searchButton.grid(row=1, column=2, pady=10,
                               padx=(10, 0), ipadx=10)
        self.reportButton.grid(row=1, column=4, padx=10,
                               ipadx=10, ipady=2, sticky='ew')
        # Creates the treeview, defining each column and naming its heading with the relevant field name
        columns = ('ExpenditureID', 'Amount', 'Details', 'Date', 'StaffID')
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
        # Creates the add, edit and delete expenditure buttons, which calls their respective functions when clicked
        self.addExpenditureButton = ttk.Button(self.frame, text='Add Expenditure',
                                               command=lambda: self.addExpenditure())
        self.editExpenditureButton = ttk.Button(self.frame, text='Edit Expenditure',
                                                command=lambda: self.editExpenditure())
        self.delExpenditureButton = ttk.Button(self.frame, text='Delete Expenditure',
                                               command=lambda: self.delExpenditure())
        # Grids the add, edit and delete expenditure buttons to the frame
        self.addExpenditureButton.grid(
            row=2, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.editExpenditureButton.grid(
            row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delExpenditureButton.grid(
            row=4, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        # Runs the search function when the user presses the 'enter' button (same as searchButton)
        self.root.bind('<Return>', lambda event: self.search())
        # Calls function to load the records from the database
        loadDatabase(self.tree, 'expenditureTbl', False)

        # Checks access level and disables relevant buttons
        accesslevel(2, self.addExpenditureButton, self.editExpenditureButton)
        accesslevel(3, self.delExpenditureButton)

        center(self.root)

    def closeWindow(self):  # destroys ExpenditureWindow, opens main menu
        self.root.destroy()
        config.app.enableMenu()

    def search(self):
        # Retrieves the search value and search field from the inputs
        # Adds a wildcard symbol, %, to the end of the search value
        search = '%' + str(self.searchVar.get().strip().upper()) + '%'
        searchFieldVar = self.searchFieldVar.get()
        if searchFieldVar == 'ExpenditureID':
            searchField = 'expenditureID'
        elif searchFieldVar == 'Amount':
            searchField = 'amount'
        elif searchFieldVar == 'Details':
            searchField = 'details'
        elif searchFieldVar == 'Date':
            searchField = 'date'
        elif searchFieldVar == 'StaffID':
            searchField = 'staffID'
        # Clears the treeview of all other records
        self.tree.delete(*self.tree.get_children())
        # Selects records from expenditureTbl where the search field matches the search value
        records = executeSQL(
            'SELECT * FROM expenditureTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records found into the treeview
            self.tree.insert('', 0, values=(i[0], i[1], i[2], i[3], i[4]))

    def addExpenditure(self):
        disableWindow(self.returnButton, self.addExpenditureButton, self.editExpenditureButton,
                      self.delExpenditureButton)
        self.expenditureWin = tk.Toplevel(self.root)
        self.expenditureWin.title('Add Expenditure')
        self.expenditureWin.iconbitmap(config.icon)
        self.expenditureWin.protocol('WM_DELETE_WINDOW', lambda: (
            enableWindow(self.expenditureWin, self.returnButton, self.addExpenditureButton,
                         self.editExpenditureButton, self.delExpenditureButton),
            accesslevel(2, self.addExpenditureButton,
                        self.editExpenditureButton),
            accesslevel(3, self.delExpenditureButton)))
        self.addExpenditureFrame = tk.Frame(self.expenditureWin)
        self.addExpenditureFrame.pack()
        # Creates all the labels and entry boxes for each field
        self.detailLabel = tk.Label(
            self.addExpenditureFrame, text='Enter Expenditure Details:', font='none 11 bold')
        self.amountLabel = tk.Label(
            self.addExpenditureFrame, text='Amount:', font='none 11')
        self.amountVar = tk.StringVar()
        self.amountBox = ttk.Entry(
            self.addExpenditureFrame, textvariable=self.amountVar)
        self.detailsLabel = tk.Label(
            self.addExpenditureFrame, text='Details:', font='none 11')
        self.detailsBox = tk.Text(self.addExpenditureFrame, width=15, height=5)
        self.dateLabel = tk.Label(self.addExpenditureFrame,
                                  text='Date:', font='none 11')
        self.dateVar = tk.StringVar()
        # Creates a calendar widget to pick the date from
        self.calendar = DateEntry(self.addExpenditureFrame, state='readonly',
                                  date_pattern='DD/MM/YYYY', textvariable=self.dateVar,
                                  showweeknumbers=False, maxdate=datetime.today())
        # Creates text variable and error label to output any error messages
        self.errorVar = tk.StringVar()
        self.errorLabel = tk.Label(
            self.addExpenditureFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
        # Creates save button, which calls the function saveExpenditure when pressed
        self.saveButton = ttk.Button(self.addExpenditureFrame, text='Save New Expenditure',
                                     command=lambda: self.saveExpenditure())
        # Grids all the labels, entry boxes and buttons that we have created to the frame
        self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
        self.amountLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
        self.amountBox.grid(row=1, column=1, padx=(0, 10))
        self.detailsLabel.grid(row=2, column=0, sticky='NE', padx=(10, 0))
        self.detailsBox.grid(row=2, column=1, padx=(0, 10))
        self.dateLabel.grid(row=3, column=0, sticky='E', padx=(10, 0))
        self.calendar.grid(row=3, column=1, padx=(0, 10), sticky='ew')
        self.errorLabel.grid(row=4, column=0, columnspan=2)
        self.saveButton.grid(row=5, column=0, columnspan=2, pady=(0, 10))
        # Runs the saveExpenditure function when the user presses the 'enter' button (same as saveButton)
        self.expenditureWin.bind(
            '<Return>', lambda event: self.saveExpenditure())

        center(self.expenditureWin)

    def saveExpenditure(self):
        # Retrieves amount, details and date from the previous form

        # Checks that amount is valid
        amount, amountValid = validateFloat(self.amountVar.get().strip())

        details = self.detailsBox.get('1.0', tk.END).strip()
        date = self.dateVar.get()

        if amountValid:
            # Checks that all fields have been filled
            if amount and details and date:
                if len(details) < 36:
                    # Generates a random expenditureID, using the random module
                    expenditureID = 'EX' + \
                        str(''.join(['%s' % random.randint(0, 9)
                            for num in range(0, 5)]))
                    # Asks for user confimation of the input details
                    if tk.messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nExpenditureID:\t'
                                              + expenditureID + '\nAmount:\t\t£{:.2f}'.format(amount) +
                                              '\nDetails:\t\t' + details + '\nDate:\t\t' + date):
                        try:
                            # Inserts record into expenditureTbl
                            executeSQL('INSERT INTO expenditureTbl VALUES (?,?,?,?,?)',
                                       (expenditureID, amount, details, date, config.userID), False)
                            # Reloads records into treeview
                            loadDatabase(self.tree, 'expenditureTbl', False)
                            # Destroys add expenditure toplevel and returns to view expenditures window
                            enableWindow(self.expenditureWin, self.returnButton, self.addExpenditureButton,
                                         self.editExpenditureButton, self.delExpenditureButton)
                            accesslevel(2, self.addExpenditureButton,
                                        self.editExpenditureButton)
                            accesslevel(3, self.delExpenditureButton)
                            tk.messagebox.showinfo(
                                'Success!', 'New Expenditure Saved')
                        except sqlite3.IntegrityError:  # Outputs error message if expenditureID is not unique
                            self.errorVar.set(
                                'Error: Failed To Update Database.\nPlease Try Again')
                else:
                    self.errorVar.set('Error: Details too long (35)')
            else:  # Outputs error if not all fields are filled
                self.errorVar.set('Error: Please Fill All Fields')
        else:
            self.errorVar.set('Error: Enter Valid Amount')

    def editExpenditure(self):
        if self.tree.selection():  # Runs IF a record is selected from treeview
            disableWindow(self.returnButton, self.addExpenditureButton, self.editExpenditureButton,
                          self.delExpenditureButton)
            for selected_item in self.tree.selection():
                # Finds record from database that matches selected record
                expenditure = executeSQL('SELECT * FROM expenditureTbl WHERE expenditureID=?',
                                         (self.tree.set(selected_item, '#1'),), False)
                expenditureID = expenditure[0]
                amount = expenditure[1]
                details = expenditure[2]
                date = expenditure[3]
            self.expenditureWin = tk.Toplevel(self.root)
            self.expenditureWin.title('Edit Expenditure')
            self.expenditureWin.iconbitmap(config.icon)
            self.expenditureWin.protocol('WM_DELETE_WINDOW', lambda: (
                enableWindow(self.expenditureWin, self.returnButton, self.addExpenditureButton,
                             self.editExpenditureButton, self.delExpenditureButton),
                accesslevel(2, self.addExpenditureButton,
                            self.editExpenditureButton),
                accesslevel(3, self.delExpenditureButton)))
            self.editExpenditureFrame = tk.Frame(self.expenditureWin)
            self.editExpenditureFrame.pack()
            # Creates all the labels and entry boxes for each field
            self.detailLabel = tk.Label(
                self.editExpenditureFrame, text='Update Expenditure Details:', font='none 11 bold')
            self.expenditureIDLabel = tk.Label(
                self.editExpenditureFrame, text='ExpenditureID:', font='none 11')
            self.expenditureIDInsert = tk.Label(
                self.editExpenditureFrame, text=expenditureID, font='none 11')
            self.amountLabel = tk.Label(
                self.editExpenditureFrame, text='Amount:', font='none 11')
            self.amountVar = tk.StringVar()
            self.amountBox = ttk.Entry(
                self.editExpenditureFrame, textvariable=self.amountVar)
            self.detailsLabel = tk.Label(
                self.editExpenditureFrame, text='Details:', font='none 11')
            self.detailsBox = tk.Text(
                self.editExpenditureFrame, width=15, height=5)
            self.dateLabel = tk.Label(
                self.editExpenditureFrame, text='Date:', font='none 11')
            self.dateVar = tk.StringVar()
            # Creates a calendar widget to pick the date from
            self.calendar = DateEntry(self.editExpenditureFrame, state='readonly',
                                      date_pattern='DD/MM/YYYY', textvariable=self.dateVar,
                                      showweeknumbers=False, maxdate=datetime.today())
            # Creates text variable and error label to output any error messages
            self.errorVar = tk.StringVar()
            self.errorLabel = tk.Label(self.editExpenditureFrame, textvariable=self.errorVar, font='none 11 bold',
                                       fg='red')
            # Creates save button, which calls the function saveExpenditure when pressed
            self.saveButton = ttk.Button(self.editExpenditureFrame, text='Update Expenditure',
                                         command=lambda: self.saveEditExpenditure(expenditureID))
            # Grids all the labels, entry boxes and buttons that we have created to the frame
            self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
            self.expenditureIDLabel.grid(
                row=1, column=0, sticky='E', padx=(10, 0))
            self.expenditureIDInsert.grid(row=1, column=1, padx=(0, 10))
            self.amountLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
            self.amountBox.grid(row=2, column=1, padx=(0, 10))
            self.detailsLabel.grid(row=3, column=0, sticky='NE', padx=(10, 0))
            self.detailsBox.grid(row=3, column=1, padx=(0, 10))
            self.dateLabel.grid(row=4, column=0, sticky='E', padx=(10, 0))
            self.calendar.grid(row=4, column=1, padx=(0, 10), sticky='ew')
            self.errorLabel.grid(row=5, column=0, columnspan=2)
            self.saveButton.grid(row=6, column=0, columnspan=2, pady=(0, 10))

            self.amountBox.insert(tk.INSERT, amount)
            self.detailsBox.insert(tk.INSERT, details)
            self.dateVar.set(date)
            # Runs the saveExpenditure function when the user presses the 'enter' button (same as saveButton)
            self.expenditureWin.bind(
                '<Return>', lambda event: self.saveEditExpenditure(expenditureID))

            center(self.expenditureWin)

        else:  # Outputs error message if no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')

    def saveEditExpenditure(self, expenditureID):
        # Retrieves amount, details and date from the previous form

        # Checks that newAmount is valid
        newAmount, newAmountValid = validateFloat(self.amountVar.get().strip())

        newDetails = self.detailsBox.get('1.0', tk.END).strip()
        newDate = self.dateVar.get()
        if newAmountValid:
            # Checks that all fields have been filled
            if newAmount and newDetails and newDate:
                if len(newDetails) < 36:
                    # Creates confirmation dialogue to confirm details are correct
                    if tk.messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nExpenditureID:\t' +
                                              expenditureID + '\nAmount:\t\t£{:.2f}'.format(newAmount) +
                                              '\nDetails:\t\t' + newDetails + '\nDate:\t\t' + newDate):
                        # Updates record where the expenditureID matches the record selected
                        executeSQL('''UPDATE expenditureTbl SET amount=?, details=?, date=?
                                       WHERE expenditureID=?''', (newAmount, newDetails, newDate, expenditureID), False)
                        # Reloads the records into the treeview, with the updated details
                        loadDatabase(self.tree, 'expenditureTbl', False)
                        # Destroys edit expenditure window and returns to view expenditures window
                        enableWindow(self.expenditureWin, self.returnButton, self.addExpenditureButton,
                                     self.editExpenditureButton, self.delExpenditureButton)
                        accesslevel(2, self.addExpenditureButton,
                                    self.editExpenditureButton)
                        accesslevel(3, self.delExpenditureButton)
                        tk.messagebox.showinfo(
                            'Success!', 'Expenditure Details Updated')
                else:
                    self.errorVar.set('Error: Details too long (35)')
            else:  # Outputs error if not all fields have been filled
                self.errorVar.set('Error: Please Fill All Fields')
        else:
            self.errorVar.set('Error: Enter Valid Amount')

    def delExpenditure(self):
        if self.tree.selection():
            for selected_item in self.tree.selection():
                expenditureID = self.tree.set(selected_item, '#1')
            # Confirms that the user wants to permanently delete the record
            if tk.messagebox.askokcancel('Delete', 'Are you sure you want to permanently delete this record?'):
                for selected_item in self.tree.selection():
                    # Deletes the record from expenditureTbl
                    executeSQL(
                        'DELETE FROM expenditureTbl WHERE expenditureID=?', (expenditureID,), False)
                    # Removes the record from the treeview
                    self.tree.delete(selected_item)
        else:  # Outputs error message if no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')

    def report(self):
        disableWindow(self.reportButton, self.returnButton, self.addExpenditureButton, self.editExpenditureButton,
                      self.delExpenditureButton)
        self.expenditureWin = tk.Toplevel(self.root)
        self.expenditureWin.title('Expenditure Report')
        self.expenditureWin.iconbitmap(config.icon)
        self.expenditureWin.protocol('WM_DELETE_WINDOW',
                                     lambda: (enableWindow(self.expenditureWin, self.reportButton, self.returnButton,
                                                           self.addExpenditureButton, self.editExpenditureButton,
                                                           self.delExpenditureButton),
                                              accesslevel(
                                                  2, self.addExpenditureButton, self.editExpenditureButton),
                                              accesslevel(3, self.delExpenditureButton)))
        self.expenditureReportFrame = tk.Frame(self.expenditureWin)
        self.expenditureReportFrame.pack()
        # Creates labels and entry boxes for start/end date of report
        self.detailLabel = tk.Label(
            self.expenditureReportFrame, text='Enter Report Parameters', font='none 11 bold')
        self.startDateLabel = tk.Label(
            self.expenditureReportFrame, text='Start Date:', font='none 11')
        self.startDateVar = tk.StringVar()
        self.startCalendar = DateEntry(self.expenditureReportFrame, state='readonly',
                                       date_pattern='DD/MM/YYYY', textvariable=self.startDateVar,
                                       showweeknumbers=False, maxdate=datetime.today())
        self.endDateLabel = tk.Label(
            self.expenditureReportFrame, text='End Date:', font='none 11')
        self.endDateVar = tk.StringVar()
        self.endCalendar = DateEntry(self.expenditureReportFrame, state='readonly',
                                     date_pattern='DD/MM/YYYY', textvariable=self.endDateVar,
                                     showweeknumbers=False, maxdate=datetime.today())
        # Creates a text variable and error label to output any errors to
        self.errorVar = tk.StringVar()
        self.errorLabel = tk.Label(self.expenditureReportFrame,
                                   textvariable=self.errorVar, font='none 11 bold', fg='red')
        # Creates a button which runs the generateReport function when pressed
        self.enterButton = ttk.Button(self.expenditureReportFrame, text='Generate Report',
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
        self.expenditureWin.bind(
            '<Return>', lambda event: self.generateReport())

        center(self.expenditureWin)

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
            self.expenditureReportWin = tk.Toplevel(self.expenditureWin)
            self.expenditureReportWin.title('Expenditure Report')
            self.expenditureReportWin.iconbitmap(config.icon)
            self.expenditureReportFrame = tk.Frame(self.expenditureReportWin)
            self.expenditureReportFrame.pack(fill='both', expand=True)
            self.expenditureReportWin.protocol('WM_DELETE_WINDOW',
                                               lambda: enableWindow(self.expenditureReportWin, self.enterButton))
            self.titleLabel = tk.Label(self.expenditureReportFrame, text='Kingfisher Trust', font='algerian 14 bold',
                                       fg='#2380b7')
            self.detailLabel = tk.Label(
                self.expenditureReportFrame, text='Expenditure Report', font='none 12 bold')
            # Creates a label detailing the date constraints of the report, as input by the user
            self.datesLabel = tk.Label(self.expenditureReportFrame,
                                       text='From ' +
                                       str(datetime.isoformat(
                                           self.startDate)[:10])
                                       + ' to ' + str(datetime.isoformat(self.endDate)[:10]) + ':')
            # Creates a button allowing the user to save the report as a PDF file
            self.pdfButton = ttk.Button(self.expenditureReportFrame, text='Save to PDF',
                                        command=lambda: (disableWindow(self.pdfButton),
                                                         expenditureReport(self.startDate, self.endDate,
                                                                           records, self.totalSpend)))
            # Grids the above labels and buttons
            self.titleLabel.grid(row=0, column=0, columnspan=3, pady=10)
            self.detailLabel.grid(row=1, column=0, columnspan=3)
            self.datesLabel.grid(row=2, column=0, padx=10, sticky='w')
            self.pdfButton.grid(row=2, column=2, padx=10, sticky='E')
            # Creates a treeview to insert all the relevant order records
            columns = ('ExpenditureID', 'Amount', 'Details', 'Date', 'StaffID')
            self.reporttree = ttk.Treeview(self.expenditureReportFrame, columns=columns, show='headings',
                                           selectmode='none')
            for col in columns:
                self.reporttree.column(col, width=100, minwidth=100)
                self.reporttree.heading(col, text=col)
            self.reporttree.grid(row=6, column=0, sticky='ewns',
                                 columnspan=3, padx=(10, 0), pady=10)
            self.expenditureReportFrame.columnconfigure(
                [0, 1, 2], weight=1)  # column with treeview
            self.expenditureReportFrame.rowconfigure(
                6, weight=1)  # row with treeview

            # Connects to database and selects all records from expenditureTbl
            self.records = executeSQL('SELECT * FROM expenditureTbl', (), True)
            self.totalSpend = 0
            records = []
            # Finds records which fall within the given dates
            for i in self.records:
                date = datetime.strptime(i[3], '%d/%m/%Y')
                if self.startDate <= date <= self.endDate:
                    # Cumulates the total amount spent within the time period
                    self.totalSpend += float(i[1])
                    # Inserts the record into the treeview
                    record = i
                    records.append(record)
                    self.reporttree.insert('', 0, values=record)
            # Creates a label with the total amount donated
            self.spentLabel = tk.Label(self.expenditureReportFrame,
                                       text=str('Total Cost = £{:.2f}'.format(self.totalSpend)))
            self.spentLabel.grid(row=3, column=0, padx=10, sticky='w')

            self.scrollbar = ttk.Scrollbar(self.expenditureReportFrame, orient='vertical',
                                           command=self.reporttree.yview)
            self.scrollbar.grid(row=6, column=3, sticky='ns',
                                pady=10, padx=(0, 10))
            self.reporttree.configure(
                yscrollcommand=self.scrollbar.set, selectmode='browse')

            center(self.expenditureReportWin)

        except ValueError:
            # Outputs an error if the dates input are invalid
            self.errorVar.set('Error: Invalid Input\nDD/MM/YYYY')
