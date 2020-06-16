import tkinter as tk
from tkinter import ttk
import random
import sqlite3

from .. import config
from ..utils import treeview_sort_column, enableWindow, disableWindow, accesslevel, center
from ..sql import loadDatabase, executeSQL
from ..validation import validateFloat, validateInt


class itemWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('View Items')
        self.root.iconbitmap(config.icon)
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill='both', expand=True)
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.closeWindow())
        # Creates title label, 'View Item Records'
        self.titleLabel = tk.Label(
            self.frame, text='View Item Records', font='none 11')
        # Creates refresh button, to reload data from the database, and the return button, to close the item window
        # and return the user to the main menu
        self.refreshButton = ttk.Button(
            self.frame, text='↺', command=lambda: loadDatabase(self.tree, 'itemTbl', True))
        self.returnButton = ttk.Button(
            self.frame, text='Main Menu', command=lambda: self.closeWindow())
        # Saves input search value from searchBox as searchVar
        self.searchVar = tk.StringVar()
        self.searchBox = ttk.Entry(self.frame, textvariable=self.searchVar)
        # Creates a dropdown menu, with all the fields listed to search, set to itemID by default
        self.searchFieldVar = tk.StringVar()
        self.searchField = ttk.OptionMenu(self.frame, self.searchFieldVar, 'ItemID', 'ItemID', 'ItemName',
                                          'SalePrice', 'Quantity', 'SupplierCost', 'SupplierID')
        # Creates a 'search' button, which calls the search function when pressed
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
        columns = ('ItemID', 'ItemName', 'SalePrice',
                   'Quantity', 'SupplierCost', 'SupplierID')
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
        # Creates the add, edit and delete item buttons, which call their respective functions when clicked
        self.addItemButton = ttk.Button(
            self.frame, text='Add Item', command=lambda: self.addItem())
        self.editItemButton = ttk.Button(
            self.frame, text='Edit Item', command=lambda: self.editItem())
        self.delItemButton = ttk.Button(
            self.frame, text='Delete Item', command=lambda: self.delItem())
        # Grids the add, edit and delete buttons to the frame
        self.addItemButton.grid(row=2, column=4, padx=10,
                                ipadx=10, ipady=2, sticky='ew')
        self.editItemButton.grid(
            row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delItemButton.grid(row=4, column=4, padx=10,
                                ipadx=10, ipady=2, sticky='ew')
        # Runs the search function when the user presses the 'enter' button (same as searchButton)
        self.root.bind('<Return>', lambda event: self.search())
        # Calls the function to load the records from the database
        loadDatabase(self.tree, 'itemTbl', False)

        # Checks access level and disables relevant buttons
        accesslevel(2, self.addItemButton, self.editItemButton)
        accesslevel(3, self.delItemButton)

        center(self.root)

    def closeWindow(self):  # destroys Item window, opens main menu
        self.root.destroy()
        config.app.enableMenu()

    def search(self):
        # Retrieves the search value and search field from the inputs
        # Adds a wildcard symbol, %, to the end of the search value
        search = '%' + str(self.searchVar.get().strip().upper()) + '%'
        searchFieldVar = self.searchFieldVar.get()
        if searchFieldVar == 'ItemID':
            searchField = 'itemID'
        elif searchFieldVar == 'ItemName':
            searchField = 'itemName'
        elif searchFieldVar == 'SalePrice':
            searchField = 'salePrice'
        elif searchFieldVar == 'Quantity':
            searchField = 'quantity'
        elif searchFieldVar == 'SupplierCost':
            searchField = 'supplierCost'
        elif searchFieldVar == 'SupplierID':
            searchField = 'supplierID'
        # Clears the treeview of all other records
        self.tree.delete(*self.tree.get_children())
        # Selects records from itemsTbl where the search field matches the search value
        records = executeSQL(
            'SELECT * FROM itemTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records found into the treeview
            self.tree.insert('', 0, values=(
                i[0], i[1], i[2], i[3], i[4], i[5]))

    def addItem(self):
        disableWindow(self.returnButton, self.addItemButton,
                      self.editItemButton, self.delItemButton)
        # Selects all supplierIDs and names, and saves them to a list
        suppliers = executeSQL(
            'SELECT supplierID,supplierName FROM supplierTbl', (), True)
        supplierIDs = [(item[0:2]) for item in suppliers]
        if supplierIDs:
            self.itemWin = tk.Toplevel(self.root)
            self.itemWin.title('Add Items')
            self.itemWin.iconbitmap(config.icon)
            self.itemWin.protocol('WM_DELETE_WINDOW',
                                  lambda: (enableWindow(self.itemWin, self.returnButton, self.addItemButton,
                                                        self.editItemButton, self.delItemButton),
                                           accesslevel(
                                               2, self.addItemButton, self.editItemButton),
                                           accesslevel(3, self.delItemButton)))
            self.addItemFrame = tk.Frame(self.itemWin)
            self.addItemFrame.pack()
            # Creates all the labels and entry boxes for each field
            self.detailLabel = tk.Label(
                self.addItemFrame, text='Enter Item Details:', font='none 11 bold')
            self.nameLabel = tk.Label(
                self.addItemFrame, text='Item Name:', font='none 11')
            self.nameVar = tk.StringVar()
            self.nameBox = ttk.Entry(
                self.addItemFrame, textvariable=self.nameVar)
            self.salePriceLabel = tk.Label(
                self.addItemFrame, text='Sale Price:', font='none 11')
            self.salePriceVar = tk.StringVar()
            self.salePriceBox = ttk.Entry(
                self.addItemFrame, textvariable=self.salePriceVar)
            self.quantityLabel = tk.Label(
                self.addItemFrame, text='Quantity:', font='none 11')
            self.quantityVar = tk.StringVar()
            self.quantityBox = ttk.Spinbox(
                self.addItemFrame, from_=0, to=999, textvariable=self.quantityVar)
            self.supplierCostLabel = tk.Label(
                self.addItemFrame, text='Supplier Cost:', font='none 11')
            self.supplierCostVar = tk.StringVar()
            self.supplierCostBox = ttk.Entry(
                self.addItemFrame, textvariable=self.supplierCostVar)
            self.supplierIDLabel = tk.Label(
                self.addItemFrame, text='SupplierID:', font='none 11')
            # Creates a dropdown menu populated with all the donorIDs that we retrieved earlier
            self.supplierIDVar = tk.StringVar()
            self.supplierIDDropdown = ttk.OptionMenu(self.addItemFrame, self.supplierIDVar, 'Select...', *supplierIDs,
                                                     command=lambda x: (
                                                         self.supplierIDVar.set(self.supplierIDVar.get()[2:9])))
            # self.supplierIDVar.set('Select...')
            # Creates text variable and error label to output any errors
            self.errorVar = tk.StringVar()
            self.errorLabel = tk.Label(
                self.addItemFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
            # Creates save button, which calls the function saveItem when pressed
            self.saveButton = ttk.Button(self.addItemFrame, text='Save New Item',
                                         command=lambda: self.saveItem())
            # Grids all the labels, entry boxes, buttons and dropdowns to the frame
            self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
            self.nameLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
            self.nameBox.grid(row=1, column=1, padx=(0, 10), sticky='ew')
            self.salePriceLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
            self.salePriceBox.grid(row=2, column=1, padx=(0, 10), sticky='ew')
            self.quantityLabel.grid(row=3, column=0, sticky='E', padx=(10, 0))
            self.quantityBox.grid(row=3, column=1, padx=(0, 10), sticky='ew')
            self.supplierCostLabel.grid(
                row=4, column=0, sticky='E', padx=(10, 0))
            self.supplierCostBox.grid(
                row=4, column=1, padx=(0, 10), sticky='ew')
            self.supplierIDLabel.grid(
                row=5, column=0, sticky='E', padx=(10, 0))
            self.supplierIDDropdown.grid(
                row=5, column=1, padx=(0, 10), sticky='ew')
            self.errorLabel.grid(row=6, column=0, columnspan=2)
            self.saveButton.grid(row=7, column=0, columnspan=2, pady=(0, 10))
            # Runs the save function when the user presses the 'enter' button (same as saveButton)
            self.itemWin.bind('<Return>', lambda event: self.saveItem())

            center(self.itemWin)
        else:
            tk.messagebox.showerror('Error', 'No Suppliers Registered')
            self.closeWindow()

    def saveItem(self):
        # Retrieves all inputs from the form
        itemName = self.nameVar.get().strip().title()
        # Length limit prevents problems with displaying name in reports
        if len(itemName) < 17:
            supplierID = self.supplierIDVar.get()

            # checks if inputs entered are valid
            salePrice, salePriceValid = validateFloat(
                self.salePriceVar.get().strip())
            supplierCost, supplierCostValid = validateFloat(
                self.supplierCostVar.get().strip())
            quantity, quantityValid = validateInt(
                self.quantityVar.get().strip())

            if salePriceValid and supplierCostValid and quantityValid:
                # Checks that all fields have been entered
                if itemName and supplierID != 'Select...':
                    # Generates a random itemID, using the random module
                    itemID = 'IT' + \
                        str(''.join(['%s' % random.randint(0, 9)
                            for num in range(0, 5)]))
                    # Comfirmation box asks user to confirm that inputs are all correct
                    if tk.messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nItemID:\t\t' + itemID +
                                              '\nItem Name:\t' + itemName +
                                              '\nSale Price:\t£{:.2f}'.format(salePrice) +
                                              '\nQuantity:\t\t' + str(quantity) +
                                              '\nSupplier Cost:\t£{:.2f}'.format(supplierCost) +
                                              '\nSupplierID:\t' + supplierID):
                        try:
                            # Insert record into itemsTbl
                            executeSQL('INSERT INTO itemTbl VALUES (?,?,?,?,?,?)',
                                       (itemID, itemName, salePrice, quantity, supplierCost, supplierID), False)
                            # Reloads records into treeview
                            loadDatabase(self.tree, 'itemTbl', False)
                            # Destroys add item window and returns to view items window
                            enableWindow(self.itemWin, self.returnButton, self.addItemButton, self.editItemButton,
                                         self.delItemButton)
                            accesslevel(2, self.addItemButton,
                                        self.editItemButton)
                            accesslevel(3, self.delItemButton)
                            tk.messagebox.showinfo(
                                'Success!', 'New Item Saved')
                        except sqlite3.IntegrityError:
                            # Outputs error if itemID is not unique
                            self.errorVar.set(
                                'Error: Failed To Update Database.\nPlease Try Again')
                else:
                    # Outputs error if not all fields are filled
                    self.errorVar.set('Error: Please Fill All Fields')
            else:
                # Outputs error if input is invalid
                self.errorVar.set('Error: Invalid Input/s')
        else:
            # Outputs error if name too long
            self.errorVar.set('Error: Item Name Too Long (16)')

    def editItem(self):
        if self.tree.selection():  # Runs IF a record is selected from treeview
            disableWindow(self.returnButton, self.addItemButton,
                          self.editItemButton, self.delItemButton)
            for selected_item in self.tree.selection():
                # Finds records from itemsTbl that match the selected record
                items = executeSQL('SELECT * FROM itemTbl WHERE itemID=?',
                                   (self.tree.set(selected_item, '#1'),), False)
                itemID = items[0]
                itemName = items[1]
                salePrice = items[2]
                quantity = items[3]
                supplierCost = items[4]
                supplierID = items[5]
            # Selects all supplierIDs and names, and saves them to a list
            suppliers = executeSQL(
                'SELECT supplierID,supplierName FROM supplierTbl', (), True)
            supplierIDs = [(item[0:2]) for item in suppliers]
            if supplierIDs:
                self.itemWin = tk.Toplevel(self.root)
                self.itemWin.title('Edit Items')
                self.itemWin.iconbitmap(config.icon)
                self.itemWin.protocol('WM_DELETE_WINDOW',
                                      lambda: (enableWindow(self.itemWin, self.returnButton, self.addItemButton,
                                                            self.editItemButton, self.delItemButton),
                                               accesslevel(
                                                   2, self.addItemButton, self.editItemButton),
                                               accesslevel(3, self.delItemButton)))
                self.editItemFrame = tk.Frame(self.itemWin)
                self.editItemFrame.pack()
                # Creates all the labels and entry boxes for each field
                self.detailLabel = tk.Label(
                    self.editItemFrame, text='Edit Item Details:', font='none 11 bold')
                self.itemIDLabel = tk.Label(
                    self.editItemFrame, text='ItemID:', font='none 11')
                self.itemIDInsert = tk.Label(
                    self.editItemFrame, text=itemID, font='none 11')
                self.nameLabel = tk.Label(
                    self.editItemFrame, text='Item Name:', font='none 11')
                self.nameVar = tk.StringVar()
                self.nameBox = ttk.Entry(
                    self.editItemFrame, textvariable=self.nameVar)
                self.salePriceLabel = tk.Label(
                    self.editItemFrame, text='Sale Price:', font='none 11')
                self.salePriceVar = tk.StringVar()
                self.salePriceBox = ttk.Entry(
                    self.editItemFrame, textvariable=self.salePriceVar)
                self.quantityLabel = tk.Label(
                    self.editItemFrame, text='Quantity:', font='none 11')
                self.quantityVar = tk.StringVar()
                self.quantityBox = ttk.Spinbox(
                    self.editItemFrame, from_=0, to=999, textvariable=self.quantityVar)
                self.supplierCostLabel = tk.Label(
                    self.editItemFrame, text='Supplier Cost:', font='none 11')
                self.supplierCostVar = tk.StringVar()
                self.supplierCostBox = ttk.Entry(
                    self.editItemFrame, textvariable=self.supplierCostVar)
                self.supplierIDLabel = tk.Label(
                    self.editItemFrame, text='SupplierID:', font='none 11')
                # Creates a dropdown menu populated with all the donorIDs that we retrieved earlier
                self.supplierIDVar = tk.StringVar()
                self.supplierIDDropdown = ttk.OptionMenu(self.editItemFrame, self.supplierIDVar, 'Select...',
                                                         *supplierIDs,
                                                         command=lambda x: (
                                                             self.supplierIDVar.set(self.supplierIDVar.get()[2:9])))
                self.supplierIDVar.set('Select...')
                # Creates text variable and error label to output any errors
                self.errorVar = tk.StringVar()
                self.errorLabel = tk.Label(
                    self.editItemFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
                # Creates save button, which calls the function saveItem when pressed
                self.saveButton = ttk.Button(self.editItemFrame, text='Update Item',
                                             command=lambda: self.saveEditItem(itemID))
                # Grids all the labels, entry boxes, buttons and dropdowns to the frame
                self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
                self.itemIDLabel.grid(
                    row=1, column=0, sticky='E', padx=(10, 0))
                self.itemIDInsert.grid(row=1, column=1, padx=(0, 10))
                self.nameLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
                self.nameBox.grid(row=2, column=1, padx=(0, 10), sticky='ew')
                self.salePriceLabel.grid(
                    row=3, column=0, sticky='E', padx=(10, 0))
                self.salePriceBox.grid(
                    row=3, column=1, padx=(0, 10), sticky='ew')
                self.quantityLabel.grid(
                    row=4, column=0, sticky='E', padx=(10, 0))
                self.quantityBox.grid(
                    row=4, column=1, padx=(0, 10), sticky='ew')
                self.supplierCostLabel.grid(
                    row=5, column=0, sticky='E', padx=(10, 0))
                self.supplierCostBox.grid(
                    row=5, column=1, padx=(0, 10), sticky='ew')
                self.supplierIDLabel.grid(
                    row=6, column=0, sticky='E', padx=(10, 0))
                self.supplierIDDropdown.grid(
                    row=6, column=1, padx=(0, 10), sticky='ew')
                self.errorLabel.grid(row=7, column=0, columnspan=2)
                self.saveButton.grid(
                    row=8, column=0, columnspan=2, pady=(0, 10))
                # Inserts all the current values into the entry boxes
                self.nameBox.insert(tk.INSERT, itemName)
                self.salePriceBox.insert(tk.INSERT, salePrice)
                self.quantityVar.set(quantity)
                self.supplierCostBox.insert(tk.INSERT, supplierCost)
                self.supplierIDVar.set(supplierID)

                # Runs the save function when the user presses the 'enter' button (same as saveButton)
                self.itemWin.bind(
                    '<Return>', lambda event: self.saveEditItem(itemID))

                center(self.itemWin)
            else:
                tk.messagebox.showerror('Error', 'No Suppliers Registered')
                self.closeWindow()

        else:
            # Outputs error message is no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')

    def saveEditItem(self, itemID):
        # Retrieves all inputs from the form
        itemName = self.nameVar.get().strip().title()
        # Length limit prevents problems with displaying name in reports
        if len(itemName) < 17:
            supplierID = self.supplierIDVar.get()

            # checks if values entered are a valid
            salePrice, saleValid = validateFloat(
                self.salePriceVar.get().strip())
            supplierCost, supplierValid = validateFloat(
                self.supplierCostVar.get().strip())
            quantity, quantityValid = validateInt(
                self.quantityVar.get().strip())

            if saleValid and supplierValid and quantityValid:
                # Checks that all fields have been entered
                if itemName and supplierID != 'Select...':
                    # Confirmation box asks user to confirm that inputs are all correct
                    if tk.messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nItemID:\t\t' + itemID +
                                              '\nItem Name:\t' + itemName +
                                              '\nSale Price:\t£{:.2f}'.format(salePrice) +
                                              '\nQuantity:\t\t' + str(quantity) +
                                              '\nSupplier Cost:\t£{:.2f}'.format(supplierCost) +
                                              '\nSupplierID:\t' + supplierID):
                        # Updates record in itemsTbl
                        executeSQL('''UPDATE itemTbl SET itemName=?, salePrice=?, quantity=?, 
                                    supplierCost=?, supplierID=? WHERE itemID=?''',
                                   (itemName, salePrice, quantity, supplierCost, supplierID, itemID), False)
                        # Reloads records into treeview, with updated values
                        loadDatabase(self.tree, 'itemTbl', False)
                        # Destroys edit item window and returns to view items window
                        enableWindow(self.itemWin, self.returnButton, self.addItemButton, self.editItemButton,
                                     self.delItemButton)
                        accesslevel(2, self.addItemButton, self.editItemButton)
                        accesslevel(3, self.delItemButton)
                        tk.messagebox.showinfo(
                            'Success!', 'Item Details Updated')
                else:
                    # Outputs error if not all fields are filled
                    self.errorVar.set('Error: Please Fill All Fields')
            else:
                # Outputs error if input is invalid
                self.errorVar.set('Error: Invalid Input/s')
        else:
            self.errorVar.set('Error: Item Name Too Long (16)')

    def delItem(self):
        if self.tree.selection():
            # Retreives the itemID from the record selected in the treeview
            for selected_item in self.tree.selection():
                itemID = self.tree.set(selected_item, '#1')
            # Asks the user for confimation that they want to permanently delete this record
            if tk.messagebox.askokcancel('Delete', 'Are you sure you want to permanently delete this record?'):
                for selected_item in self.tree.selection():
                    # Removes the record from itemsTbl
                    executeSQL('DELETE FROM itemTbl WHERE itemID=?',
                               (itemID,), False)
                    # Removes the record from the treeview
                    self.tree.delete(selected_item)
        else:
            # Outputs error message is no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')
