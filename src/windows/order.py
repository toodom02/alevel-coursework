import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime
import random
import sqlite3

from .. import config
from ..utils import treeview_sort_column, enableWindow, disableWindow, accesslevel, center
from ..sql import loadDatabase, executeSQL
from ..report import orderReport

from .customer import customerWindow


class orderWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('View Orders')
        self.root.iconbitmap(config.icon)
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill='both', expand=True)
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.closeWindow())
        # Creates title label, 'View Order Records'
        self.titleLabel = tk.Label(
            self.frame, text='View Order Records', font='none 11')
        # Creates refresh button, to reload data from the database, and the return button, to close the order window
        # and return the user to the main menu
        self.refreshButton = ttk.Button(
            self.frame, text='↺', command=lambda: loadDatabase(self.tree, 'orderTbl', True))
        self.returnButton = ttk.Button(
            self.frame, text='Main Menu', command=lambda: self.closeWindow())
        # Saves input search value from searchBox as searchVar
        self.searchVar = tk.StringVar()
        self.searchBox = ttk.Entry(self.frame, textvariable=self.searchVar)
        # Creates a dropdown menu, with all the fields listed to search, set to orderID by default
        self.searchFieldVar = tk.StringVar()
        self.searchField = ttk.OptionMenu(self.frame, self.searchFieldVar, 'OrderNo', 'OrderNo', 'CustomerID',
                                          'OrderTotal', 'Date', 'StaffID')
        # Creates a 'search' button, which calls the search function when pressed
        self.searchButton = ttk.Button(
            self.frame, text='Search', command=lambda: self.search())
        self.customersButton = tk.Label(
            self.frame, text='View Customers', fg='blue', cursor='hand2')
        self.customersButton.bind('<Button-1>', lambda x: self.customer())
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
        self.customersButton.grid(row=0, column=2)
        # Creates the treeview, defining each column and naming its heading with the relevant field name
        columns = ('OrderNo', 'CustomerID', 'OrderTotal', 'Date', 'StaffID')
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
        # Creates the add, edit and delete order buttons, which call their respective functions when clicked
        self.addOrderButton = ttk.Button(
            self.frame, text='Add Order', command=lambda: self.addOrder())
        self.editOrderButton = ttk.Button(
            self.frame, text='Edit Order', command=lambda: self.editOrder())
        self.delOrderButton = ttk.Button(
            self.frame, text='Delete Order', command=lambda: self.delOrder())
        # Grids the add, edit and delete buttons to the frame
        self.addOrderButton.grid(
            row=2, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.editOrderButton.grid(
            row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delOrderButton.grid(
            row=4, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        # Runs the search function when the user presses the 'enter' button (same as searchButton)
        self.root.bind('<Return>', lambda event: self.search())
        # Calls the function to load the records from the database
        loadDatabase(self.tree, 'orderTbl', False)

        # Checks access level and disables relevant buttons
        accesslevel(2, self.addOrderButton, self.editOrderButton)
        accesslevel(3, self.delOrderButton)

        center(self.root)

    def customer(self):
        self.root.withdraw()
        customerWindow(tk.Toplevel(self.root), self.root)

    def closeWindow(self):  # destroys Order window, opens main menu
        self.root.destroy()
        config.app.enableMenu()

    def search(self):
        # Retrieves the search value and search field from the inputs
        # Adds a wildcard symbol, %, to the end of the search value
        search = '%' + str(self.searchVar.get().strip().upper()) + '%'
        searchFieldVar = self.searchFieldVar.get()
        if searchFieldVar == 'OrderNo':
            searchField = 'orderNo'
        elif searchFieldVar == 'CustomerID':
            searchField = 'customerID'
        elif searchFieldVar == 'OrderTotal':
            searchField = 'orderTotal'
        elif searchFieldVar == 'Date':
            searchField = 'date'
        elif searchFieldVar == 'StaffID':
            searchField = 'staffID'
        # Clears the treeview of all other records
        self.tree.delete(*self.tree.get_children())
        # Selects records from orderTbl where the search field matches the search value
        records = executeSQL(
            'SELECT * FROM orderTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records found into the treeview
            self.tree.insert('', 0, values=(i[0], i[1], i[2], i[3], i[4]))

    def addOrder(self):
        # count used for how many items are added to order
        self.itemIDs = []
        self.count = 0
        self.total = 0
        disableWindow(self.reportButton, self.returnButton, self.addOrderButton, self.editOrderButton,
                      self.delOrderButton)
        # Selects all customerIDs, forenames and surnames, and saves them to a list
        customers = executeSQL(
            'SELECT customerID,customerForename,customerSurname FROM customerTbl', (), True)
        customerIDs = [(item[0:3]) for item in customers]
        self.orderWin = tk.Toplevel(self.root)
        self.orderWin.lift(self.root)
        self.orderWin.title('Add Order')
        self.orderWin.iconbitmap(config.icon)
        self.orderWin.protocol('WM_DELETE_WINDOW',
                               lambda: (enableWindow(self.orderWin, self.reportButton, self.returnButton,
                                                     self.addOrderButton, self.editOrderButton, self.delOrderButton),
                                        accesslevel(
                                            2, self.addOrderButton, self.editOrderButton),
                                        accesslevel(3, self.delOrderButton)))
        self.addOrderFrame = tk.Frame(self.orderWin)
        self.addOrderFrame.pack(side=tk.LEFT, fill='y')
        # Creates all the labels and entry boxes for each field
        self.detailLabel = tk.Label(
            self.addOrderFrame, text='Enter Order Details:', font='none 11 bold')
        self.customerIDLabel = tk.Label(
            self.addOrderFrame, text='CustomerID:', font='none 11')
        # Creates a dropdown menu populated with all the customerIDs that we retrieved earlier
        self.customerIDVar = tk.StringVar()
        if customerIDs:
            self.customerIDDropdown = ttk.OptionMenu(self.addOrderFrame, self.customerIDVar, 'Anonymous', *customerIDs,
                                                     command=lambda x: (
                                                         self.customerIDVar.set(self.customerIDVar.get()[2:9])))
        else:
            self.customerIDDropdown = tk.Label(
                self.addOrderFrame, textvariable=self.customerIDVar, font='none 11')
        # self.customerIDVar.set('Anonymous')
        self.dateLabel = tk.Label(
            self.addOrderFrame, text='Date:', font='none 11')
        self.dateVar = tk.StringVar()
        # Creates a calendar widget to pick the date from
        self.calendar = DateEntry(self.addOrderFrame, state='readonly',
                                  date_pattern='DD/MM/YYYY', textvariable=self.dateVar,
                                  showweeknumbers=False, maxdate=datetime.today())

        # Creates canvas to put all items on
        self.canvas = tk.Canvas(self.addOrderFrame)
        self.allItemsFrame = tk.Frame(self.canvas)
        # Creates scrollbar for canvas
        self.canvasScroll = ttk.Scrollbar(
            self.addOrderFrame, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(
            yscrollcommand=self.canvasScroll.set, width=200, height=150)
        self.canvas.grid(row=3, column=0, columnspan=2, sticky='ns')
        self.canvasScroll.grid(row=3, column=3, sticky='ns')
        self.canvas.create_window(
            (0, 0), window=self.allItemsFrame, anchor='nw')
        self.allItemsFrame.bind('<Configure>', lambda x: self.canvas.configure(
            scrollregion=self.canvas.bbox('all')))

        self.addOrderFrame.columnconfigure(0, weight=1)  # column with canvas
        self.addOrderFrame.rowconfigure(3, weight=1)  # row with canvas

        self.totalVar = tk.StringVar()
        self.totalVar.set('Total: £0.00')
        self.totalLabel = tk.Label(
            self.addOrderFrame, textvariable=self.totalVar, font='none 11 bold')
        # Creates text variable and error label to output any errors
        self.errorVar = tk.StringVar()
        self.errorLabel = tk.Label(
            self.addOrderFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
        # Creates save button, which calls the function saveOrder when pressed
        self.saveButton = ttk.Button(self.addOrderFrame, text='Save New Order',
                                     command=lambda: self.saveOrder())
        # Grids all the labels, entry boxes, buttons and dropdowns to the frame
        self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
        self.customerIDLabel.grid(row=1, column=0, sticky='e', padx=(10, 0))
        self.customerIDDropdown.grid(
            row=1, column=1, padx=(0, 10), sticky='ew')
        self.dateLabel.grid(row=2, column=0, sticky='e', padx=(10, 0))
        self.calendar.grid(row=2, column=1, padx=(0, 10), sticky='ew')
        self.totalLabel.grid(row=4, column=0, columnspan=2)
        self.errorLabel.grid(row=5, column=0, columnspan=2)
        self.saveButton.grid(row=6, column=0, columnspan=2, pady=(0, 10))
        # Runs the save function when the user presses the 'enter' button (same as saveButton)
        self.orderWin.bind('<Return>', lambda event: self.saveOrder())

        self.seperator = ttk.Separator(self.orderWin, orient='vertical')
        self.seperator.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        self.addItemFrame = tk.Frame(self.orderWin)
        self.addItemFrame.pack(side=tk.LEFT, fill='both', expand=True)
        self.label = tk.Label(
            self.addItemFrame, text='Double click on an item to add it to the order')
        # Creates the treeview, defining each column and naming its heading with the relevant field name
        columns = ('ItemID', 'ItemName', 'SalePrice', 'Quantity')
        self.itemTree = ttk.Treeview(
            self.addItemFrame, columns=columns, show='headings')
        for col in columns:
            self.itemTree.column(col, width=100, minwidth=100)
            self.itemTree.heading(col, text=col)
        self.itemTree.grid(row=1, column=0, sticky='nesw',
                           padx=(10, 0), pady=(10, 0))

        self.addItemFrame.columnconfigure(0, weight=1)  # column with treeview
        self.addItemFrame.rowconfigure(1, weight=1)  # row with treeview

        # Creates vertical and horizontal scrollbars, linking them to the treeview
        self.scrollbar = ttk.Scrollbar(
            self.addItemFrame, orient='vertical', command=self.itemTree.yview)
        self.scrollbar.grid(row=1, column=1, sticky='ns',
                            pady=10, padx=(0, 10))
        self.itemTree.configure(
            yscrollcommand=self.scrollbar.set, selectmode='browse')
        self.xscrollbar = ttk.Scrollbar(
            self.addItemFrame, orient='horizontal', command=self.itemTree.xview)
        self.xscrollbar.grid(row=2, column=0, sticky='ew')
        self.itemTree.configure(
            xscrollcommand=self.xscrollbar.set, selectmode='browse')
        self.itemTree.bind('<Double-1>', lambda x: self.addItemToOrder())
        self.addedVar = tk.StringVar()
        self.addedLabel = tk.Label(
            self.addItemFrame, textvariable=self.addedVar, font='none 11 bold')
        self.addedLabel.grid(row=3, column=0, sticky='s', pady=(0, 10))
        self.label.grid(row=0, column=0, sticky='n', pady=(10, 0))

        loadDatabase(self.itemTree, 'itemTbl', False)

        center(self.orderWin)

    def addItemToOrder(self):
        if self.itemTree.selection():
            # Retrieves all item details from the treeview
            item = self.itemTree.selection()
            itemID = self.itemTree.set(item, '#1')
            itemName = self.itemTree.set(item, '#2')
            salePrice = float(self.itemTree.set(item, '#3'))
            quantity = int(self.itemTree.set(item, '#4'))
            # Checks if item is in stock and outputs relevant message
            if quantity <= 0:
                self.addedLabel.config(fg='red')
                self.addedVar.set(itemName + ' Not In Stock')
                return
            # Count is used to grid labels without any overlapping
            self.count += 1
            # Adds item to list of all items in order
            self.itemIDs.append([itemID, itemName])
            # Decrements quantity in treeview
            newQuantity = quantity - 1
            self.itemTree.set(item, column=3, value=newQuantity)
            # Creates labels/buttons (to remove the item) and grids them to the frame with all other items in order
            itemNameLabel = tk.Label(self.allItemsFrame, text=(
                itemID + ' ' + itemName), font='none 11', wraplength=125)
            priceLabel = tk.Label(self.allItemsFrame, text=(
                str('£{:.2f}'.format(salePrice))), font='none 11')
            removeItemLabel = tk.Label(
                self.allItemsFrame, text='x', fg='red', cursor='hand2')
            removeItemLabel.bind('<Button-1>',
                                 lambda x: self.removeItem(item, itemID, itemName, itemNameLabel, priceLabel,
                                                           removeItemLabel, salePrice))
            itemNameLabel.grid(row=self.count, column=0,
                               sticky='W', padx=(10, 0))
            priceLabel.grid(row=self.count, column=1, sticky='E')
            removeItemLabel.grid(row=self.count, column=2,
                                 sticky='E', padx=(0, 10))
            # Alters the total price to reflect the added item
            self.total += salePrice
            self.totalVar.set(str('Total: £{:.2f}'.format(self.total)))
            # Outputs message confirming addition of item
            self.addedLabel.config(fg='green')
            self.addedVar.set(itemName + ' Added to Order')

    def removeItem(self, item, itemID, itemName, itemNameLabel, priceLabel, removeItemLabel, salePrice):
        # Ungrids all labels/buttons related to that item from the frame
        itemNameLabel.grid_remove()
        priceLabel.grid_remove()
        removeItemLabel.grid_remove()
        quantity = int(self.itemTree.set(item, '#4'))
        # Alters the total price to reflect the removed item
        self.total -= salePrice
        self.totalVar.set(str('Total: £{:.2f}'.format(self.total)))
        # Increments the item quantity in the item treeview
        self.itemTree.set(item, column=3, value=(quantity + 1))
        # Removes the item from the list of items
        self.itemIDs.remove([itemID, itemName])
        # Outputs message confirming removal of item
        self.addedLabel.config(fg='red')
        self.addedVar.set(itemName + ' Removed from Order')

    def saveOrder(self):
        if self.itemIDs:
            customerID = self.customerIDVar.get()
            date = self.dateVar.get()

            itemNames = [self.itemIDs[x][1] for x in range(len(self.itemIDs))]
            # Generates a random orderID, using the random module
            orderNo = 'ON' + \
                str(''.join(['%s' % random.randint(0, 9)
                    for num in range(0, 5)]))
            # Comfirmation box asks user to confirm that inputs are all correct
            if tk.messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nOrderNo:\t' +
                                      orderNo + '\nCustomerID:\t' + customerID + '\nDate:\t\t' +
                                      date + '\nStaffID\t\t' + config.userID + '\nItems:\t\t' +
                                      '\n\t\t'.join(itemNames) +
                                      '\nTotal:\t\t£' + str('{:.2f}'.format(self.total))):
                try:
                    itemSaved = []
                    # Insert record into orderTbl
                    executeSQL('INSERT INTO orderTbl VALUES (?,?,?,?,?)',
                               (orderNo, customerID, '{:.2f}'.format(self.total), date, config.userID), False)
                    for item in self.itemIDs:
                        oldQuantity = executeSQL(
                            'SELECT quantity FROM itemTbl WHERE itemID = ?', (item[0],), False)[0]
                        executeSQL('UPDATE itemTbl SET quantity = ? WHERE itemID = ?', (oldQuantity - 1, item[0]),
                                   False)
                        if item[0] not in itemSaved:
                            executeSQL(
                                'INSERT INTO orderItemTbl VALUES (?,?,?)', (orderNo, item[0], 1), False)
                            itemSaved.append(item[0])
                        else:
                            lastQuantity = \
                                executeSQL('SELECT quantity FROM orderItemTbl WHERE itemID = ? AND orderNo = ?',
                                           (item[0], orderNo), False)[0]
                            executeSQL('UPDATE orderItemTbl SET quantity = ? WHERE itemID = ? AND orderNo = ?',
                                       (lastQuantity + 1, item[0], orderNo), False)
                    # Reloads records into treeview
                    loadDatabase(self.tree, 'orderTbl', False)
                    # Destroys add order window and returns to view orders window
                    enableWindow(self.orderWin, self.reportButton, self.returnButton, self.addOrderButton,
                                 self.editOrderButton, self.delOrderButton)
                    accesslevel(2, self.addOrderButton, self.editOrderButton)
                    accesslevel(3, self.delOrderButton)
                    tk.messagebox.showinfo('Success!', 'New Order Saved')
                except sqlite3.IntegrityError:
                    # Outputs error if orderID is not unique
                    self.errorVar.set(
                        'Error: Failed To Update Database.\nPlease Try Again')
        else:
            # Outputs error if not all fields are filled
            self.errorVar.set('Error: No Items in Order')

    def editOrder(self):
        if self.tree.selection():  # Runs IF a record is selected from treeview
            disableWindow(self.reportButton, self.returnButton, self.addOrderButton, self.editOrderButton,
                          self.delOrderButton)
            for selected_item in self.tree.selection():
                # Finds records from orderTbl that match the selected record
                orders = executeSQL('SELECT * FROM orderTbl WHERE orderNo=?', (self.tree.set(selected_item, '#1'),),
                                    False)
                orderNo = orders[0]
                customerID = orders[1]
                self.total = orders[2]
                date = orders[3]
            # Selects all customerIDs, forenames and surnames, and saves them to a list
            customers = executeSQL(
                'SELECT customerID,customerForename,customerSurname FROM customerTbl', (), True)
            customerIDs = [(item[0:3]) for item in customers]
            self.orderWin = tk.Toplevel(self.root)
            self.orderWin.title('Edit Order')
            self.orderWin.iconbitmap(config.icon)
            self.orderWin.protocol('WM_DELETE_WINDOW',
                                   lambda: (enableWindow(self.orderWin, self.reportButton, self.returnButton,
                                                         self.addOrderButton, self.editOrderButton,
                                                         self.delOrderButton),
                                            accesslevel(
                                                2, self.addOrderButton, self.editOrderButton),
                                            accesslevel(3, self.delOrderButton)))
            self.editOrderFrame = tk.Frame(self.orderWin)
            self.editOrderFrame.pack(side=tk.LEFT, fill='y')
            # Creates all the labels and entry boxes for each field
            self.detailLabel = tk.Label(
                self.editOrderFrame, text='Edit Order Details:', font='none 11 bold')
            self.customerIDLabel = tk.Label(
                self.editOrderFrame, text='CustomerID:', font='none 11')
            # Creates a dropdown menu populated with all the customerIDs that we retrieved earlier
            self.customerIDVar = tk.StringVar()
            if customerIDs:
                self.customerIDDropdown = ttk.OptionMenu(self.editOrderFrame, self.customerIDVar, customerID,
                                                         *customerIDs,
                                                         command=lambda x: (
                                                             self.customerIDVar.set(self.customerIDVar.get()[2:9])))
            else:
                self.customerIDDropdown = tk.Label(
                    self.editOrderFrame, textvariable=self.customerIDVar, font='none 11')
            self.customerIDVar.set(customerID)
            self.dateLabel = tk.Label(self.editOrderFrame,
                                      text='Date:', font='none 11')
            self.dateVar = tk.StringVar()
            # Creates a calendar widget to pick the date from
            self.calendar = DateEntry(self.editOrderFrame, state='readonly',
                                      date_pattern='DD/MM/YYYY', textvariable=self.dateVar,
                                      showweeknumbers=False, maxdate=datetime.today())
            self.dateVar.set(date)

            self.canvas = tk.Canvas(self.editOrderFrame)
            self.allItemsFrame = tk.Frame(self.canvas)
            self.canvasScrolly = ttk.Scrollbar(
                self.editOrderFrame, orient='vertical', command=self.canvas.yview)
            self.canvas.configure(
                yscrollcommand=self.canvasScrolly.set, width=200, height=150)
            self.canvas.grid(row=3, column=0, columnspan=2, sticky='ns')
            self.canvasScrolly.grid(row=3, column=3, sticky='ns')
            self.canvas.create_window(
                (0, 0), window=self.allItemsFrame, anchor='nw')
            self.allItemsFrame.bind('<Configure>',
                                    lambda x: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

            self.editOrderFrame.columnconfigure(
                0, weight=1)  # column with canvas
            self.editOrderFrame.rowconfigure(3, weight=1)  # row with canvas

            self.totalVar = tk.StringVar()
            self.totalVar.set(str('Total: £{:.2f}'.format(self.total)))
            self.totalLabel = tk.Label(
                self.editOrderFrame, textvariable=self.totalVar, font='none 11 bold')
            # Creates text variable and error label to output any errors
            self.errorVar = tk.StringVar()
            self.errorLabel = tk.Label(
                self.editOrderFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
            # Creates save button, which calls the function saveOrder when pressed
            self.saveButton = ttk.Button(self.editOrderFrame, text='Update Order',
                                         command=lambda: self.saveEditOrder(orderNo))
            # Grids all the labels, entry boxes, buttons and dropdowns to the frame
            self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
            self.customerIDLabel.grid(
                row=1, column=0, sticky='e', padx=(10, 0))
            self.customerIDDropdown.grid(
                row=1, column=1, padx=(0, 10), sticky='ew')
            self.dateLabel.grid(row=2, column=0, sticky='e', padx=(10, 0))
            self.calendar.grid(row=2, column=1, padx=(0, 10), sticky='ew')
            self.totalLabel.grid(row=4, column=0, columnspan=2)
            self.errorLabel.grid(row=5, column=0, columnspan=2)
            self.saveButton.grid(row=6, column=0, columnspan=2, pady=(0, 10))
            # Runs the save function when the user presses the 'enter' button (same as saveButton)
            self.orderWin.bind(
                '<Return>', lambda event: self.saveEditOrder(orderNo))

            self.seperator = ttk.Separator(self.orderWin, orient='vertical')
            self.seperator.pack(side=tk.LEFT, fill=tk.Y, padx=10)

            self.addItemFrame = tk.Frame(self.orderWin)
            self.addItemFrame.pack(side=tk.LEFT, fill='both', expand=True)
            self.label = tk.Label(
                self.addItemFrame, text='Double click on an item to add it to the order')
            # Creates the treeview, defining each column and naming its heading with the relevant field name
            columns = ('ItemID', 'ItemName', 'SalePrice', 'Quantity')
            self.itemTree = ttk.Treeview(
                self.addItemFrame, columns=columns, show='headings')
            for col in columns:
                self.itemTree.column(col, width=100, minwidth=100)
                self.itemTree.heading(col, text=col)
            self.itemTree.grid(row=1, column=0, sticky='nesw',
                               padx=(10, 0), pady=(10, 0))

            self.addItemFrame.columnconfigure(
                0, weight=1)  # column with treeview
            self.addItemFrame.rowconfigure(1, weight=1)  # row with treeview

            # Creates vertical and horizontal scrollbars, linking them to the treeview
            self.scrollbar = ttk.Scrollbar(
                self.addItemFrame, orient='vertical', command=self.itemTree.yview)
            self.scrollbar.grid(row=1, column=1, sticky='ns',
                                pady=10, padx=(0, 10))
            self.itemTree.configure(
                yscrollcommand=self.scrollbar.set, selectmode='browse')
            self.xscrollbar = ttk.Scrollbar(
                self.addItemFrame, orient='horizontal', command=self.itemTree.xview)
            self.xscrollbar.grid(row=2, column=0, sticky='ew')
            self.itemTree.configure(
                xscrollcommand=self.xscrollbar.set, selectmode='browse')
            self.itemTree.bind('<Double-1>', lambda x: self.addItemToOrder())
            self.addedVar = tk.StringVar()
            self.addedLabel = tk.Label(
                self.addItemFrame, textvariable=self.addedVar, font='none 11 bold')
            self.addedLabel.grid(row=3, column=0, sticky='s', pady=(0, 10))
            self.label.grid(row=0, column=0, sticky='n', pady=(10, 0))

            loadDatabase(self.itemTree, 'itemTbl', False)

            center(self.orderWin)

            itemIDQuantity = executeSQL(
                'SELECT itemID,quantity FROM orderItemTbl WHERE orderNo = ?', (orderNo,), True)
            self.count = 0
            self.itemIDs = []
            for item in itemIDQuantity:
                items = executeSQL(
                    'SELECT * FROM itemTbl WHERE itemID = ?', (item[0],), False)
                for x in range(item[1]):
                    listOfEntriesInTreeView = self.itemTree.get_children()
                    for row in listOfEntriesInTreeView:
                        if self.itemTree.set(row, '#1') == items[0]:
                            selected = row

                    self.addOldItemsToOrder(items, selected)
            self.originalItems = list(self.itemIDs)

        else:
            # Outputs error message is no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')

    def addOldItemsToOrder(self, items, item):
        # Goes through all items in original order, adding them to the list of all items and prices in the order,
        # as well as creating labels and buttons to remove it from the order
        itemID = items[0]
        itemName = items[1]
        salePrice = items[2]
        self.count += 1
        self.itemIDs.append([itemID, itemName])

        itemNameLabel = tk.Label(self.allItemsFrame, text=(
            itemID + ' ' + itemName), font='none 11', wraplength=125)
        priceLabel = tk.Label(self.allItemsFrame, text=(
            str('£{:.2f}'.format(salePrice))), font='none 11')
        removeItemLabel = tk.Label(
            self.allItemsFrame, text='x', fg='red', cursor='hand2')
        removeItemLabel.bind('<Button-1>', lambda x: self.removeItem(item, itemID, itemName, itemNameLabel, priceLabel,
                                                                     removeItemLabel, salePrice))
        itemNameLabel.grid(row=self.count, column=0, sticky='W', padx=(10, 0))
        priceLabel.grid(row=self.count, column=1, sticky='E')
        removeItemLabel.grid(row=self.count, column=2,
                             sticky='E', padx=(0, 10))

    def saveEditOrder(self, orderNo):
        # Creates a list of all the new items in the order
        temp = list(self.originalItems)
        newItems = []
        for x in self.itemIDs:
            if x not in temp:
                newItems.append(x)
            else:
                temp.remove(x)

        # Creates a list of all items removed from the order
        temp = list(self.itemIDs)
        removedItems = []
        for x in self.originalItems:
            if x not in temp:
                removedItems.append(x)
            else:
                temp.remove(x)

        if self.itemIDs:
            customerID = self.customerIDVar.get()
            date = self.dateVar.get()

            itemNames = [self.itemIDs[x][1] for x in range(len(self.itemIDs))]
            # Comfirmation box asks user to confirm that inputs are all correct
            if tk.messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nOrderNo:\t' +
                                      orderNo + '\nCustomerID:\t' + customerID + '\nDate:\t\t' +
                                      date + '\nStaffID\t\t' + config.userID + '\nItems:\t\t' +
                                      '\n\t\t'.join(itemNames) +
                                      '\nTotal:\t\t£' + str('{:.2f}'.format(self.total))):
                try:
                    # Update record in orderTbl
                    executeSQL('UPDATE orderTbl SET customerID = ?, orderTotal = ?, date = ? WHERE orderNo = ?',
                               (customerID, '{:.2f}'.format(self.total), date, orderNo), False)
                    executeSQL(
                        'DELETE FROM orderItemTbl WHERE orderNo=?', (orderNo,), False)
                    for item in removedItems:
                        oldQuantity = executeSQL(
                            'SELECT quantity FROM itemTbl WHERE itemID = ?', (item[0],), False)[0]
                        executeSQL('UPDATE itemTbl SET quantity = ? WHERE itemID = ?', (oldQuantity + 1, item[0]),
                                   False)
                    for item in newItems:
                        oldQuantity = executeSQL(
                            'SELECT quantity FROM itemTbl WHERE itemID = ?', (item[0],), False)[0]
                        executeSQL('UPDATE itemTbl SET quantity = ? WHERE itemID = ?', (oldQuantity - 1, item[0]),
                                   False)
                    itemSaved = []
                    for item in self.itemIDs:
                        if item[0] not in itemSaved:
                            executeSQL(
                                'INSERT INTO orderItemTbl VALUES (?,?,?)', (orderNo, item[0], 1), False)
                            itemSaved.append(item[0])
                        else:
                            oldQuantity = \
                                executeSQL('SELECT quantity FROM orderItemTbl WHERE itemID = ? AND orderNo = ?',
                                           (item[0], orderNo), False)[0]
                            executeSQL('UPDATE orderItemTbl SET quantity = ? WHERE itemID = ? AND orderNo = ?',
                                       (oldQuantity + 1, item[0], orderNo), False)
                    # Reloads records into treeview
                    loadDatabase(self.tree, 'orderTbl', False)
                    # Destroys edit order window and returns to view orders window
                    enableWindow(self.orderWin, self.reportButton, self.returnButton, self.addOrderButton,
                                 self.editOrderButton, self.delOrderButton)
                    accesslevel(2, self.addOrderButton, self.editOrderButton)
                    accesslevel(3, self.delOrderButton)
                    tk.messagebox.showinfo('Success!', 'Order Updated')
                except sqlite3.IntegrityError:
                    # Outputs error if orderID is not unique
                    self.errorVar.set(
                        'Error: Failed To Update Database.\nPlease Try Again')
        else:
            # Outputs error if not all fields are filled
            self.errorVar.set('Error: No Items in Order')

    def delOrder(self):
        if self.tree.selection():
            # Retrieves the orderID from the record selected in the treeview
            for selected_item in self.tree.selection():
                orderNo = self.tree.set(selected_item, '#1')
            # Asks the user for confimation that they want to permanently delete this record
            if tk.messagebox.askokcancel('Delete', '''Are you sure you want to permanently delete this record?
                                        \nNote: This will increase the quantity of items in stock'''):
                for selected_item in self.tree.selection():
                    # Removes the record from orderTbl
                    executeSQL('DELETE FROM orderTbl WHERE orderNo=?',
                               (orderNo,), False)
                    items = executeSQL(
                        'SELECT itemID,quantity FROM orderItemTbl WHERE orderNo = ?', (orderNo,), True)
                    for item in items:
                        oldQuantity = executeSQL(
                            'SELECT quantity FROM itemTbl WHERE itemID = ?', (item[0],), False)[0]
                        executeSQL('UPDATE itemTbl SET quantity = ? WHERE itemID = ?', (oldQuantity + item[1], item[0]),
                                   False)
                    executeSQL(
                        'DELETE FROM orderItemTbl WHERE orderNo=?', (orderNo,), False)
                    # Removes the record from the treeview
                    self.tree.delete(selected_item)
        else:
            # Outputs error message is no record has been selected
            tk.messagebox.showerror('Error', 'No Record Selected')

    def report(self):
        disableWindow(self.reportButton, self.returnButton, self.addOrderButton, self.editOrderButton,
                      self.delOrderButton)
        self.orderWin = tk.Toplevel(self.root)
        self.orderWin.title('Order Report')
        self.orderWin.iconbitmap(config.icon)
        self.orderWin.protocol('WM_DELETE_WINDOW',
                               lambda: (enableWindow(self.orderWin, self.reportButton, self.returnButton,
                                                     self.addOrderButton, self.editOrderButton, self.delOrderButton),
                                        accesslevel(
                                            2, self.addOrderButton, self.editOrderButton),
                                        accesslevel(3, self.delOrderButton)))
        self.orderReportFrame = tk.Frame(self.orderWin)
        self.orderReportFrame.pack()
        # Creates labels and entry boxes for start/end date of report
        self.detailLabel = tk.Label(
            self.orderReportFrame, text='Enter Report Parameters', font='none 11 bold')
        self.startDateLabel = tk.Label(
            self.orderReportFrame, text='Start Date:', font='none 11')
        self.startDateVar = tk.StringVar()
        self.startCalendar = DateEntry(self.orderReportFrame, state='readonly',
                                       date_pattern='DD/MM/YYYY', textvariable=self.startDateVar,
                                       showweeknumbers=False, maxdate=datetime.today())
        self.endDateLabel = tk.Label(
            self.orderReportFrame, text='End Date:', font='none 11')
        self.endDateVar = tk.StringVar()
        self.endCalendar = DateEntry(self.orderReportFrame, state='readonly',
                                     date_pattern='DD/MM/YYYY', textvariable=self.endDateVar,
                                     showweeknumbers=False, maxdate=datetime.today())
        # Creates a text variable and error label to output any errors to
        self.errorVar = tk.StringVar()
        self.errorLabel = tk.Label(
            self.orderReportFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
        # Creates a button which runs the generateReport function when pressed
        self.enterButton = ttk.Button(self.orderReportFrame, text='Generate Report',
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
        self.orderWin.bind('<Return>', lambda event: self.generateReport())

        center(self.orderWin)

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
            self.orderReportWin = tk.Toplevel(self.orderWin)
            self.orderReportWin.title('Revenue Report')
            self.orderReportWin.iconbitmap(config.icon)
            self.orderReportFrame = tk.Frame(self.orderReportWin)
            self.orderReportFrame.pack(fill='both', expand=True)
            self.orderReportWin.protocol('WM_DELETE_WINDOW',
                                         lambda: enableWindow(self.orderReportWin, self.enterButton))
            self.titleLabel = tk.Label(self.orderReportFrame, text='Kingfisher Trust', font='algerian 14 bold',
                                       fg='#2380b7')
            self.detailLabel = tk.Label(
                self.orderReportFrame, text='Revenue Report', font='none 12 bold')
            # Creates a label detailing the date constraints of the report, as input by the user
            self.datesLabel = tk.Label(self.orderReportFrame, text='From ' + str(datetime.isoformat(self.startDate)[:10])
                                       + ' to ' + str(
                datetime.isoformat(self.endDate)[:10]) + ':')
            # Creates a button allowing the user to save the report as a PDF file
            self.pdfButton = ttk.Button(self.orderReportFrame, text='Save to PDF',
                                        command=lambda: (disableWindow(self.pdfButton),
                                                         orderReport(self.startDate, self.endDate, records,
                                                                     self.totalCost, self.totalRevenue,
                                                                     self.totalProfit)))
            # Grids the above labels and buttons
            self.titleLabel.grid(row=0, column=0, columnspan=3, pady=10)
            self.detailLabel.grid(row=1, column=0, columnspan=3)
            self.datesLabel.grid(row=2, column=0, padx=10, sticky='w')
            self.pdfButton.grid(row=2, column=2, padx=10, sticky='E')
            # Creates a treeview to insert all the relevant order records
            columns = ('OrderID', 'CustomerID', 'Date', 'ItemID', 'ItemName', 'Quantity', 'SalePrice', 'SupplierCost',
                       'SupplierID')
            self.reporttree = ttk.Treeview(
                self.orderReportFrame, columns=columns, show='headings', selectmode='none')
            for col in columns:
                self.reporttree.column(col, width=100, minwidth=100)
                self.reporttree.heading(col, text=col)
            self.reporttree.grid(row=6, column=0, sticky='nesw',
                                 columnspan=3, padx=(10, 0), pady=10)
            self.orderReportFrame.columnconfigure(
                [0, 1, 2], weight=1)  # column with treeview
            self.orderReportFrame.rowconfigure(
                6, weight=1)  # row with treeview
            # Connects to database and selects all records from orderTbl
            self.orders = executeSQL('SELECT * FROM orderTbl', (), True)
            self.totalCost = 0
            self.totalRevenue = 0
            records = []
            # Iterates through all the orders, selecting all relevant fields for orders within the
            # given time period
            for order in self.orders:
                count = 0
                orderItems = executeSQL(
                    'SELECT * FROM orderItemTbl WHERE orderNo = ?', (order[0],), True)
                date = order[3]
                if self.startDate <= datetime.strptime(date, '%d/%m/%Y') <= self.endDate:
                    for orderItem in orderItems:
                        items = executeSQL(
                            'SELECT * FROM itemTbl WHERE itemID = ?', (orderItem[1],), False)

                        orderNo = order[0]
                        customerID = order[1]
                        itemID = items[0]
                        itemName = items[1]
                        quantity = int(orderItem[2])
                        salePrice = float(items[2]) * quantity
                        supplierCost = float(items[4]) * quantity
                        supplierID = items[5]

                        self.totalCost += supplierCost
                        self.totalRevenue += salePrice

                        # Inserts all record items into treeview, grouping such that only the top record shows the
                        # order number and other repeated values
                        if count == len(orderItems) - 1:
                            record = (orderNo, customerID, date, itemID, itemName, quantity,
                                      str('£{:.2f}'.format(salePrice)), str('£{:.2f}'.format(supplierCost)), supplierID)
                            records.append(record)
                            self.reporttree.insert('', 0, values=record)
                        else:
                            record = ('', '', '', itemID, itemName, quantity,
                                      str('£{:.2f}'.format(salePrice)), str('£{:.2f}'.format(supplierCost)), supplierID)
                            records.append(record)
                            self.reporttree.insert('', 0, values=record)

                        count += 1

            self.totalProfit = self.totalRevenue - self.totalCost

            self.scrollbar = ttk.Scrollbar(
                self.orderReportFrame, orient='vertical', command=self.reporttree.yview)
            self.scrollbar.grid(row=6, column=3, sticky='ns',
                                pady=10, padx=(0, 10))
            self.reporttree.configure(
                yscrollcommand=self.scrollbar.set, selectmode='browse')

            self.totalCostLabel = tk.Label(self.orderReportFrame, text=str(
                'Total Cost = £{:.2f}'.format(self.totalCost)))
            self.totalRevenueLabel = tk.Label(self.orderReportFrame,
                                              text=str('Total Revenue = £{:.2f}'.format(self.totalRevenue)))
            self.totalProfitLabel = tk.Label(self.orderReportFrame,
                                             text=str('Total Profit = £{:.2f}'.format(self.totalProfit)))
            self.totalCostLabel.grid(row=3, column=0, padx=10, sticky='w')
            self.totalRevenueLabel.grid(row=4, column=0, padx=10, sticky='w')
            self.totalProfitLabel.grid(row=5, column=0, padx=10, sticky='w')

            center(self.orderReportWin)

        except ValueError:
            # Outputs an error if the dates input are invalid
            self.errorVar.set('Error: Invalid Input\nDD/MM/YYYY')
