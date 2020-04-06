# Python 3.8.1
# Requires prettytable, fpdf, tkcalendar, bcrypt to be installed

import random
from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry

# Importing the custom made reporting module for creating PDFs
from report import *
# Importing the custom made sql module
from sql import *
# Importing the custom made validation module
from validation import *

icon = 'logo.ico'


# Centres the window
def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry('+{}+{}'.format(x, y))

    # Sets min size to default size (i.e. when all widgets fit on window)
    win.minsize(width, height)


# Creates tooltips
class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        """Display text in tooltip window"""
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox('insert')
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry('+%d+%d' % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background='#ffffe0', relief=SOLID, borderwidth=1,
                      font=('tahoma', '8', 'normal'))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


# Checks access level and disables relevant buttons
# And displays a tooltip message where necessary.
def accesslevel(required, *buttons):
    if accessLevel < required:
        for i in buttons:
            toolTip = ToolTip(i)
            i['state'] = 'disabled'
            i.bind('<Enter>', lambda x: toolTip.showtip('Insufficient Access Level'))
            i.bind('<Leave>', lambda x: toolTip.hidetip())


# Sets the state of all buttons passed to 'disabled'
def disableWindow(*args):
    for i in args:
        i['state'] = 'disabled'


# Destroys the toplevel window that the function is called from,
# And resets the state of all buttons passed to 'normal'
def enableWindow(win, *args):
    win.destroy()
    for i in args:
        i['state'] = 'normal'


# Sorts the specified treeview by the selected column,
# Ensuring each item is sorted as the correct data type.
def treeview_sort_column(tv, col, reverse):
    l = []
    for k in tv.get_children(''):

        try:
            elem = (datetime.strptime(tv.set(k, col), '%d/%m/%Y').timestamp(), k)
        except ValueError:
            try:
                elem = (float(tv.set(k, col)), k)
            except:
                elem = (tv.set(k, col), k)

        l.append(elem)

    # Tries to sort the list, reversed if the second time
    try:
        l.sort(reverse=reverse)
    # Converts to strings and sorts alphanumerically if error is raised
    except:
        j = []
        for i in l:
            elem = (str(i[0]), i[1])
            j.append(elem)

        l = j
        l.sort(reverse=reverse)

    # Rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    # Sets the command for the column to reverse the sort when clicked
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))


########################################### LOGIN WINDOW ###########################################
    
class loginWin:
    # Creates login window
    def __init__(self, root):
        self.authenticated = False
        self.root = root
        self.root.title('Login')
        self.root.iconbitmap(icon)
        self.frame = Frame(root)
        self.frame.pack(expand=True)
        # Creates a label with ‘Kingfisher Trust’ in bold, blue text with ‘Algerian’ font – the same text
        # as is used on their website, to maintain brand consistency.
        self.titleLabel = Label(self.frame, text='Kingfisher Trust', font='algerian 18 bold', fg='#2380b7')
        # Creates the username and password labels and entry boxes, as well as defining variables for the
        # inputted data
        self.usernameLabel = Label(self.frame, text='Username:', font='none 11')
        self.usernameVar = StringVar()
        self.usernameBox = ttk.Entry(self.frame, textvariable=self.usernameVar)
        self.passwordLabel = Label(self.frame, text='Password:', font='none 11')
        self.passwordVar = StringVar()
        # Password will only show *s when data is input, to protect the user’s password
        # from falling victim to shoulder surfing.
        self.passwordBox = ttk.Entry(self.frame, show='•', textvariable=self.passwordVar)
        self.forgotPass = Label(self.frame, text='Forgotten Password?', fg='blue', cursor='hand2')
        # Defines a text variable and creates a label so that errors can be shown
        # This is initially blank, and the variable can be set to display any suitable message
        self.errorVar = StringVar()
        self.errorLabel = Label(self.frame, textvariable=self.errorVar, font='none 11 bold', fg='red')
        # Creates the exit and login buttons, and calls the functions when the buttons are clicked
        self.exitButton = ttk.Button(self.frame, text='Exit', command=lambda: self.closeWindow())
        self.loginButton = ttk.Button(self.frame, text='Login', command=lambda: self.login())
        # Grids all the labels, boxes and buttons that we have created to the frame
        self.titleLabel.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.usernameLabel.grid(row=1, column=0, sticky='e')
        self.usernameBox.grid(row=1, column=1, pady=10, padx=(0, 10))
        self.passwordLabel.grid(row=2, column=0, sticky='e')
        self.passwordBox.grid(row=2, column=1, pady=10, padx=(0, 10))
        self.forgotPass.grid(row=3, column=0, columnspan=2)
        self.forgotPass.bind('<Button-1>', lambda x: self.forgotPassword())
        self.errorLabel.grid(row=4, column=0, columnspan=2)
        self.exitButton.grid(row=5, column=0, pady=(0, 25), padx=10, ipadx=10, ipady=2, sticky='news')
        self.loginButton.grid(row=5, column=1, pady=(0, 25), padx=10, ipadx=10, ipady=2, sticky='news')
        # Runs the login function when the user presses the 'enter' button (same as loginButton)
        self.root.bind('<Return>', lambda event: self.login())

        center(self.root)

    # Verifies login credentials
    def login(self):
        # Retrieves the username and password from the entry boxes, storing them as variables
        username = self.usernameVar.get()
        password = self.passwordVar.get()

        # Checks that username and password aren't blank
        if username and password:
            user = executeSQL('SELECT * FROM staffTbl WHERE staffID = ?', (username,), False)
            # If a matching records is found, it drops into the following code
            if user:
                # makes userID, fullname and accessLevel global so that they can be used later by the program
                global userID, fullName, accessLevel
                userID = username
                accessLevel = user[4]
                fullName = user[2] + ' ' + user[1]
                salt = user[6]
                storedPass = user[5]
                # If access level ‘x’ i.e. no longer have access to system, a suitable error message is output
                if accessLevel == 'x':
                    self.errorVar.set('Error: User has no access rights')
                else:
                    # Hashes the input password with the same salt as originally used
                    hashedPass = bcrypt.hashpw(password.encode('utf-8'), salt)
                    # Checks that hashed input password matches hashed stored password
                    if hashedPass == storedPass:
                        # Closes the window, sets Boolean var ‘authenticated’ to true, proceeding to the main menu
                        self.closeWindow()
                        self.authenticated = True
                    else:
                        self.errorVar.set('Error: Incorrect\nUsername or Password')
            # If no records matched, the errorVar text variable is set to a suitable error message
            else:
                self.errorVar.set('Error: Incorrect\nUsername or Password')
        else:
            self.errorVar.set('Error: Please Fill all Fields')

    # Creates password reset window
    def forgotPassword(self):
        # Creates a frame for admin login
        self.passWin = Toplevel(self.root)
        self.passWin.iconbitmap(icon)
        self.passWin.protocol('WM_DELETE_WINDOW', lambda: (self.passWin.destroy(),
                                                           self.forgotPass.bind('<Button-1>',
                                                                                lambda x: self.forgotPassword())))
        self.forgotPass.bind('<Button-1>', lambda x: self.passWin.lift())
        self.passWin.title('Password Reset')
        self.adminFrame = Frame(self.passWin)
        # packs frame to window
        self.adminFrame.pack(side=LEFT, expand=True)
        self.adminUsernameLabel = Label(self.adminFrame, text='Admin Username:', font='none 11')
        self.adminUsernameVar = StringVar()
        self.adminUsernameBox = ttk.Entry(self.adminFrame, textvariable=self.adminUsernameVar)
        self.adminPasswordLabel = Label(self.adminFrame, text='Admin Password:', font='none 11')
        self.adminPasswordVar = StringVar()
        self.adminPasswordBox = ttk.Entry(self.adminFrame, show='•', textvariable=self.adminPasswordVar)
        self.adminErrorVar = StringVar()
        self.adminErrorLabel = Label(self.adminFrame, textvariable=self.adminErrorVar, font='none 11 bold', fg='red')
        self.loginButton = ttk.Button(self.adminFrame, text='Login', command=lambda: self.adminLogin())
        # Grids buttons/labels/entries to frame
        self.adminUsernameLabel.grid(row=1, column=0, padx=(10, 0))
        self.adminUsernameBox.grid(row=1, column=1, pady=10, padx=10)
        self.adminPasswordLabel.grid(row=2, column=0, padx=(10, 0))
        self.adminPasswordBox.grid(row=2, column=1, pady=10, padx=10)
        self.adminErrorLabel.grid(row=3, column=0, columnspan=2)
        self.loginButton.grid(row=4, column=0, columnspan=2, pady=(0, 20), padx=10, ipadx=10, ipady=2, sticky='news')

        # Creates a seperator between the frames
        self.seperator = ttk.Separator(self.passWin, orient='vertical')
        self.seperator.pack(side=LEFT, fill=Y)

        # Creates a frame to enter a username and new password
        # Entry boxes and buttons are readonly/disabled until the admin password is entered
        self.passFrame = Frame(self.passWin)
        self.passFrame.pack(side=LEFT, expand=True)
        self.usernameLabel = Label(self.passFrame, text='Staff Username:', font='none 11')
        self.staffUsernameVar = StringVar()
        self.usernameBox = ttk.Entry(self.passFrame, textvariable=self.staffUsernameVar, state='readonly')
        self.passwordLabel = Label(self.passFrame, text='New Password:', font='none 11', )
        self.newPasswordVar = StringVar()
        self.passwordBox = ttk.Entry(self.passFrame, show='•', textvariable=self.newPasswordVar, state='readonly')
        self.newPassErrorVar = StringVar()
        self.newPassErrorLabel = Label(self.passFrame, textvariable=self.newPassErrorVar, font='none 11 bold', fg='red')
        self.confirmButton = ttk.Button(self.passFrame, text='Confirm', state='disabled',
                                        command=lambda: self.changePass())
        # Grids buttons/labels/entries to frame
        self.usernameLabel.grid(row=1, column=0)
        self.usernameBox.grid(row=1, column=1, pady=10, padx=10)
        self.passwordLabel.grid(row=2, column=0)
        self.passwordBox.grid(row=2, column=1, pady=10, padx=10)
        self.newPassErrorLabel.grid(row=3, column=0, columnspan=2)
        self.confirmButton.grid(row=4, column=0, columnspan=2, pady=(0, 20), padx=10, ipadx=10, ipady=2, sticky='news')

        center(self.passWin)

    # Verifies admin credentials
    def adminLogin(self):
        # Retrieves admin username/password from form
        username = self.adminUsernameVar.get()
        password = self.adminPasswordVar.get()
        # Fetches record with the same username as inputted
        user = executeSQL('SELECT * FROM staffTbl WHERE staffID = ?', (username,), False)
        if user:
            adminAccessLevel = user[4]
            adminFullName = user[2] + ' ' + user[1]
            storedPass = user[5]
            salt = user[6]
            # Hashes the password input with the salt saved in the record
            password = bcrypt.hashpw(password.encode('utf-8'), salt)
            # Compares the input hashed password with the stored hashed password
            if password == storedPass:
                # Checks if user has admin status i.e. access lvl. 3
                if adminAccessLevel == 3:
                    # Disables admin login frame
                    self.loginButton['state'] = 'disabled'
                    self.adminErrorLabel.config(fg='green')

                    self.adminUsernameBox.config(state='readonly')
                    self.adminPasswordBox.config(state='readonly')
                    self.adminErrorVar.set('Logged in as ' + adminFullName)
                    # Enables password change frame
                    self.usernameBox.config(state='normal')
                    self.passwordBox.config(state='normal')
                    self.confirmButton['state'] = 'normal'
                else:
                    self.adminErrorVar.set('Error: Insufficient Access Level')
            else:
                self.adminErrorVar.set('Error: Incorrect\nUsername or Password')
        else:
            self.adminErrorVar.set('Error: Incorrect\nUsername or Password')

    # Changed password of input user
    def changePass(self):
        username = self.staffUsernameVar.get()
        password = self.newPasswordVar.get()
        if username and password:
            user = executeSQL('SELECT * FROM staffTbl WHERE staffID = ?', (username,), False)
            if user:
                salt = user[6]
                password = bcrypt.hashpw(password.encode('utf-8'), salt)
                executeSQL('UPDATE staffTbl SET password = ? WHERE staffID = ?', (password, username), False)
                self.newPassErrorLabel.config(fg='green')
                self.newPassErrorVar.set('Password Reset Successfully')
            else:
                self.newPassErrorLabel.config(fg='red')
                self.newPassErrorVar.set('Error: User Not Found')
        else:
            self.newPassErrorLabel.config(fg='red')
            self.newPassErrorVar.set('Error: Enter Username\nand Password')

    def closeWindow(self):
        # destroys the login window
        self.root.destroy()


############################################# MAIN MENU ############################################

class mainMenu:
    # Creates main menu window
    def __init__(self, root):
        self.root = root
        self.root.title('Main Menu')
        self.root.iconbitmap(icon)
        self.frame = Frame(self.root)
        self.frame.pack()
        # Calls the logout function when the main menu is closed
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.logout())
        # Creates labels with the Trust's name, a welcome message and the user's access level
        self.kingfisherLabel = Label(self.frame, text='Kingfisher Trust', font='algerian 18 bold', fg='#2380b7')
        self.userLabel = Label(self.frame, text='Welcome\n' + fullName, font='none 11')
        self.userAccessLabel = Label(self.frame, text='Access Level: ' + str(accessLevel), font='none 9')
        # Creates all the buttons for the user to navigate the system, and
        # states what functions are called when the buttons are pressed
        self.orderButton = ttk.Button(self.frame, text='New Order', command=lambda: self.newOrder())
        self.donatButton = ttk.Button(self.frame, text='New Donation', command=lambda: self.newDonat())
        self.viewOrdersButton = ttk.Button(self.frame, text='View Orders', command=lambda: self.viewOrders())
        self.viewDonationsButton = ttk.Button(self.frame, text='View Donations', command=lambda: self.viewDonations())
        self.viewItemsButton = ttk.Button(self.frame, text='View Items', command=lambda: self.viewItems())
        self.viewDonorsButton = ttk.Button(self.frame, text='View Donors', command=lambda: self.viewDonors())
        self.viewSuppliersButton = ttk.Button(self.frame, text='View Suppliers', command=lambda: self.viewSuppliers())
        self.viewStaffButton = ttk.Button(self.frame, text='View Staff', command=lambda: self.viewStaff())
        self.viewRecipientsButton = ttk.Button(self.frame, text='View Recipients',
                                               command=lambda: self.viewRecipients())
        self.viewExpendituresButton = ttk.Button(self.frame, text='View Expenditures',
                                                 command=lambda: self.viewExpenditures())
        self.logoutButton = ttk.Button(self.frame, text='Logout', command=lambda: self.logout())

        # Grids all the buttons/labels to the frame
        self.kingfisherLabel.grid(row=0, column=0, columnspan=2)
        self.userLabel.grid(row=1, column=0)
        self.userAccessLabel.grid(row=2, column=0)
        self.logoutButton.grid(row=1, column=1, rowspan=2, ipadx=10, ipady=2)
        self.orderButton.grid(row=3, column=0, padx=(10, 0), pady=(5, 10), ipadx=10, ipady=2, sticky='news')
        self.donatButton.grid(row=3, column=1, padx=(0, 10), pady=(5, 10), ipadx=10, ipady=2, sticky='news')
        self.viewOrdersButton.grid(row=4, column=0, padx=(10, 0), ipadx=10, ipady=2, sticky='news')
        self.viewDonationsButton.grid(row=4, column=1, padx=(0, 10), ipadx=10, ipady=2, sticky='news')
        self.viewItemsButton.grid(row=5, column=0, padx=(10, 0), ipadx=10, ipady=2, sticky='news')
        self.viewDonorsButton.grid(row=5, column=1, padx=(0, 10), ipadx=10, ipady=2, sticky='news')
        self.viewSuppliersButton.grid(row=6, column=0, padx=(10, 0), ipadx=10, ipady=2, sticky='news')
        self.viewRecipientsButton.grid(row=6, column=1, padx=(0, 10), ipadx=10, ipady=2, sticky='news')
        self.viewStaffButton.grid(row=7, column=0, padx=(10, 0), pady=(0, 10), ipadx=10, ipady=2, sticky='news')
        self.viewExpendituresButton.grid(row=7, column=1, padx=(0, 10), pady=(0, 10), ipadx=10, ipady=2, sticky='news')

        # Checks access level and disables relevant buttons
        accesslevel(2, self.donatButton, self.orderButton)

        center(self.root)

    def logout(self):
        # Creates dialogue box to confirm whether the user wants to logout of the system
        if messagebox.askyesno('Logout', 'Are you sure you want to logout?', icon='warning'):
            self.closeWindow()

    def closeWindow(self):
        # destroys the main menu window
        self.root.destroy()

    def disableMenu(self):
        # Hides the main menu window
        self.root.withdraw()

    def enableMenu(self):
        # Unhides the main menu window
        self.root.deiconify()

    def viewStaff(self):
        # Hides the main menu and creates the view staff window as a toplevel window
        self.disableMenu()
        self.staffRoot = Toplevel(self.root)
        self.createstaffWindow = staffWindow(self.staffRoot)

    def viewDonors(self):
        # Hides the main menu and creates the view donor window as a toplevel window
        self.disableMenu()
        self.donorRoot = Toplevel(self.root)
        self.createDonorWindow = donorWindow(self.donorRoot)

    def newDonat(self):
        # Hides the main menu and opens the view donation window, as well as the add new donation form
        self.disableMenu()
        self.donationRoot = Toplevel(self.root)
        self.createDonationWindow = donationWindow(self.donationRoot)
        self.createDonationWindow.addDonation()

    def viewDonations(self):
        # Hides the main menu and creates the view donation window as a toplevel window
        self.disableMenu()
        self.donationRoot = Toplevel(self.root)
        self.createDonationWindow = donationWindow(self.donationRoot)

    def viewSuppliers(self):
        # Hides the main menu and creates the view supplier window as a toplevel window
        self.disableMenu()
        self.supplierRoot = Toplevel(self.root)
        self.createSupplierWindow = supplierWindow(self.supplierRoot)

    def viewItems(self):
        # Hides the main menu and creates the view items window as a toplevel window
        self.disableMenu()
        self.itemRoot = Toplevel(self.root)
        self.createItemWindow = itemWindow(self.itemRoot)

    def newOrder(self):
        # Hides the main menu and opens the view order window, as well as the add new order form
        self.disableMenu()
        self.orderRoot = Toplevel(self.root)
        self.createOrderWindow = orderWindow(self.orderRoot)
        self.createOrderWindow.addOrder()

    def viewOrders(self):
        # Hides the main menu and creates the view orders window as a toplevel window
        self.disableMenu()
        self.orderRoot = Toplevel(self.root)
        self.createOrderWindow = orderWindow(self.orderRoot)

    def viewRecipients(self):
        # Hides the main menu and creates the view recipients window as a toplevel window
        self.disableMenu()
        self.recipientRoot = Toplevel(self.root)
        self.createRecipientWindow = recipientWindow(self.recipientRoot)

    def viewExpenditures(self):
        # Hides the main menu and creates the view expenditures window as a toplevel window
        self.disableMenu()
        self.expenditureRoot = Toplevel(self.root)
        self.createExpenditureWindow = expenditureWindow(self.expenditureRoot)


################################### STAFF WINDOW ###################################################

class staffWindow:
    # Creates view staff window
    def __init__(self, root):
        self.root = root
        self.root.title('View Staff')
        self.root.iconbitmap(icon)
        self.frame = Frame(self.root)
        self.frame.pack(fill='both', expand=True)
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.closeWindow())
        # Creates title label, 'View Staff Records'
        self.titleLabel = Label(self.frame, text='View Staff Records', font='none 11')
        # Creates refresh button, to reload data from the database,
        # And the return button, to close the staff window and return the user to the main menu
        self.refreshButton = ttk.Button(self.frame, text='↺', command=lambda: loadDatabase(self.tree, 'staffTbl', True))
        self.returnButton = ttk.Button(self.frame, text='Main Menu', command=lambda: self.closeWindow())
        # Saves input search value from searchBox as searchVar
        self.searchVar = StringVar()
        self.searchBox = ttk.Entry(self.frame, textvariable=self.searchVar)
        # Creates a dropdown menu, with all the fields listed, set to staffID by default
        self.searchFieldVar = StringVar()
        self.searchField = ttk.OptionMenu(self.frame, self.searchFieldVar, 'StaffID', 'StaffID',
                                          'Surname', 'Forename', 'Contact', 'AccessLevel')
        # Creates a 'Search' button, which calls the search function when pressed
        self.searchButton = ttk.Button(self.frame, text='Search', command=lambda: self.search())
        # Grids the above labels, buttons and entry boxes to the frame
        self.titleLabel.grid(row=0, column=1, sticky='ns')
        self.refreshButton.grid(row=0, column=4, pady=10)
        self.returnButton.grid(row=0, column=0, pady=10, padx=10, ipadx=10, ipady=2, sticky='w')
        self.searchField.grid(row=1, column=0, padx=10, sticky='ew')
        self.searchBox.grid(row=1, column=1, sticky='ew')
        self.searchButton.grid(row=1, column=2, pady=10, padx=(10, 0), ipadx=10)
        # Creates the treeview, defining each column and naming its heading with the relevant field name
        columns = ('StaffID', 'Surname', 'Forename', 'Contact', 'AccessLevel')
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        for col in columns:
            self.tree.column(col, width=100, minwidth=100)
            self.tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(self.tree, _col, False))
        self.tree.grid(row=2, column=0, sticky='ewns', rowspan=3, columnspan=3, padx=(10, 0), pady=(10, 0))
        self.frame.columnconfigure(1, weight=1)  # column with treeview
        self.frame.rowconfigure([2, 3, 4], weight=1)  # row with treeview
        # Creates vertical and horizontal scrollbars, linking them to the treeview
        self.scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=self.tree.yview)
        self.scrollbar.grid(row=2, column=3, sticky='ns', rowspan=3, pady=10)
        self.tree.configure(yscrollcommand=self.scrollbar.set, selectmode='browse')
        self.xscrollbar = ttk.Scrollbar(self.frame, orient='horizontal', command=self.tree.xview)
        self.xscrollbar.grid(row=5, column=0, sticky='ew', columnspan=4, pady=(0, 10))
        self.tree.configure(xscrollcommand=self.xscrollbar.set, selectmode='browse')
        # Creates the add, edit and delete staff buttons, which call their respective functions when clicked
        self.addStaffButton = ttk.Button(self.frame, text='Add Staff', command=lambda: self.addStaff())
        self.editStaffButton = ttk.Button(self.frame, text='Edit Staff', command=lambda: self.editStaff())
        self.delStaffButton = ttk.Button(self.frame, text='Delete Staff', command=lambda: self.delStaff())
        # Grids the add, edit and delete buttons to the frame
        self.addStaffButton.grid(row=2, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.editStaffButton.grid(row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delStaffButton.grid(row=4, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        # Runs the search function when the user presses the 'enter' button (same as searchButton)
        self.root.bind('<Return>', lambda event: self.search())
        # Calls function to load the records from the database
        loadDatabase(self.tree, 'staffTbl', False)

        # Checks access level and disables relevant buttons
        accesslevel(3, self.addStaffButton, self.editStaffButton, self.delStaffButton)

        self.tree.bind('<<TreeviewSelect>>', lambda event: self.on_select())

        center(self.root)

    def on_select(self):
        if self.tree.set(self.tree.selection()[0], '#1') == userID:
            self.editStaffButton['state'] = 'normal'
            self.delStaffButton['state'] = 'normal'
        else:
            accesslevel(3, self.delStaffButton, self.editStaffButton)

    # Destroys staffWindow, opens main menu
    def closeWindow(self):
        self.root.destroy()
        app.enableMenu()

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
        records = executeSQL('SELECT * FROM staffTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records fetched into the treeview
            self.tree.insert('', 0, values=(i[0], i[1], i[2], i[3], i[4]))

    # Creates add staff window
    def addStaff(self):
        disableWindow(self.returnButton, self.addStaffButton, self.editStaffButton, self.delStaffButton)
        self.staffWin = Toplevel(self.root)
        self.staffWin.title('Add Staff')
        self.staffWin.iconbitmap(icon)
        self.staffWin.protocol('WM_DELETE_WINDOW',
                               lambda: (enableWindow(self.staffWin, self.returnButton, self.addStaffButton,
                                                     self.editStaffButton, self.delStaffButton),
                                        accesslevel(3, self.addStaffButton, self.editStaffButton,
                                                    self.delStaffButton)))
        self.addStaffFrame = Frame(self.staffWin)
        self.addStaffFrame.pack()
        # Creates all the labels and entry boxes for each field
        self.detailLabel = Label(self.addStaffFrame, text='Enter Staff Details:', font='none 11 bold')
        self.forenameLabel = Label(self.addStaffFrame, text='Forename:', font='none 11')
        self.forenameVar = StringVar()
        self.forenameBox = ttk.Entry(self.addStaffFrame, textvariable=self.forenameVar)
        self.surnameLabel = Label(self.addStaffFrame, text='Surname:', font='none 11')
        self.surnameVar = StringVar()
        self.surnameBox = ttk.Entry(self.addStaffFrame, textvariable=self.surnameVar)
        self.contactLabel = Label(self.addStaffFrame, text='Phone No.:', font='none 11')
        self.contactVar = StringVar()
        self.contactBox = ttk.Entry(self.addStaffFrame, textvariable=self.contactVar)
        self.accessLevelLabel = Label(self.addStaffFrame, text='Access Level:', font='none 11')
        # Creates a dropdown for the accesslevel to be selected from the given options
        self.accessLevelVar = StringVar()
        self.accessLevelVar.set('Select...')
        self.accessLevelDropdown = ttk.OptionMenu(self.addStaffFrame, self.accessLevelVar, '1', '1', '2', '3')
        self.passwordLabel = Label(self.addStaffFrame, text='Password:', font='none 11')
        self.passwordVar = StringVar()
        # Both the password and password confirmation show *s for any input characters, to prevent
        # shoulder surfers from seeing the input password
        self.passwordBox = ttk.Entry(self.addStaffFrame, show='•', textvariable=self.passwordVar)
        self.passConfirmLabel = Label(self.addStaffFrame, text='Confirm Password:', font='none 11')
        self.passConfirmVar = StringVar()
        self.passConfirmBox = ttk.Entry(self.addStaffFrame, show='•', textvariable=self.passConfirmVar)
        self.errorVar = StringVar()
        # Creates error label to display any errors
        self.errorLabel = Label(self.addStaffFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
        # Creates save button, which calls the function saveStaff when pressed
        self.saveButton = ttk.Button(self.addStaffFrame, text='Save New Staff', command=lambda: self.saveStaff())
        # Grids all labels, entry boxes, dropdowns and buttons that we have created
        self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
        self.forenameLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
        self.forenameBox.grid(row=1, column=1, padx=(0, 10))
        self.surnameLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
        self.surnameBox.grid(row=2, column=1, padx=(0, 10))
        self.contactLabel.grid(row=3, column=0, sticky='E', padx=(10, 0))
        self.contactBox.grid(row=3, column=1, padx=(0, 10))
        self.accessLevelLabel.grid(row=4, column=0, sticky='E', padx=(10, 0))
        self.accessLevelDropdown.grid(row=4, column=1, padx=(0, 10), sticky='ew')
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
                    staffID = 'ST' + str(''.join(['%s' % random.randint(0, 9) for num in range(0, 5)]))
                    if messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nStaffID:\t\t' + staffID +
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
                            accesslevel(3, self.addStaffButton, self.editStaffButton, self.delStaffButton)
                            messagebox.showinfo('Success!', 'Staff Details Saved')
                        except sqlite3.IntegrityError:  # Outputs error if staffID is not unique
                            self.errorVar.set('Error: Failed To Update Database.\nPlease Try Again')
                else:  # Outputs error if passwords don't match
                    self.errorVar.set("Error: Passwords Don't Match")
            else:  # Outputs error if contact is invalid
                self.errorVar.set('Error: Invalid Phone Number')
        else:  # Outputs error if not all fields are filled
            self.errorVar.set('Error: Please Fill All Fields')

    # Creates edit staff window
    def editStaff(self):
        if self.tree.selection():  # Runs IF a record is selected from treeview
            disableWindow(self.returnButton, self.addStaffButton, self.editStaffButton, self.delStaffButton)
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
            self.staffWin = Toplevel(self.root)
            self.staffWin.title('Edit Staff')
            self.staffWin.iconbitmap(icon)
            self.staffWin.protocol('WM_DELETE_WINDOW',
                                   lambda: (enableWindow(self.staffWin, self.returnButton, self.addStaffButton,
                                                         self.editStaffButton, self.delStaffButton),
                                            accesslevel(3, self.addStaffButton, self.editStaffButton,
                                                        self.delStaffButton)))
            self.editStaffFrame = Frame(self.staffWin)
            self.editStaffFrame.pack()
            # Creates all the labels and entry boxes where necessary for each field
            self.detailLabel = Label(self.editStaffFrame, text='Edit Staff Details:', font='none 11 bold')
            self.staffIDLabel = Label(self.editStaffFrame, text='StaffID:', font='none 11')
            # staffID is only a label, so it cannot be edited by the user
            self.staffIDInsert = Label(self.editStaffFrame, text=staffID, font='none 11')
            self.forenameLabel = Label(self.editStaffFrame, text='Forename:', font='none 11')
            self.forenameVar = StringVar()
            self.forenameBox = ttk.Entry(self.editStaffFrame, textvariable=self.forenameVar)
            self.surnameLabel = Label(self.editStaffFrame, text='Surname:', font='none 11')
            self.surnameVar = StringVar()
            self.surnameBox = ttk.Entry(self.editStaffFrame, textvariable=self.surnameVar)
            self.contactLabel = Label(self.editStaffFrame, text='Phone No.:', font='none 11')
            self.contactVar = StringVar()
            self.contactBox = ttk.Entry(self.editStaffFrame, textvariable=self.contactVar)
            # Creates a dropdown for the accesslevel to be selected from the given options
            self.accessLevelLabel = Label(self.editStaffFrame, text='Access Level:', font='none 11')
            self.accessLevelVar = StringVar()
            self.accessLevelDropdown = ttk.OptionMenu(self.editStaffFrame, self.accessLevelVar, '1', '1', '2', '3')
            if accessLevel < 3:
                self.accessLevelDropdown['state'] = 'disabled'
            self.passwordLabel = Label(self.editStaffFrame, text='Password:', font='none 11')
            self.passwordVar = StringVar()
            # Both password and new password only show *s for any input characters to
            # prevent shoulder surfers from seeing the input password
            self.passwordBox = ttk.Entry(self.editStaffFrame, show='•', textvariable=self.passwordVar)
            # Creates button (text only) to change password
            self.changePass = Label(self.editStaffFrame, text='Change Password?', fg='blue', cursor='hand2')
            self.newPasswordLabel = Label(self.editStaffFrame, text='New Password:', font='none 11')
            self.newPasswordVar = StringVar()
            self.newPasswordBox = ttk.Entry(self.editStaffFrame, show='•', textvariable=self.newPasswordVar)
            self.errorVar = StringVar()
            # Creates error label to display any errors
            self.errorLabel = Label(self.editStaffFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
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
            self.accessLevelLabel.grid(row=5, column=0, sticky='E', padx=(10, 0))
            self.accessLevelDropdown.grid(row=5, column=1, padx=(0, 10), sticky='ew')
            self.passwordLabel.grid(row=6, column=0, sticky='E', padx=(10, 0))
            self.passwordBox.grid(row=6, column=1, padx=(0, 10))
            self.changePass.grid(row=7, column=0, columnspan=2)
            self.changePassVar = False
            self.changePass.bind('<Button-1>', lambda x: self.changePassword())
            self.errorLabel.grid(row=9, column=0, columnspan=2)
            self.saveButton.grid(row=10, column=0, columnspan=2, pady=(0, 10))
            # Inserts the currect fields into the boxes/ dropdowns
            self.forenameBox.insert(INSERT, forename)
            self.surnameBox.insert(INSERT, surname)
            self.contactBox.insert(INSERT, contact)
            self.accessLevelVar.set(staffAccessLevel)
            # Runs the save function when the user presses the 'enter' button (same as saveButton)
            self.staffWin.bind('<Return>', lambda event: self.saveEditStaff(staffID, password, salt))

            center(self.staffWin)

        else:  # Outputs error message if not record has been selected
            messagebox.showerror('Error', 'No Record Selected')

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
                    if messagebox.askyesno('Confirm Changes', 'Are these details correct?\n\nStaffID:\t\t' + staffID +
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
                        accesslevel(3, self.addStaffButton, self.editStaffButton, self.delStaffButton)
                        # Outputs success dialogue box
                        messagebox.showinfo('Success!', 'Staff Details Updated')
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
                existsForeign = executeSQL('SELECT * FROM donationsTbl WHERE staffID = ?', (staffID,), True)
                existsForeign += executeSQL('SELECT * FROM orderTbl WHERE staffID = ?', (staffID,), True)
                existsForeign += executeSQL('SELECT * FROM foodDonatTbl WHERE staffID = ?', (staffID,), True)
                existsForeign += executeSQL('SELECT * FROM giveFoodTbl WHERE staffID = ?', (staffID,), True)
                existsForeign += executeSQL('SELECT * FROM expenditureTbl WHERE staffID = ?', (staffID,), True)
                # If staffID is NOT stored in any other tables
                if not existsForeign:
                    # Confirms that user wants to delete the record
                    if messagebox.askokcancel('Delete', 'Are you sure you want to permanantly delete this record?'):
                        for selected_item in self.tree.selection():
                            # Delete the record from the database
                            executeSQL('DELETE FROM staffTbl WHERE staffID=?', (staffID,), False)
                            # Remove the item from the treeview
                            self.tree.delete(selected_item)
                else:  # If staffID is stored in other tables
                    if messagebox.askokcancel('Delete',
                                              'Error: Record is in use in other tables.\nRemove Login from System?'):
                        # Change access level to 'x'
                        executeSQL('UPDATE staffTbl SET accessLevel=?, password=? WHERE staffID=?', ('x', '', staffID),
                                   False)
                        # Reload records from database into treeview
                        loadDatabase(self.tree, 'staffTbl', False)
            else:
                messagebox.showerror('Error', 'Record Already Removed From System')
        else:
            messagebox.showerror('Error', 'No Record Selected')


###########################################################################

################################### DONOR WINDOW ###################################################

class donorWindow:
    # Creates view donors window
    def __init__(self, root):
        self.root = root
        self.root.title('View Donors')
        self.root.iconbitmap(icon)
        self.frame = Frame(self.root)
        self.frame.pack(fill='both', expand=True)
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.closeWindow())
        # Creates title label, 'View Donor Records'
        self.titleLabel = Label(self.frame, text='View Donor Records', font='none 11')
        # Creates refresh button, to reload data from the database, and the return button, to close the donor window
        # and return the user to the main menu
        self.refreshButton = ttk.Button(self.frame, text='↺', command=lambda: loadDatabase(self.tree, 'donorTbl', True))
        self.returnButton = ttk.Button(self.frame, text='Main Menu', command=lambda: self.closeWindow())
        # Saves input search value from searchBox as searchVar
        self.searchVar = StringVar()
        self.searchBox = ttk.Entry(self.frame, textvariable=self.searchVar)
        # Creates a dropdown menu, with all the fields listed, set to donorID by default
        self.searchFieldVar = StringVar()
        self.searchField = ttk.OptionMenu(self.frame, self.searchFieldVar, 'DonorID', 'DonorID', 'Surname', 'Forename',
                                          'Contact')
        # Creates a 'Search' button, which calls the search function when pressed
        self.searchButton = ttk.Button(self.frame, text='Search', command=lambda: self.search())
        # Grids all the above labels, buttons and entry boxes to the frame
        self.titleLabel.grid(row=0, column=1, sticky='ns')
        self.refreshButton.grid(row=0, column=4, pady=10)
        self.returnButton.grid(row=0, column=0, pady=10, padx=10, ipadx=10, ipady=2, sticky='w')
        self.searchField.grid(row=1, column=0, padx=10, sticky='ew')
        self.searchBox.grid(row=1, column=1, sticky='ew')
        self.searchButton.grid(row=1, column=2, pady=10, padx=(10, 0), ipadx=10)
        # Creates the treeview, defining each column and naming its heading with the relevant field name
        columns = ('DonorID', 'Surname', 'Forename', 'Contact')
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        for col in columns:
            self.tree.column(col, width=100, minwidth=100)
            self.tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(self.tree, _col, False))
        self.tree.grid(row=2, column=0, sticky='ewns', rowspan=3, columnspan=3, padx=(10, 0), pady=(10, 0))
        self.frame.columnconfigure(1, weight=1)  # column with treeview
        self.frame.rowconfigure([2, 3, 4], weight=1)  # row with treeview
        # Creates vertical and horizontal scrollbars, linking them to the treeview
        self.scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=self.tree.yview)
        self.scrollbar.grid(row=2, column=3, sticky='ns', rowspan=3, pady=10)
        self.tree.configure(yscrollcommand=self.scrollbar.set, selectmode='browse')
        self.xscrollbar = ttk.Scrollbar(self.frame, orient='horizontal', command=self.tree.xview)
        self.xscrollbar.grid(row=5, column=0, sticky='ew', columnspan=4, pady=(0, 10))
        self.tree.configure(xscrollcommand=self.xscrollbar.set, selectmode='browse')
        # Creates the add/edit/delete donor buttons, which calls their respective functions when clicked
        self.addDonorButton = ttk.Button(self.frame, text='Add Donor', command=lambda: self.addDonor())
        self.editDonorButton = ttk.Button(self.frame, text='Edit Donor', command=lambda: self.editDonor())
        self.delDonorButton = ttk.Button(self.frame, text='Delete Donor', command=lambda: self.delDonor())
        # Grids the add/edit/delete donor buttons to the frame
        self.addDonorButton.grid(row=2, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.editDonorButton.grid(row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delDonorButton.grid(row=4, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
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
        app.enableMenu()

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
        records = executeSQL('SELECT * FROM donorTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records found into the treeview
            self.tree.insert('', 0, values=(i[0], i[1], i[2], i[3]))

    # Creates add donor window
    def addDonor(self):
        disableWindow(self.returnButton, self.addDonorButton, self.editDonorButton, self.delDonorButton)
        self.donorWin = Toplevel(self.root)
        self.donorWin.title('Add Donor')
        self.donorWin.iconbitmap(icon)
        self.donorWin.protocol('WM_DELETE_WINDOW',
                               lambda: (enableWindow(self.donorWin, self.returnButton, self.addDonorButton,
                                                     self.editDonorButton, self.delDonorButton),
                                        accesslevel(2, self.addDonorButton, self.editDonorButton),
                                        accesslevel(3, self.delDonorButton)))
        self.addDonorFrame = Frame(self.donorWin)
        self.addDonorFrame.pack()
        # Creates all the labels and entry boxes for each field
        self.detailLabel = Label(self.addDonorFrame, text='Enter Donor Details:', font='none 11 bold')
        self.forenameLabel = Label(self.addDonorFrame, text='Forename:', font='none 11')
        self.forenameVar = StringVar()
        self.forenameBox = ttk.Entry(self.addDonorFrame, textvariable=self.forenameVar)
        self.surnameLabel = Label(self.addDonorFrame, text='Surname:', font='none 11')
        self.surnameVar = StringVar()
        self.surnameBox = ttk.Entry(self.addDonorFrame, textvariable=self.surnameVar)
        self.contactLabel = Label(self.addDonorFrame, text='Contact:', font='none 11')
        self.contactVar = StringVar()
        self.contactBox = ttk.Entry(self.addDonorFrame, textvariable=self.contactVar)
        # Creates text variable and error label to output any error messages
        self.errorVar = StringVar()
        self.errorLabel = Label(self.addDonorFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
        # Creates save button, which calls the function saveDonor when pressed
        self.saveButton = ttk.Button(self.addDonorFrame, text='Save New Donor', command=lambda: self.saveDonor())
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
                donorID = 'DO' + str(''.join(['%s' % random.randint(0, 9) for num in range(0, 5)]))
                # Asks for user confirmation of the input details
                if messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nDonorID:\t\t' + donorID +
                                                          '\nName:\t\t' + forename + ' ' + surname +
                                                          '\nContact:\t\t' + contact):
                    try:
                        # Inserts record into donorTbl
                        executeSQL('INSERT INTO donorTbl VALUES (?,?,?,?)', (donorID, surname, forename, contact),
                                   False)
                        loadDatabase(self.tree, 'donorTbl', False)  # Reloads records into treeview
                        # Destroys add donor toplevel and returns to view donors window
                        enableWindow(self.donorWin, self.returnButton, self.addDonorButton, self.editDonorButton,
                                     self.delDonorButton)
                        accesslevel(2, self.addDonorButton, self.editDonorButton)
                        accesslevel(3, self.delDonorButton)
                        messagebox.showinfo('Success!', 'New Donor Saved')
                    except sqlite3.IntegrityError:  # Outputs error message if donorID is not unique
                        self.errorVar.set('Error: Failed To Update Database.\nPlease Try Again')
            else:
                self.errorVar.set('Error: Please Enter a\nValid Phone No. Or Email')
        else:  # Outputs error if not all fields are filled
            self.errorVar.set('Error: Please Fill All Fields')

    # Creates edit donor window
    def editDonor(self):
        # Runs IF a record is selected from treeview
        if self.tree.selection():
            disableWindow(self.returnButton, self.addDonorButton, self.editDonorButton, self.delDonorButton)
            for selected_item in self.tree.selection():
                # Finds record from database that matches selected record
                donor = executeSQL('SELECT * FROM donorTbl WHERE donorID=?', (self.tree.set(selected_item, '#1'),),
                                   False)
                donorID = donor[0]
                surname = donor[1]
                forename = donor[2]
                contact = donor[3]
            self.donorWin = Toplevel(self.root)
            self.donorWin.title('Edit Donor')
            self.donorWin.iconbitmap(icon)
            self.donorWin.protocol('WM_DELETE_WINDOW',
                                   lambda: (enableWindow(self.donorWin, self.returnButton, self.addDonorButton,
                                                         self.editDonorButton, self.delDonorButton),
                                            accesslevel(2, self.addDonorButton, self.editDonorButton),
                                            accesslevel(3, self.delDonorButton)))
            self.editDonorFrame = Frame(self.donorWin)
            self.editDonorFrame.pack()
            # Creates all the labels and entry boxes where necessary for each field (no entry box for donorID)
            self.detailLabel = Label(self.editDonorFrame, text='Edit Donor Details:', font='none 11 bold')
            self.donorIDLabel = Label(self.editDonorFrame, text='DonorID:', font='none 11')
            self.donorIDInsert = Label(self.editDonorFrame, text=donorID, font='none 11')
            self.forenameLabel = Label(self.editDonorFrame, text='Forename:', font='none 11')
            self.forenameVar = StringVar()
            self.forenameBox = ttk.Entry(self.editDonorFrame, textvariable=self.forenameVar)
            self.surnameLabel = Label(self.editDonorFrame, text='Surname:', font='none 11')
            self.surnameVar = StringVar()
            self.surnameBox = ttk.Entry(self.editDonorFrame, textvariable=self.surnameVar)
            self.contactLabel = Label(self.editDonorFrame, text='Contact:', font='none 11')
            self.contactVar = StringVar()
            self.contactBox = ttk.Entry(self.editDonorFrame, textvariable=self.contactVar)
            # Creates text variable and error label to output error messages to
            self.errorVar = StringVar()
            self.errorLabel = Label(self.editDonorFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
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
            self.forenameBox.insert(INSERT, forename)
            self.surnameBox.insert(INSERT, surname)
            self.contactBox.insert(INSERT, contact)
            # Runs the save function when the user presses the 'enter' button (same as saveButton)
            self.donorWin.bind('<Return>', lambda event: self.saveEditDonor(donorID))

            center(self.donorWin)

        else:  # Outputs error message if no record has been selected
            messagebox.showerror('Error', 'No Record Selected')

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
                if messagebox.askyesno('Confirm Changes', 'Are these details correct?\n\nDonorID:\t\t'
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
                    messagebox.showinfo('Success!', 'Donor Details Updated')
            else:
                self.errorVar.set('Error: Please Enter a\nValid Phone No. Or Email')
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
            existsForeign = executeSQL('SELECT * FROM donationsTbl WHERE donorID = ?', (donorID,), True)
            existsForeign += executeSQL('SELECT * FROM foodDonatTbl WHERE donorID = ?', (donorID,), True)
            # If donorID is not stored in any other tables
            if not existsForeign:
                # Confirms that the user wants to permanently delete the record
                if messagebox.askokcancel('Delete', 'Are you sure you want to permanently delete this record?'):
                    for selected_item in self.tree.selection():
                        # Deletes the record from donorTbl
                        executeSQL('DELETE FROM donorTbl WHERE donorID=?', (donorID,), False)
                        # Removes the record from the treeview
                        self.tree.delete(selected_item)
            else:
                # If donorID is a foreign key in other tables, output error as the record cannot be deleted
                messagebox.showerror('Error', 'Error: Record in use by other tables')
        else:  # Outputs error message if no record has been selected
            messagebox.showerror('Error', 'No Record Selected')


###########################################################################

################################## DONATION WINDOW #################################################

class donationWindow:
    # Creates view donations window for financial and food donations
    def __init__(self, root):
        self.root = root
        self.root.title('View Donations')
        self.root.iconbitmap(icon)
        self.frame = Frame(self.root)
        self.frame.pack(fill=X)
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.closeWindow())

        # Creates title label, 'View Staff Records'
        self.titleLabel = Label(self.frame, text='View Donation Records', font='none 11')
        # Creates refresh button, to reload data from the database, and the return button, to close the staff window
        # and return the user to the main menu
        self.refreshButton = ttk.Button(self.frame, text='↺', command=lambda: self.checkTab())
        self.returnButton = ttk.Button(self.frame, text='Main Menu', command=lambda: self.closeWindow())

        self.titleLabel.grid(row=0, column=1, sticky='ns')
        self.refreshButton.grid(row=0, column=2, pady=10, padx=40, sticky='e')
        self.returnButton.grid(row=0, column=0, pady=10, padx=10, ipadx=10, ipady=2, sticky='w')

        self.frame.columnconfigure(1, weight=1)

        self.notebookFrame = Frame(self.root)
        self.notebookFrame.pack(fill='both', expand=True)
        self.notebook = ttk.Notebook(self.notebookFrame)
        self.moneyTab = Frame(self.notebook)
        self.foodTab = Frame(self.notebook)
        self.notebook.add(self.moneyTab, text='Money')
        self.notebook.add(self.foodTab, text='Food')
        self.notebook.pack(fill='both', expand=True, pady=10, padx=10)

        ################# MONEY DONATION TAB ##################
        # Saves input search value from searchBox as searchVar
        self.searchVar = StringVar()
        self.searchBox = ttk.Entry(self.moneyTab, textvariable=self.searchVar)
        # Creates a dropdown menu, with all the fields listed to search, set to donationID by default
        self.searchFieldVar = StringVar()
        self.searchField = ttk.OptionMenu(self.moneyTab, self.searchFieldVar, 'DonationID', 'DonationID', 'Amount',
                                          'Cash/Bank', 'Reference No', 'Date', 'DonorID', 'StaffID')
        # Creates a 'search' button, which calls the search function when pressed
        self.searchButton = ttk.Button(self.moneyTab, text='Search', command=lambda: self.search())
        # Creates a 'Create report' button, which launches the report function
        self.reportButton = ttk.Button(self.moneyTab, text='Create Report', command=lambda: self.report())
        # Grids all the above labels, buttons and entry boxes to the frame
        self.searchField.grid(row=1, column=0, pady=10, padx=10, sticky='ew')
        self.searchBox.grid(row=1, column=1, pady=10, sticky='ew')
        self.searchButton.grid(row=1, column=2, pady=10, padx=(10, 0), ipadx=10)
        self.reportButton.grid(row=1, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')

        # Creates the treeview, defining each column and naming its heading with the relevant field name
        columns = ('DonationID', 'Amount', 'Cash/Bank', 'Reference No', 'Date', 'DonorID', 'StaffID')
        self.tree = ttk.Treeview(self.moneyTab, columns=columns, show='headings')
        for col in columns:
            self.tree.column(col, width=100, minwidth=100)
            self.tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(self.tree, _col, False))
        self.tree.grid(row=2, column=0, sticky='ewns', rowspan=3, columnspan=3, padx=(10, 0), pady=(10, 0))

        self.moneyTab.rowconfigure([2, 3, 4], weight=1)
        self.moneyTab.columnconfigure(1, weight=1)
        # Creates vertical and horizontal scrollbars, linking them to the treeview
        self.scrollbar = ttk.Scrollbar(self.moneyTab, orient='vertical', command=self.tree.yview)
        self.scrollbar.grid(row=2, column=3, sticky='ns', rowspan=3, pady=10)
        self.tree.configure(yscrollcommand=self.scrollbar.set, selectmode='browse')
        self.xscrollbar = ttk.Scrollbar(self.moneyTab, orient='horizontal', command=self.tree.xview)
        self.xscrollbar.grid(row=5, column=0, sticky='ew', columnspan=4, pady=(0, 10))
        self.tree.configure(xscrollcommand=self.xscrollbar.set, selectmode='browse')
        # Creates the add, edit and delete donation buttons, which call their respective functions when clicked
        self.addDonationButton = ttk.Button(self.moneyTab, text='Add Donation', command=lambda: self.addDonation())
        self.editDonationButton = ttk.Button(self.moneyTab, text='Edit Donation', command=lambda: self.editDonation())
        self.delDonationButton = ttk.Button(self.moneyTab, text='Delete Donation', command=lambda: self.delDonation())
        # Grids the add, edit and delete buttons to the frame
        self.addDonationButton.grid(row=2, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.editDonationButton.grid(row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delDonationButton.grid(row=4, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        # Runs the search function when the user presses the 'enter' button (same as searchButton)
        self.root.bind('<Return>', lambda event: self.search())
        # Calls the function to load the records from the database
        loadDatabase(self.tree, 'donationsTbl', False)

        # Checks access level and disables relevant buttons
        accesslevel(2, self.addDonationButton, self.editDonationButton)
        accesslevel(3, self.delDonationButton)

        ################# FOOD DONATION TAB ###################
        # Saves input search value from searchBox as searchVar
        self.searchFoodVar = StringVar()
        self.searchFoodBox = ttk.Entry(self.foodTab, textvariable=self.searchFoodVar)
        # Creates a dropdown menu, with all the fields listed to search, set to FoodID by default
        self.searchFoodFieldVar = StringVar()
        self.searchFoodField = ttk.OptionMenu(self.foodTab, self.searchFoodFieldVar, 'FoodID', 'FoodID', 'Name',
                                              'DonationDate', 'ExpiryDate', 'GivenAway', 'DonorID', 'StaffID')
        # Creates a 'search' button, which calls the search function when pressed
        self.searchFoodButton = ttk.Button(self.foodTab, text='Search', command=lambda: self.foodSearch())
        # Grids all the above labels, buttons and entry boxes to the frame
        self.searchFoodField.grid(row=1, column=0, pady=10, padx=10, sticky='ew')
        self.searchFoodBox.grid(row=1, column=1, pady=10, sticky='ew')
        self.searchFoodButton.grid(row=1, column=2, pady=10, padx=(10, 0), ipadx=10)

        # Creates the treeview, defining each column and naming its heading with the relevant field name
        columns = ('FoodID', 'Name', 'DonationDate', 'ExpiryDate', 'GivenAway', 'DonorID', 'StaffID')
        self.foodTree = ttk.Treeview(self.foodTab, columns=columns, show='headings')
        for col in columns:
            self.foodTree.column(col, width=100, minwidth=100)
            self.foodTree.heading(col, text=col,
                                  command=lambda _col=col: treeview_sort_column(self.foodTree, _col, False))
        self.foodTree.grid(row=2, column=0, sticky='ewns', rowspan=3, columnspan=3, padx=(10, 0), pady=(10, 0))

        self.foodTab.rowconfigure([2, 3, 4], weight=1)
        self.foodTab.columnconfigure(1, weight=1)
        # Creates vertical and horizontal scrollbars, linking them to the treeview
        self.scrollbarFood = ttk.Scrollbar(self.foodTab, orient='vertical', command=self.foodTree.yview)
        self.scrollbarFood.grid(row=2, column=3, sticky='ns', rowspan=3, pady=10)
        self.foodTree.configure(yscrollcommand=self.scrollbarFood.set, selectmode='browse')
        self.xscrollbarFood = ttk.Scrollbar(self.foodTab, orient='horizontal', command=self.foodTree.xview)
        self.xscrollbarFood.grid(row=5, column=0, sticky='ew', columnspan=4, pady=(0, 10))
        self.foodTree.configure(xscrollcommand=self.xscrollbarFood.set, selectmode='browse')
        # Creates the add, edit and delete donation buttons, which call their respective functions when clicked
        self.giveFoodButton = ttk.Button(self.foodTab, text='Give Away Food', command=lambda: self.giveFood())
        self.addFoodButton = ttk.Button(self.foodTab, text='Add Donation', command=lambda: self.addFood())
        self.editFoodButton = ttk.Button(self.foodTab, text='Edit Donation', command=lambda: self.editFood())
        self.delFoodButton = ttk.Button(self.foodTab, text='Delete Donation', command=lambda: self.delFood())
        # Grids the add, edit and delete buttons to the frame
        self.giveFoodButton.grid(row=1, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.addFoodButton.grid(row=2, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.editFoodButton.grid(row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delFoodButton.grid(row=4, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        # Calls the function to load the records from the database
        loadDatabase(self.foodTree, 'foodDonatTbl', False)

        # Checks access level and disables relevant buttons
        accesslevel(2, self.addFoodButton, self.editFoodButton, self.giveFoodButton)
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
        app.enableMenu()

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
        records = executeSQL('SELECT * FROM foodDonatTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records found into the treeview
            self.foodTree.insert('', 0, values=(i[0], i[1], i[2], i[3], i[4], i[5], i[6]))

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
                self.donationWin = Toplevel(self.root)
                self.donationWin.lift(self.root)
                self.donationWin.title('Edit Food Donation')
                self.donationWin.iconbitmap(icon)
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
                self.giveFoodFrame = Frame(self.donationWin)
                self.giveFoodFrame.pack()
                # Creates all the labels and entry boxes for each field
                self.detailLabel = Label(self.giveFoodFrame, text='Give Away Food Details:', font='none 11 bold')
                self.foodIDLabel = Label(self.giveFoodFrame, text='FoodID:', font='none 11')
                self.foodIDInsert = Label(self.giveFoodFrame, text=foodID, font='none 11')
                self.nameLabel = Label(self.giveFoodFrame, text='Food Name:', font='none 11')
                self.nameInsert = Label(self.giveFoodFrame, text=name, font='none 11')
                self.recipientIDLabel = Label(self.giveFoodFrame, text='RecipientID:', font='none 11')
                # Creates a dropdown menu populated with all the recipientIDs that we retrieved earlier
                self.recipientIDVar = StringVar()
                # self.recipientIDVar.set('Anonymous')
                if recipientIDs:
                    self.recipientIDDropdown = ttk.OptionMenu(self.giveFoodFrame, self.recipientIDVar, 'Anonymous',
                                                              *recipientIDs,
                                                              command=lambda x: (self.recipientIDVar.set(
                                                                  self.recipientIDVar.get()[2:9])))
                else:
                    self.recipientIDDropdown = Label(self.giveFoodFrame, textvariable=self.recipientIDVar,
                                                     font='none 11')
                self.staffIDLabel = Label(self.giveFoodFrame, text='StaffID:', font='none 11')
                self.staffIDInsert = Label(self.giveFoodFrame, text=userID, font='none 11')
                # Creates text variable and error label to output any errors
                self.errorVar = StringVar()
                self.errorLabel = Label(self.giveFoodFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
                # Creates save button, which calls the function saveGiveFood when pressed
                self.saveButton = ttk.Button(self.giveFoodFrame, text='Save Record',
                                             command=lambda: self.saveGiveFood(foodID, name))
                # Grids all the labels, entry boxes, buttons and dropdowns to the frame
                self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
                self.foodIDLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
                self.foodIDInsert.grid(row=1, column=1, padx=(0, 10))
                self.nameLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
                self.nameInsert.grid(row=2, column=1, padx=(0, 10))
                self.recipientIDLabel.grid(row=3, column=0, sticky='E', padx=(10, 0))
                self.recipientIDDropdown.grid(row=3, column=1, padx=(0, 10), sticky='ew')
                self.staffIDLabel.grid(row=4, column=0, sticky='E', padx=(10, 0))
                self.staffIDInsert.grid(row=4, column=1, padx=(0, 10))
                self.errorLabel.grid(row=5, column=0, columnspan=2)
                self.saveButton.grid(row=6, column=0, columnspan=2, pady=(0, 10))

                # Runs the save function when the user presses the 'enter' button (same as saveButton)
                self.donationWin.bind('<Return>', lambda event: self.saveGiveFood(foodID, name))

                center(self.donationWin)

            else:
                messagebox.showerror('Error', 'Item already given away')

        else:
            # Outputs error message is no record has been selected
            messagebox.showerror('Error', 'No Record Selected')

    def saveGiveFood(self, foodID, name):
        recipientID = self.recipientIDVar.get()
        staffID = userID
        if messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nFoodID:\t\t' +
                                                  foodID + '\nName:\t\t' + name + '\nRecipientID:\t' + recipientID +
                                                  '\nStaffID:\t\t' + staffID):
            try:
                # Insert record into donationsTbl
                executeSQL('INSERT INTO giveFoodTbl VALUES (?,?,?)', (foodID, recipientID, staffID), False)
                executeSQL('UPDATE foodDonatTbl SET givenAway=? WHERE foodID = ?', (1, foodID), False)
                # Reloads records into treeview
                loadDatabase(self.foodTree, 'foodDonatTbl', False)
                # Destroys add donation window and returns to view donations window
                self.notebook.tab(0, state='normal')
                enableWindow(self.donationWin, self.giveFoodButton, self.returnButton, self.addFoodButton,
                             self.editFoodButton, self.delFoodButton)
                accesslevel(2, self.addFoodButton, self.editFoodButton, self.giveFoodButton)
                accesslevel(3, self.delFoodButton)
                messagebox.showinfo('Success!', 'Given Away')
            except sqlite3.IntegrityError:
                # Outputs error if donationID is not unique
                self.errorVar.set('Error: Failed To Update Database.\nPlease Try Again')

    def addFood(self):
        self.notebook.tab(0, state='disabled')
        disableWindow(self.returnButton, self.giveFoodButton, self.addFoodButton, self.editFoodButton,
                      self.delFoodButton)
        # Selects all donorIDs, forenames and surnames, and saves them to a list
        donors = executeSQL('SELECT donorID,donorForename,donorSurname FROM donorTbl', (), True)
        donorIDs = [(item[0:3]) for item in donors]
        self.donationWin = Toplevel(self.root)
        self.donationWin.lift(self.root)
        self.donationWin.title('Add Food Donation')
        self.donationWin.iconbitmap(icon)
        self.donationWin.protocol('WM_DELETE_WINDOW', lambda: (self.notebook.tab(0, state='normal'),
                                                               enableWindow(self.donationWin, self.giveFoodButton,
                                                                            self.returnButton,
                                                                            self.addFoodButton, self.editFoodButton,
                                                                            self.delFoodButton),
                                                               accesslevel(2, self.addFoodButton, self.editFoodButton,
                                                                           self.giveFoodButton),
                                                               accesslevel(3, self.delFoodButton)))
        self.addDonationFrame = Frame(self.donationWin)
        self.addDonationFrame.pack()
        # Creates all the labels and entry boxes for each field
        self.detailLabel = Label(self.addDonationFrame, text='Enter Donation Details:', font='none 11 bold')
        self.nameLabel = Label(self.addDonationFrame, text='Food Name:', font='none 11')
        self.nameVar = StringVar()
        self.nameBox = ttk.Entry(self.addDonationFrame, textvariable=self.nameVar)
        self.dateLabel = Label(self.addDonationFrame, text='Date:', font='none 11')
        self.dateVar = StringVar()
        # Creates a calendar widget to pick the date from
        self.calendar = DateEntry(self.addDonationFrame, state='readonly',
                                  date_pattern='DD/MM/YYYY', textvariable=self.dateVar,
                                  showweeknumbers=False, maxdate=datetime.today())
        self.expiryDateLabel = Label(self.addDonationFrame, text='Expiry Date:', font='none 11')
        self.expiryDateVar = StringVar()
        # Creates a calendar widget to pick the date from
        self.expiryCalendar = DateEntry(self.addDonationFrame, state='readonly',
                                        date_pattern='DD/MM/YYYY', textvariable=self.expiryDateVar,
                                        showweeknumbers=False, mindate=datetime.today())
        self.donorIDLabel = Label(self.addDonationFrame, text='DonorID:', font='none 11')
        # Creates a dropdown menu populated with all the donorIDs that we retrieved earlier
        self.donorIDVar = StringVar()
        # self.donorIDVar.set('Anonymous')
        if donorIDs:
            self.donorIDDropdown = ttk.OptionMenu(self.addDonationFrame, self.donorIDVar, 'Anonymous', *donorIDs,
                                                  command=lambda x: (self.donorIDVar.set(self.donorIDVar.get()[2:9])))
        else:
            self.donorIDDropdown = Label(self.addDonationFrame, textvariable=self.donorIDVar, font='none 11')
        # Creates text variable and error label to output any errors
        self.errorVar = StringVar()
        self.errorLabel = Label(self.addDonationFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
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
        self.donationWin.bind('<Return>', lambda event: self.saveFoodDonation())

        center(self.donationWin)

    def saveFoodDonation(self):
        # Retrieves all inputs from the form
        name = self.nameVar.get().title().strip()
        date = self.dateVar.get()
        expiryDate = self.expiryDateVar.get()
        donorID = self.donorIDVar.get()
        # Checks that all fields have been entered
        if name:
            staffID = userID
            foodID = 'FD' + str(''.join(['%s' % random.randint(0, 9) for num in range(0, 5)]))
            # Comfirmation box asks user to confirm that inputs are all correct
            if messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nFoodID:\t\t' +
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
                    accesslevel(2, self.addFoodButton, self.editFoodButton, self.giveFoodButton)
                    accesslevel(3, self.delFoodButton)
                    messagebox.showinfo('Success!', 'New Donation Saved')
                except sqlite3.IntegrityError:
                    # Outputs error if donationID is not unique
                    self.errorVar.set('Error: Failed To Update Database.\nPlease Try Again')
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
            donors = executeSQL('SELECT donorID,donorForename,donorSurname FROM donorTbl', (), True)
            donorIDs = [(item[0:3]) for item in donors]
            self.donationWin = Toplevel(self.root)
            self.donationWin.lift(self.root)
            self.donationWin.title('Edit Food Donation')
            self.donationWin.iconbitmap(icon)
            self.donationWin.protocol('WM_DELETE_WINDOW', lambda: (self.notebook.tab(0, state='normal'),
                                                                   enableWindow(self.donationWin, self.giveFoodButton,
                                                                                self.returnButton,
                                                                                self.addFoodButton, self.editFoodButton,
                                                                                self.delFoodButton),
                                                                   accesslevel(2, self.addFoodButton,
                                                                               self.editFoodButton,
                                                                               self.giveFoodButton),
                                                                   accesslevel(3, self.delFoodButton)))
            self.editDonationFrame = Frame(self.donationWin)
            self.editDonationFrame.pack()
            # Creates all the labels and entry boxes for each field
            self.detailLabel = Label(self.editDonationFrame, text='Edit Donation Details:', font='none 11 bold')
            self.foodIDLabel = Label(self.editDonationFrame, text='FoodID:', font='none 11')
            self.foodIDInsert = Label(self.editDonationFrame, text=foodID, font='none 11')
            self.nameLabel = Label(self.editDonationFrame, text='Food Name:', font='none 11')
            self.nameVar = StringVar()
            self.nameBox = ttk.Entry(self.editDonationFrame, textvariable=self.nameVar)
            self.dateLabel = Label(self.editDonationFrame, text='Date:', font='none 11')
            self.dateVar = StringVar()
            # Creates a calendar widget to pick the date from
            self.calendar = DateEntry(self.editDonationFrame, state='readonly',
                                      date_pattern='DD/MM/YYYY', textvariable=self.dateVar,
                                      showweeknumbers=False, maxdate=datetime.today())
            self.expiryDateLabel = Label(self.editDonationFrame, text='Expiry Date:', font='none 11')
            self.expiryDateVar = StringVar()
            # Creates a calendar widget to pick the date from
            self.expiryCalendar = DateEntry(self.editDonationFrame, state='readonly',
                                            date_pattern='DD/MM/YYYY', textvariable=self.expiryDateVar,
                                            showweeknumbers=False, mindate=datetime.today())
            self.donorIDLabel = Label(self.editDonationFrame, text='DonorID:', font='none 11')
            # Creates a dropdown menu populated with all the donorIDs that we retrieved earlier
            self.donorIDVar = StringVar()
            if donorIDs:
                self.donorIDDropdown = ttk.OptionMenu(self.editDonationFrame, self.donorIDVar, 'Anonymous', *donorIDs,
                                                      command=lambda x: (
                                                          self.donorIDVar.set(self.donorIDVar.get()[2:9])))
            else:
                self.donorIDDropdown = Label(self.editDonationFrame, textvariable=self.donorIDVar, font='none 11')
            self.staffIDLabel = Label(self.editDonationFrame, text='StaffID:', font='none 11')
            self.staffIDInsert = Label(self.editDonationFrame, text=staffID, font='none 11')
            # Creates text variable and error label to output any errors
            self.errorVar = StringVar()
            self.errorLabel = Label(self.editDonationFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
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
            self.expiryDateLabel.grid(row=4, column=0, sticky='E', padx=(10, 0))
            self.expiryCalendar.grid(row=4, column=1, padx=(0, 10), sticky='ew')
            self.donorIDLabel.grid(row=5, column=0, sticky='E', padx=(10, 0))
            self.donorIDDropdown.grid(row=5, column=1, padx=(0, 10), sticky='ew')
            self.staffIDLabel.grid(row=6, column=0, sticky='E', padx=(10, 0))
            self.staffIDInsert.grid(row=6, column=1, padx=(0, 10))
            self.errorLabel.grid(row=7, column=0, columnspan=2)
            self.saveButton.grid(row=8, column=0, columnspan=2, pady=(0, 10))

            self.nameBox.insert(INSERT, name)
            self.calendar.set_date(date)
            self.expiryCalendar.set_date(expiryDate)
            self.donorIDVar.set(donorID)
            # Runs the save function when the user presses the 'enter' button (same as saveButton)
            self.donationWin.bind('<Return>', lambda event: self.saveEditFoodDonation(foodID, staffID))

            center(self.donationWin)

        else:
            # Outputs error message is no record has been selected
            messagebox.showerror('Error', 'No Record Selected')

    def saveEditFoodDonation(self, foodID, staffID):
        # Retrieves all inputs from the form
        name = self.nameVar.get().title().strip()
        date = self.dateVar.get()
        expiryDate = self.expiryDateVar.get()
        donorID = self.donorIDVar.get()
        # Checks that all fields have been entered
        if name:
            # Comfirmation box asks user to confirm that inputs are all correct
            if messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nFoodID:\t\t' +
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
                    accesslevel(2, self.addFoodButton, self.editFoodButton, self.giveFoodButton)
                    accesslevel(3, self.delFoodButton)
                    messagebox.showinfo('Success!', 'Donation Updated')
                except sqlite3.IntegrityError:
                    # Outputs error if donationID is not unique
                    self.errorVar.set('Error: Failed To Update Database.\nPlease Try Again')
        else:
            # Outputs error if not all fields are filled
            self.errorVar.set('Error: Please Fill All Fields')

    def delFood(self):
        if self.foodTree.selection():
            # Retreives the donationID from the record selected in the treeview
            for selected_item in self.foodTree.selection():
                foodID = self.foodTree.set(selected_item, '#1')
            existsForeign = executeSQL('SELECT * FROM giveFoodTbl WHERE foodID = ?', (foodID,), False)
            if not existsForeign:
                # Asks the user for confimation that they want to permanently delete this record
                if messagebox.askokcancel('Delete', 'Are you sure you want to permanently delete this record?'):
                    # Removes the recird from foodDonatTbl
                    executeSQL('DELETE FROM foodDonatTbl WHERE foodID=?', (foodID,), False)
                    # Removes the record from the treeview
                    self.foodTree.delete(selected_item)
            else:
                messagebox.showerror('Error', 'Food Item Already Given Away')
        else:
            # Outputs error message is no record has been selected
            messagebox.showerror('Error', 'No Record Selected')

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
        records = executeSQL('SELECT * FROM donationsTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records found into the treeview
            self.tree.insert('', 0, values=(i[0], i[1], i[2], i[3], i[4], i[5], i[6]))

    def addDonation(self):
        self.notebook.tab(1, state='disabled')
        disableWindow(self.reportButton, self.returnButton, self.addDonationButton, self.editDonationButton,
                      self.delDonationButton)
        # Selects all donorIDs, forenames and surnames, and saves them to a list
        donors = executeSQL('SELECT donorID,donorForename,donorSurname FROM donorTbl', (), True)
        donorIDs = [(item[0:3]) for item in donors]
        if donorIDs:
            self.donationWin = Toplevel(self.root)
            self.donationWin.lift(self.root)
            self.donationWin.title('Add Donations')
            self.donationWin.iconbitmap(icon)
            self.donationWin.protocol('WM_DELETE_WINDOW', lambda: (self.notebook.tab(1, state='normal'),
                                                                   enableWindow(self.donationWin, self.reportButton,
                                                                                self.returnButton,
                                                                                self.addDonationButton,
                                                                                self.editDonationButton,
                                                                                self.delDonationButton),
                                                                   accesslevel(2, self.addDonationButton,
                                                                               self.editDonationButton),
                                                                   accesslevel(3, self.delDonationButton)))
            self.addDonationFrame = Frame(self.donationWin)
            self.addDonationFrame.pack()
            # Creates all the labels and entry boxes for each field
            self.detailLabel = Label(self.addDonationFrame, text='Enter Donation Details:', font='none 11 bold')
            self.amountLabel = Label(self.addDonationFrame, text='Amount:', font='none 11')
            self.amountVar = StringVar()
            self.amountBox = ttk.Entry(self.addDonationFrame, textvariable=self.amountVar)
            self.cashbankLabel = Label(self.addDonationFrame, text='Cash or Bank?', font='none 11')
            self.cashbankVar = IntVar()
            # Creates radio buttons, and gives them commands to show/hide the reference no. label and entry box
            self.cashRadio = ttk.Radiobutton(self.addDonationFrame, text='Cash', variable=self.cashbankVar, value=0,
                                             command=lambda: (self.referenceBox.delete(0, END),
                                                              self.referenceBox.config(state='readonly')))
            self.bankRadio = ttk.Radiobutton(self.addDonationFrame, text='Bank', variable=self.cashbankVar, value=1,
                                             command=lambda: (self.referenceBox.config(state='normal')))
            self.referenceLabel = Label(self.addDonationFrame, text='Reference No:', font='none 11')
            self.referenceVar = StringVar()
            self.referenceBox = ttk.Entry(self.addDonationFrame, textvariable=self.referenceVar)
            self.dateLabel = Label(self.addDonationFrame, text='Date:', font='none 11')
            self.dateVar = StringVar()
            # Creates a calendar widget to pick the date from
            self.calendar = DateEntry(self.addDonationFrame, state='readonly',
                                      date_pattern='DD/MM/YYYY', textvariable=self.dateVar,
                                      showweeknumbers=False, maxdate=datetime.today())
            self.donorIDLabel = Label(self.addDonationFrame, text='DonorID:', font='none 11')
            # Creates a dropdown menu populated with all the donorIDs that we retrieved earlier
            self.donorIDVar = StringVar()
            self.donorIDDropdown = ttk.OptionMenu(self.addDonationFrame, self.donorIDVar, 'Select...', *donorIDs,
                                                  command=lambda x: (self.donorIDVar.set(self.donorIDVar.get()[2:9])))
            # self.donorIDVar.set('Select...')
            self.staffIDLabel = Label(self.addDonationFrame, text='staffID:', font='none 11')
            self.staffIDEntered = Label(self.addDonationFrame, text=userID, font='none 11')
            # Creates text variable and error label to output any errors
            self.errorVar = StringVar()
            self.errorLabel = Label(self.addDonationFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
            # Creates save button, which calls the function saveDonation when pressed
            self.saveButton = ttk.Button(self.addDonationFrame, text='Save New Donation',
                                         command=lambda: self.saveDonation())
            # Grids all the labels, entry boxes, buttons and dropdowns to the frame
            self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
            self.amountLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
            self.amountBox.grid(row=1, column=1, padx=(0, 10))
            self.cashbankLabel.grid(row=2, column=0, rowspan=2, sticky='E', padx=(10, 0))
            self.cashRadio.grid(row=2, column=1)
            self.bankRadio.grid(row=3, column=1)
            self.referenceLabel.grid(row=4, column=0, sticky='E', padx=(10, 0)),
            self.referenceBox.grid(row=4, column=1, padx=(0, 10))
            self.referenceBox.config(state='readonly')
            self.dateLabel.grid(row=5, column=0, sticky='E', padx=(10, 0))
            self.calendar.grid(row=5, column=1, padx=(0, 10), sticky='ew')
            self.donorIDLabel.grid(row=6, column=0, sticky='E', padx=(10, 0))
            self.donorIDDropdown.grid(row=6, column=1, padx=(0, 10), sticky='ew')
            self.staffIDLabel.grid(row=7, column=0, sticky='E', padx=(10, 0))
            self.staffIDEntered.grid(row=7, column=1, padx=(0, 10))
            self.errorLabel.grid(row=8, column=0, columnspan=2)
            self.saveButton.grid(row=9, column=0, columnspan=2, pady=(0, 10))
            # Runs the save function when the user presses the 'enter' button (same as saveButton)
            self.donationWin.bind('<Return>', lambda event: self.saveDonation())

            center(self.donationWin)
        else:
            messagebox.showerror('Error', 'No donors registered')
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
            staffID = userID
            # Checks whether a reference no is required
            refneeded = True if cashorbankVar == 1 else False
            # Checks that reference no. is given if required
            refgood = True if (refneeded and referenceNo) or (not refneeded) else False
            if refgood and cashorbank and donorID != 'Select...':
                # Generates a random donationID, using the random module
                donationID = 'DN' + str(''.join(['%s' % random.randint(0, 9) for num in range(0, 5)]))
                # Comfirmation box asks user to confirm that inputs are all correct
                if messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nDonationID:\t' +
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
                        accesslevel(2, self.addDonationButton, self.editDonationButton)
                        accesslevel(3, self.delDonationButton)
                        messagebox.showinfo('Success!', 'New Donation Saved')
                    except sqlite3.IntegrityError:
                        # Outputs error if donationID is not unique
                        self.errorVar.set('Error: Failed To Update Database.\nPlease Try Again')
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
            donors = executeSQL('SELECT donorID,donorForename,donorSurname FROM donorTbl', (), True)
            donorIDs = [(item[0:3]) for item in donors]
            cashorbank = 0 if cashorbank == 'Cash' else 1
            self.donationWin = Toplevel(self.root)
            self.donationWin.title('Edit Donation')
            self.donationWin.iconbitmap(icon)
            self.donationWin.protocol('WM_DELETE_WINDOW', lambda: (self.notebook.tab(1, state='normal'),
                                                                   enableWindow(self.donationWin, self.reportButton,
                                                                                self.returnButton,
                                                                                self.addDonationButton,
                                                                                self.editDonationButton,
                                                                                self.delDonationButton),
                                                                   accesslevel(2, self.addDonationButton,
                                                                               self.editDonationButton),
                                                                   accesslevel(3, self.delDonationButton)))
            self.editDonationFrame = Frame(self.donationWin)
            self.editDonationFrame.pack()
            # Creates all the labels and entry boxes for each field
            self.detailLabel = Label(self.editDonationFrame, text='Edit Donation Details:', font='none 11 bold')
            self.donationIDLabel = Label(self.editDonationFrame, text='DonationID:', font='none 11')
            self.donationIDEntered = Label(self.editDonationFrame, text=donationID, font='none 11')
            self.amountLabel = Label(self.editDonationFrame, text='Amount:', font='none 11')
            self.amountVar = StringVar()
            self.amountBox = ttk.Entry(self.editDonationFrame, textvariable=self.amountVar)
            self.cashbankLabel = Label(self.editDonationFrame, text='Cash or Bank?', font='none 11')
            # Creates radio buttons, and gives them commands to show/hide the reference no. label and entry boxes
            # depending on which option is selected.
            self.cashbankVar = IntVar()
            self.cashRadio = ttk.Radiobutton(self.editDonationFrame, text='Cash', variable=self.cashbankVar, value=0,
                                             command=lambda: (self.referenceBox.delete(0, END),
                                                              self.referenceBox.config(state='readonly')))
            self.bankRadio = ttk.Radiobutton(self.editDonationFrame, text='Bank', variable=self.cashbankVar, value=1,
                                             command=lambda: (self.referenceBox.config(state='normal')))
            self.referenceLabel = Label(self.editDonationFrame, text='Reference No:', font='none 11')
            self.referenceVar = StringVar()
            self.referenceBox = ttk.Entry(self.editDonationFrame, textvariable=self.referenceVar)
            self.dateLabel = Label(self.editDonationFrame, text='Date:', font='none 11')
            self.dateVar = StringVar()
            # Creates a calendar widget to pick the date from
            self.calendar = DateEntry(self.editDonationFrame, state='readonly',
                                      date_pattern='DD/MM/YYYY', textvariable=self.dateVar,
                                      showweeknumbers=False, maxdate=datetime.today())
            self.donorIDLabel = Label(self.editDonationFrame, text='DonorID:', font='none 11')
            # Creates a dropdown menu populated with all the donorIDs that we retrieved earlier
            self.donorIDVar = StringVar()
            self.donorIDDropdown = ttk.OptionMenu(self.editDonationFrame, self.donorIDVar, 'Select...', *donorIDs,
                                                  command=lambda x: (self.donorIDVar.set(self.donorIDVar.get()[2:9])))
            # self.donorIDVar.set('Select...')
            self.staffIDLabel = Label(self.editDonationFrame, text='StaffID:', font='none 11')
            self.staffIDEntered = Label(self.editDonationFrame, text=staffID, font='none 11')
            # Creates a text variable and error label to output any errors to
            self.errorVar = StringVar()
            self.errorLabel = Label(self.editDonationFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
            # Creaets a save button, which calls the function saveEditDonation when pressed
            self.saveButton = ttk.Button(self.editDonationFrame, text='Update Donation',
                                         command=lambda: self.saveEditDonation(donationID, staffID))
            # Grids all the labels, entry boxes, buttons and dropdowns to the frame
            self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
            self.donationIDLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
            self.donationIDEntered.grid(row=1, column=1, padx=(0, 10))
            self.amountLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
            self.amountBox.grid(row=2, column=1, padx=(0, 10))
            self.cashbankLabel.grid(row=3, column=0, rowspan=2, sticky='E', padx=(10, 0))
            self.cashRadio.grid(row=3, column=1)
            self.bankRadio.grid(row=4, column=1)
            self.referenceLabel.grid(row=5, column=0, sticky='E', padx=(10, 0)),
            self.referenceBox.grid(row=5, column=1, padx=(0, 10))
            self.referenceBox.config(state='readonly')
            self.dateLabel.grid(row=6, column=0, sticky='E', padx=(10, 0))
            self.calendar.grid(row=6, column=1, padx=(0, 10), sticky='ew')
            self.donorIDLabel.grid(row=7, column=0, sticky='E', padx=(10, 0))
            self.donorIDDropdown.grid(row=7, column=1, padx=(0, 10), sticky='ew')
            self.staffIDLabel.grid(row=8, column=0, sticky='E', padx=(10, 0))
            self.staffIDEntered.grid(row=8, column=1, padx=(0, 10))
            self.errorLabel.grid(row=9, column=0, columnspan=2)
            self.saveButton.grid(row=10, column=0, columnspan=2, pady=(0, 10))
            # Inserts all the current values into the entry boxes
            self.amountBox.insert(INSERT, amount)
            self.cashbankVar.set(cashorbank)
            self.referenceVar.set(referenceNo)
            self.calendar.set_date(date)
            self.donorIDVar.set(donorID)
            # Grids the reference no. label and entry box if 'bank' is selected
            if cashorbank == 1:
                self.referenceBox.config(state='normal')
            # Runs the save function when the user presses the 'enter' key (same as saveButton)
            self.donationWin.bind('<Return>', lambda event: self.saveEditDonation(donationID, staffID))

            center(self.donationWin)

        else:
            # Outputs error message is no record has been selected
            messagebox.showerror('Error', 'No Record Selected')

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
            refgood = True if (refneeded and referenceNo) or (not refneeded) else False
            if refgood:
                # Confirmation box asks user to confirm that inputs are all correct
                if messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nDonationID:\t' +
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
                    accesslevel(2, self.addDonationButton, self.editDonationButton)
                    accesslevel(3, self.delDonationButton)
                    messagebox.showinfo('Success!', 'Donation Details Updated')
            else:
                # Outputs error if not all fields are filled
                self.errorVar.set('Error: Please Fill All Fields')

    def delDonation(self):
        if self.tree.selection():
            # Retreives the donationID from the record selected in the treeview
            for selected_item in self.tree.selection():
                donationID = self.tree.set(selected_item, '#1')
            # Asks the user for confimation that they want to permanently delete this record
            if messagebox.askokcancel('Delete', 'Are you sure you want to permanently delete this record?'):
                for selected_item in self.tree.selection():
                    # Removes the recird from donationsTbl
                    executeSQL('DELETE FROM donationsTbl WHERE donationID=?', (donationID,), False)
                    # Removes the record from the treeview
                    self.tree.delete(selected_item)
        else:
            # Outputs error message is no record has been selected
            messagebox.showerror('Error', 'No Record Selected')

    def report(self):
        self.notebook.tab(1, state='disabled')
        disableWindow(self.reportButton, self.returnButton, self.addDonationButton, self.editDonationButton,
                      self.delDonationButton)
        self.donationWin = Toplevel(self.root)
        self.donationWin.title('Donation Report')
        self.donationWin.iconbitmap(icon)
        self.donationWin.protocol('WM_DELETE_WINDOW', lambda: (self.notebook.tab(1, state='normal'),
                                                               enableWindow(self.donationWin, self.reportButton,
                                                                            self.returnButton,
                                                                            self.addDonationButton,
                                                                            self.editDonationButton,
                                                                            self.delDonationButton),
                                                               accesslevel(2, self.addDonationButton,
                                                                           self.editDonationButton),
                                                               accesslevel(3, self.delDonationButton)))
        self.donationReportFrame = Frame(self.donationWin)
        self.donationReportFrame.pack()
        # Creates labels and entry boxes for start/end date of report
        self.detailLabel = Label(self.donationReportFrame, text='Enter Report Parameters', font='none 11 bold')
        self.startDateLabel = Label(self.donationReportFrame, text='Start Date:', font='none 11')
        self.startDateVar = StringVar()
        self.startCalendar = DateEntry(self.donationReportFrame, state='readonly',
                                       date_pattern='DD/MM/YYYY', textvariable=self.startDateVar,
                                       showweeknumbers=False, maxdate=datetime.today())
        self.endDateLabel = Label(self.donationReportFrame, text='End Date:', font='none 11')
        self.endDateVar = StringVar()
        self.endCalendar = DateEntry(self.donationReportFrame, state='readonly',
                                     date_pattern='DD/MM/YYYY', textvariable=self.endDateVar,
                                     showweeknumbers=False, maxdate=datetime.today())
        # Creates a text variable and error label to output any errors to
        self.errorVar = StringVar()
        self.errorLabel = Label(self.donationReportFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
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
            self.startDate = datetime.strptime(self.startDateVar.get().strip(), '%d/%m/%Y')
            self.endDate = datetime.strptime(self.endDateVar.get().strip(), '%d/%m/%Y')
            # Clears any error messages
            self.errorVar.set('')
            disableWindow(self.enterButton)
            # Creates a new toplevel window to display the report
            self.donationReportWin = Toplevel(self.root)
            self.donationReportWin.title('Donation Report')
            self.donationReportWin.iconbitmap(icon)
            self.donationReportFrame = Frame(self.donationReportWin)
            self.donationReportFrame.pack(fill='both', expand=True)
            self.donationReportWin.protocol('WM_DELETE_WINDOW',
                                            lambda: enableWindow(self.donationReportWin, self.enterButton))
            self.titleLabel = Label(self.donationReportFrame, text='Kingfisher Trust', font='algerian 14 bold',
                                    fg='#2380b7')
            self.detailLabel = Label(self.donationReportFrame, text='Donation Report', font='none 12 bold')
            # Creates a label detailing the date constraints of the report, as input by the user
            self.datesLabel = Label(self.donationReportFrame,
                                    text='From ' + str(datetime.isoformat(self.startDate)[:10])
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
            columns = ('DonationID', 'Amount', 'Cash/Bank', 'Reference No', 'Date', 'DonorID', 'Donor Name', 'StaffID')
            self.reporttree = ttk.Treeview(self.donationReportFrame, columns=columns, show='headings',
                                           selectmode='none')
            for col in columns:
                self.reporttree.column(col, width=100, minwidth=100)
                self.reporttree.heading(col, text=col)
            self.reporttree.grid(row=4, column=0, sticky='ewns', columnspan=3, padx=(10, 0), pady=10)
            self.donationReportFrame.columnconfigure([0, 1, 2], weight=1)  # column with treeview
            self.donationReportFrame.rowconfigure(4, weight=1)  # row with treeview
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
                    record = i[0], i[1], i[2], i[3], i[4], i[5], (i[7] + ' ' + i[8]), i[6]
                    records.append(record)
                    self.reporttree.insert('', 0, values=record)
            # Creates a label with the total amount donated
            self.donatedLabel = Label(self.donationReportFrame,
                                      text=str('Total Donated = £{:.2f}'.format(self.totalDonat)))
            self.donatedLabel.grid(row=3, column=0, padx=10, sticky='w')

            self.scrollbar = ttk.Scrollbar(self.donationReportFrame, orient='vertical', command=self.reporttree.yview)
            self.scrollbar.grid(row=4, column=3, sticky='ns', pady=10, padx=(0, 10))
            self.reporttree.configure(yscrollcommand=self.scrollbar.set, selectmode='browse')

            center(self.donationReportWin)

        except ValueError:
            # Outputs an error if the dates input are invalid
            self.errorVar.set('Error: Invalid Input\nDD/MM/YYYY')


###########################################################################

################################## SUPPLIER WINDOW #################################################

class supplierWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('View Suppliers')
        self.root.iconbitmap(icon)
        self.frame = Frame(self.root)
        self.frame.pack(fill='both', expand=True)
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.closeWindow())
        # Creates title label, 'View Supplier Records'
        self.titleLabel = Label(self.frame, text='View Supplier Records', font='none 11')
        # Creates refresh button, to reload data from the database, and the return button, to close the supplier window
        # and return the user to the main menu
        self.refreshButton = ttk.Button(self.frame, text='↺',
                                        command=lambda: loadDatabase(self.tree, 'supplierTbl', True))
        self.returnButton = ttk.Button(self.frame, text='Main Menu', command=lambda: self.closeWindow())
        # Saves input search value from searchBox as searchVar
        self.searchVar = StringVar()
        self.searchBox = ttk.Entry(self.frame, textvariable=self.searchVar)
        # Creates a dropdown menu, with all the fields listed, set to supplierID by default
        self.searchFieldVar = StringVar()
        self.searchField = ttk.OptionMenu(self.frame, self.searchFieldVar, 'SupplierID', 'SupplierID', 'Name',
                                          'Contact')
        # Creates a 'Search' button, which calls the search function when pressed
        self.searchButton = ttk.Button(self.frame, text='Search', command=lambda: self.search())
        # Grids all the above labels, buttons and entry boxes to the frame
        self.titleLabel.grid(row=0, column=1, sticky='ns')
        self.refreshButton.grid(row=0, column=4, pady=10)
        self.returnButton.grid(row=0, column=0, pady=10, padx=10, ipadx=10, ipady=2, sticky='w')
        self.searchField.grid(row=1, column=0, padx=10, sticky='ew')
        self.searchBox.grid(row=1, column=1, sticky='ew')
        self.searchButton.grid(row=1, column=2, pady=10, padx=(10, 0), ipadx=10)
        # Creates the treeview, defining each column and naming its heading with the relevant field name
        columns = ('SupplierID', 'Name', 'Contact')
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        for col in columns:
            self.tree.column(col, width=100, minwidth=100)
            self.tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(self.tree, _col, False))
        self.tree.grid(row=2, column=0, sticky='ewns', rowspan=3, columnspan=3, padx=(10, 0), pady=(10, 0))
        self.frame.columnconfigure(1, weight=1)  # column with treeview
        self.frame.rowconfigure([2, 3, 4], weight=1)  # row with treeview
        # Creates vertical and horizontal scrollbars, linking them to the treeview
        self.scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=self.tree.yview)
        self.scrollbar.grid(row=2, column=3, sticky='ns', rowspan=3, pady=10)
        self.tree.configure(yscrollcommand=self.scrollbar.set, selectmode='browse')
        self.xscrollbar = ttk.Scrollbar(self.frame, orient='horizontal', command=self.tree.xview)
        self.xscrollbar.grid(row=5, column=0, sticky='ew', columnspan=4, pady=(0, 10))
        self.tree.configure(xscrollcommand=self.xscrollbar.set, selectmode='browse')
        # Creates the add, edit and delete supplier buttons, which calls their respective functions when clicked
        self.addSupplierButton = ttk.Button(self.frame, text='Add Supplier', command=lambda: self.addSupplier())
        self.editSupplierButton = ttk.Button(self.frame, text='Edit Supplier', command=lambda: self.editSupplier())
        self.delSupplierButton = ttk.Button(self.frame, text='Delete Supplier', command=lambda: self.delSupplier())
        # Grids the add, edit and delete supplier buttons to the frame
        self.addSupplierButton.grid(row=2, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.editSupplierButton.grid(row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delSupplierButton.grid(row=4, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
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
        app.enableMenu()

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
        records = executeSQL('SELECT * FROM supplierTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records found into the treeview
            self.tree.insert('', 0, values=(i[0], i[1], i[2]))

    def addSupplier(self):
        disableWindow(self.returnButton, self.addSupplierButton, self.editSupplierButton, self.delSupplierButton)
        self.supplierWin = Toplevel(self.root)
        self.supplierWin.title('Add Supplier')
        self.supplierWin.iconbitmap(icon)
        self.supplierWin.protocol('WM_DELETE_WINDOW',
                                  lambda: (enableWindow(self.supplierWin, self.returnButton, self.addSupplierButton,
                                                        self.editSupplierButton, self.delSupplierButton),
                                           accesslevel(2, self.addSupplierButton, self.editSupplierButton),
                                           accesslevel(3, self.delSupplierButton)))
        self.addSupplierFrame = Frame(self.supplierWin)
        self.addSupplierFrame.pack()
        # Creates all the labels and entry boxes for each field
        self.detailLabel = Label(self.addSupplierFrame, text='Enter Supplier Details:', font='none 11 bold')
        self.nameLabel = Label(self.addSupplierFrame, text='Name:', font='none 11')
        self.nameVar = StringVar()
        self.nameBox = ttk.Entry(self.addSupplierFrame, textvariable=self.nameVar)
        self.contactLabel = Label(self.addSupplierFrame, text='Contact:', font='none 11')
        self.contactVar = StringVar()
        self.contactBox = ttk.Entry(self.addSupplierFrame, textvariable=self.contactVar)
        # Creates text variable and error label to output any error messages
        self.errorVar = StringVar()
        self.errorLabel = Label(self.addSupplierFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
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
                supplierID = 'SU' + str(''.join(['%s' % random.randint(0, 9) for num in range(0, 5)]))
                # Asks for user confimation of the input details
                if messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nSupplierID:\t' + supplierID +
                                                          '\nName:\t\t' + name + '\nContact:\t\t' + contact):
                    try:
                        # Inserts record into supplierTbl
                        executeSQL('INSERT INTO supplierTbl VALUES (?,?,?)', (supplierID, name, contact), False)
                        loadDatabase(self.tree, 'supplierTbl', False)  # Reloads records into treeview
                        # Destroys add supplier toplevel and returns to view suppliers window
                        enableWindow(self.supplierWin, self.returnButton, self.addSupplierButton,
                                     self.editSupplierButton, self.delSupplierButton)
                        accesslevel(2, self.addSupplierButton, self.editSupplierButton)
                        accesslevel(3, self.delSupplierButton)
                        messagebox.showinfo('Success!', 'New Supplier Saved')
                    except sqlite3.IntegrityError:  # Outputs error message if supplierID is not unique
                        self.errorVar.set('Error: Failed To Update Database.\nPlease Try Again')
            else:
                self.errorVar.set('Error: Please Enter a\nValid Phone No. Or Email')
        else:  # Outputs error if not all fields are filled
            self.errorVar.set('Error: Please Fill All Fields')

    def editSupplier(self):
        if self.tree.selection():  # Runs IF a record is selected from treeview
            disableWindow(self.returnButton, self.addSupplierButton, self.editSupplierButton, self.delSupplierButton)
            for selected_item in self.tree.selection():
                # Finds record from database that matches selected record
                supplier = executeSQL('SELECT * FROM supplierTbl WHERE supplierID=?',
                                      (self.tree.set(selected_item, '#1'),), False)
                supplierID = supplier[0]
                name = supplier[1]
                contact = supplier[2]
            self.supplierWin = Toplevel(self.root)
            self.supplierWin.title('Edit Supplier')
            self.supplierWin.iconbitmap(icon)
            self.supplierWin.protocol('WM_DELETE_WINDOW',
                                      lambda: (enableWindow(self.supplierWin, self.returnButton, self.addSupplierButton,
                                                            self.editSupplierButton, self.delSupplierButton),
                                               accesslevel(2, self.addSupplierButton, self.editSupplierButton),
                                               accesslevel(3, self.delSupplierButton)))
            self.editSupplierFrame = Frame(self.supplierWin)
            self.editSupplierFrame.pack()
            # Creates all the labels and entry boxes where necessary for each field (no entry box for supplierID)
            self.detailLabel = Label(self.editSupplierFrame, text='Edit Supplier Details:', font='none 11 bold')
            self.supplierIDLabel = Label(self.editSupplierFrame, text='SupplierID:', font='none 11')
            self.supplierIDInsert = Label(self.editSupplierFrame, text=supplierID, font='none 11')
            self.nameLabel = Label(self.editSupplierFrame, text='Name:', font='none 11')
            self.nameVar = StringVar()
            self.nameBox = ttk.Entry(self.editSupplierFrame, textvariable=self.nameVar)
            self.contactLabel = Label(self.editSupplierFrame, text='Contact:', font='none 11')
            self.contactVar = StringVar()
            self.contactBox = ttk.Entry(self.editSupplierFrame, textvariable=self.contactVar)
            # Creates text variable and error label to output error messages to
            self.errorVar = StringVar()
            self.errorLabel = Label(self.editSupplierFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
            # Creates save button, which calls the function saveEditSupplier
            self.saveButton = ttk.Button(self.editSupplierFrame, text='Update Supplier',
                                         command=lambda: self.saveEditSupplier(supplierID))
            # Grids all the labels, entry boxes and buttons to the frame
            self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
            self.supplierIDLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
            self.supplierIDInsert.grid(row=1, column=1, padx=(0, 10))
            self.nameLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
            self.nameBox.grid(row=2, column=1, padx=(0, 10))
            self.contactLabel.grid(row=3, column=0, sticky='E', padx=(10, 0))
            self.contactBox.grid(row=3, column=1, padx=(0, 10))
            self.errorLabel.grid(row=4, column=0, columnspan=2)
            self.saveButton.grid(row=5, column=0, columnspan=2, pady=(0, 10))
            # Inserts the current fields into the entry boxes
            self.nameBox.insert(INSERT, name)
            self.contactBox.insert(INSERT, contact)
            # Runs the save function when the user presses the 'enter' button (same as saveButton)
            self.supplierWin.bind('<Return>', lambda event: self.saveEditSupplier(supplierID))

            center(self.supplierWin)

        else:  # Outputs error message if no record has been selected
            messagebox.showerror('Error', 'No Record Selected')

    def saveEditSupplier(self, supplierID):
        # Retrieves name, contact from form
        newName = self.nameVar.get().title().strip()
        newContact = self.contactVar.get().replace(' ', '')
        # Checks that all fields have been filled
        if newName and newContact:
            # Checks that contact is valid phoneNo OR email
            if validatePhone(newContact) or validateEmail(newContact):
                # Creates confirmation dialogue to confirm details are correct
                if messagebox.askyesno('Confirm Changes', 'Are these details correct?\n\nSupplierID:\t'
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
                    accesslevel(2, self.addSupplierButton, self.editSupplierButton)
                    accesslevel(3, self.delSupplierButton)
                    messagebox.showinfo('Success!', 'Supplier Details Updated')
            else:
                self.errorVar.set('Error: Please Enter a\nValid Phone No. Or Email')
        else:  # Outputs error if not all fields have been filled
            self.errorVar.set('Error: Please Fill All Fields')

    def delSupplier(self):
        if self.tree.selection():
            for selected_item in self.tree.selection():
                supplierID = self.tree.set(selected_item, '#1')
            # Searches through the table where the
            # supplierID might be stored as a foreign key
            existsForeign = executeSQL('SELECT * FROM itemTbl WHERE supplierID = ?', (supplierID,), False)
            # If supplierID is not stored in any other tables
            if not existsForeign:
                # Confirms that the user wants to permanently delete the record
                if messagebox.askokcancel('Delete', 'Are you sure you want to permanently delete this record?'):
                    for selected_item in self.tree.selection():
                        # Deletes the record from supplierTbl
                        executeSQL('DELETE FROM supplierTbl WHERE supplierID=?', (supplierID,), False)
                        # Removes the record from the treeview
                        self.tree.delete(selected_item)
            else:
                # If supplierID is a foreign key in other tables, output error as the record cannot be deleted
                messagebox.showerror('Error', 'Error: Record in use by other tables')
        else:  # Outputs error message if no record has been selected
            messagebox.showerror('Error', 'No Record Selected')


###########################################################################

################################## ITEM WINDOW #####################################################

class itemWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('View Items')
        self.root.iconbitmap(icon)
        self.frame = Frame(self.root)
        self.frame.pack(fill='both', expand=True)
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.closeWindow())
        # Creates title label, 'View Item Records'
        self.titleLabel = Label(self.frame, text='View Item Records', font='none 11')
        # Creates refresh button, to reload data from the database, and the return button, to close the item window
        # and return the user to the main menu
        self.refreshButton = ttk.Button(self.frame, text='↺', command=lambda: loadDatabase(self.tree, 'itemTbl', True))
        self.returnButton = ttk.Button(self.frame, text='Main Menu', command=lambda: self.closeWindow())
        # Saves input search value from searchBox as searchVar
        self.searchVar = StringVar()
        self.searchBox = ttk.Entry(self.frame, textvariable=self.searchVar)
        # Creates a dropdown menu, with all the fields listed to search, set to itemID by default
        self.searchFieldVar = StringVar()
        self.searchField = ttk.OptionMenu(self.frame, self.searchFieldVar, 'ItemID', 'ItemID', 'ItemName',
                                          'SalePrice', 'Quantity', 'SupplierCost', 'SupplierID')
        # Creates a 'search' button, which calls the search function when pressed
        self.searchButton = ttk.Button(self.frame, text='Search', command=lambda: self.search())
        # Grids all the above labels, buttons and entry boxes to the frame
        self.titleLabel.grid(row=0, column=1, sticky='ns')
        self.refreshButton.grid(row=0, column=4, pady=10)
        self.returnButton.grid(row=0, column=0, pady=10, padx=10, ipadx=10, ipady=2, sticky='w')
        self.searchField.grid(row=1, column=0, padx=10, sticky='ew')
        self.searchBox.grid(row=1, column=1, sticky='ew')
        self.searchButton.grid(row=1, column=2, pady=10, padx=(10, 0), ipadx=10)
        # Creates the treeview, defining each column and naming its heading with the relevant field name
        columns = ('ItemID', 'ItemName', 'SalePrice', 'Quantity', 'SupplierCost', 'SupplierID')
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        for col in columns:
            self.tree.column(col, width=100, minwidth=100)
            self.tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(self.tree, _col, False))
        self.tree.grid(row=2, column=0, sticky='ewns', rowspan=3, columnspan=3, padx=(10, 0), pady=(10, 0))
        self.frame.columnconfigure(1, weight=1)  # column with treeview
        self.frame.rowconfigure([2, 3, 4], weight=1)  # row with treeview
        # Creates vertical and horizontal scrollbars, linking them to the treeview
        self.scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=self.tree.yview)
        self.scrollbar.grid(row=2, column=3, sticky='ns', rowspan=3, pady=10)
        self.tree.configure(yscrollcommand=self.scrollbar.set, selectmode='browse')
        self.xscrollbar = ttk.Scrollbar(self.frame, orient='horizontal', command=self.tree.xview)
        self.xscrollbar.grid(row=5, column=0, sticky='ew', columnspan=4, pady=(0, 10))
        self.tree.configure(xscrollcommand=self.xscrollbar.set, selectmode='browse')
        # Creates the add, edit and delete item buttons, which call their respective functions when clicked
        self.addItemButton = ttk.Button(self.frame, text='Add Item', command=lambda: self.addItem())
        self.editItemButton = ttk.Button(self.frame, text='Edit Item', command=lambda: self.editItem())
        self.delItemButton = ttk.Button(self.frame, text='Delete Item', command=lambda: self.delItem())
        # Grids the add, edit and delete buttons to the frame
        self.addItemButton.grid(row=2, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.editItemButton.grid(row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delItemButton.grid(row=4, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
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
        app.enableMenu()

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
        records = executeSQL('SELECT * FROM itemTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records found into the treeview
            self.tree.insert('', 0, values=(i[0], i[1], i[2], i[3], i[4], i[5]))

    def addItem(self):
        disableWindow(self.returnButton, self.addItemButton, self.editItemButton, self.delItemButton)
        # Selects all supplierIDs and names, and saves them to a list
        suppliers = executeSQL('SELECT supplierID,supplierName FROM supplierTbl', (), True)
        supplierIDs = [(item[0:2]) for item in suppliers]
        if supplierIDs:
            self.itemWin = Toplevel(self.root)
            self.itemWin.title('Add Items')
            self.itemWin.iconbitmap(icon)
            self.itemWin.protocol('WM_DELETE_WINDOW',
                                  lambda: (enableWindow(self.itemWin, self.returnButton, self.addItemButton,
                                                        self.editItemButton, self.delItemButton),
                                           accesslevel(2, self.addItemButton, self.editItemButton),
                                           accesslevel(3, self.delItemButton)))
            self.addItemFrame = Frame(self.itemWin)
            self.addItemFrame.pack()
            # Creates all the labels and entry boxes for each field
            self.detailLabel = Label(self.addItemFrame, text='Enter Item Details:', font='none 11 bold')
            self.nameLabel = Label(self.addItemFrame, text='Item Name:', font='none 11')
            self.nameVar = StringVar()
            self.nameBox = ttk.Entry(self.addItemFrame, textvariable=self.nameVar)
            self.salePriceLabel = Label(self.addItemFrame, text='Sale Price:', font='none 11')
            self.salePriceVar = StringVar()
            self.salePriceBox = ttk.Entry(self.addItemFrame, textvariable=self.salePriceVar)
            self.quantityLabel = Label(self.addItemFrame, text='Quantity:', font='none 11')
            self.quantityVar = StringVar()
            self.quantityBox = ttk.Spinbox(self.addItemFrame, from_=0, to=999, textvariable=self.quantityVar)
            self.supplierCostLabel = Label(self.addItemFrame, text='Supplier Cost:', font='none 11')
            self.supplierCostVar = StringVar()
            self.supplierCostBox = ttk.Entry(self.addItemFrame, textvariable=self.supplierCostVar)
            self.supplierIDLabel = Label(self.addItemFrame, text='SupplierID:', font='none 11')
            # Creates a dropdown menu populated with all the donorIDs that we retrieved earlier
            self.supplierIDVar = StringVar()
            self.supplierIDDropdown = ttk.OptionMenu(self.addItemFrame, self.supplierIDVar, 'Select...', *supplierIDs,
                                                     command=lambda x: (
                                                         self.supplierIDVar.set(self.supplierIDVar.get()[2:9])))
            # self.supplierIDVar.set('Select...')
            # Creates text variable and error label to output any errors
            self.errorVar = StringVar()
            self.errorLabel = Label(self.addItemFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
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
            self.supplierCostLabel.grid(row=4, column=0, sticky='E', padx=(10, 0))
            self.supplierCostBox.grid(row=4, column=1, padx=(0, 10), sticky='ew')
            self.supplierIDLabel.grid(row=5, column=0, sticky='E', padx=(10, 0))
            self.supplierIDDropdown.grid(row=5, column=1, padx=(0, 10), sticky='ew')
            self.errorLabel.grid(row=6, column=0, columnspan=2)
            self.saveButton.grid(row=7, column=0, columnspan=2, pady=(0, 10))
            # Runs the save function when the user presses the 'enter' button (same as saveButton)
            self.itemWin.bind('<Return>', lambda event: self.saveItem())

            center(self.itemWin)
        else:
            messagebox.showerror('Error', 'No Suppliers Registered')
            self.closeWindow()

    def saveItem(self):
        # Retrieves all inputs from the form
        itemName = self.nameVar.get().strip().title()
        # Length limit prevents problems with displaying name in reports
        if len(itemName) < 17:
            supplierID = self.supplierIDVar.get()

            # checks if inputs entered are valid
            salePrice, salePriceValid = validateFloat(self.salePriceVar.get().strip())
            supplierCost, supplierCostValid = validateFloat(self.supplierCostVar.get().strip())
            quantity, quantityValid = validateInt(self.quantityVar.get().strip())

            if salePriceValid and supplierCostValid and quantityValid:
                # Checks that all fields have been entered
                if itemName and supplierID != 'Select...':
                    # Generates a random itemID, using the random module
                    itemID = 'IT' + str(''.join(['%s' % random.randint(0, 9) for num in range(0, 5)]))
                    # Comfirmation box asks user to confirm that inputs are all correct
                    if messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nItemID:\t\t' + itemID +
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
                            accesslevel(2, self.addItemButton, self.editItemButton)
                            accesslevel(3, self.delItemButton)
                            messagebox.showinfo('Success!', 'New Item Saved')
                        except sqlite3.IntegrityError:
                            # Outputs error if itemID is not unique
                            self.errorVar.set('Error: Failed To Update Database.\nPlease Try Again')
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
            disableWindow(self.returnButton, self.addItemButton, self.editItemButton, self.delItemButton)
            for selected_item in self.tree.selection():
                # Finds records from itemsTbl that match the selected record
                items = executeSQL('SELECT * FROM itemTbl WHERE itemID=?', (self.tree.set(selected_item, '#1'),), False)
                itemID = items[0]
                itemName = items[1]
                salePrice = items[2]
                quantity = items[3]
                supplierCost = items[4]
                supplierID = items[5]
            # Selects all supplierIDs and names, and saves them to a list
            suppliers = executeSQL('SELECT supplierID,supplierName FROM supplierTbl', (), True)
            supplierIDs = [(item[0:2]) for item in suppliers]
            if supplierIDs:
                self.itemWin = Toplevel(self.root)
                self.itemWin.title('Edit Items')
                self.itemWin.iconbitmap(icon)
                self.itemWin.protocol('WM_DELETE_WINDOW',
                                      lambda: (enableWindow(self.itemWin, self.returnButton, self.addItemButton,
                                                            self.editItemButton, self.delItemButton),
                                               accesslevel(2, self.addItemButton, self.editItemButton),
                                               accesslevel(3, self.delItemButton)))
                self.editItemFrame = Frame(self.itemWin)
                self.editItemFrame.pack()
                # Creates all the labels and entry boxes for each field
                self.detailLabel = Label(self.editItemFrame, text='Edit Item Details:', font='none 11 bold')
                self.itemIDLabel = Label(self.editItemFrame, text='ItemID:', font='none 11')
                self.itemIDInsert = Label(self.editItemFrame, text=itemID, font='none 11')
                self.nameLabel = Label(self.editItemFrame, text='Item Name:', font='none 11')
                self.nameVar = StringVar()
                self.nameBox = ttk.Entry(self.editItemFrame, textvariable=self.nameVar)
                self.salePriceLabel = Label(self.editItemFrame, text='Sale Price:', font='none 11')
                self.salePriceVar = StringVar()
                self.salePriceBox = ttk.Entry(self.editItemFrame, textvariable=self.salePriceVar)
                self.quantityLabel = Label(self.editItemFrame, text='Quantity:', font='none 11')
                self.quantityVar = StringVar()
                self.quantityBox = ttk.Spinbox(self.editItemFrame, from_=0, to=999, textvariable=self.quantityVar)
                self.supplierCostLabel = Label(self.editItemFrame, text='Supplier Cost:', font='none 11')
                self.supplierCostVar = StringVar()
                self.supplierCostBox = ttk.Entry(self.editItemFrame, textvariable=self.supplierCostVar)
                self.supplierIDLabel = Label(self.editItemFrame, text='SupplierID:', font='none 11')
                # Creates a dropdown menu populated with all the donorIDs that we retrieved earlier
                self.supplierIDVar = StringVar()
                self.supplierIDDropdown = ttk.OptionMenu(self.editItemFrame, self.supplierIDVar, 'Select...',
                                                         *supplierIDs,
                                                         command=lambda x: (
                                                             self.supplierIDVar.set(self.supplierIDVar.get()[2:9])))
                self.supplierIDVar.set('Select...')
                # Creates text variable and error label to output any errors
                self.errorVar = StringVar()
                self.errorLabel = Label(self.editItemFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
                # Creates save button, which calls the function saveItem when pressed
                self.saveButton = ttk.Button(self.editItemFrame, text='Update Item',
                                             command=lambda: self.saveEditItem(itemID))
                # Grids all the labels, entry boxes, buttons and dropdowns to the frame
                self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
                self.itemIDLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
                self.itemIDInsert.grid(row=1, column=1, padx=(0, 10))
                self.nameLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
                self.nameBox.grid(row=2, column=1, padx=(0, 10), sticky='ew')
                self.salePriceLabel.grid(row=3, column=0, sticky='E', padx=(10, 0))
                self.salePriceBox.grid(row=3, column=1, padx=(0, 10), sticky='ew')
                self.quantityLabel.grid(row=4, column=0, sticky='E', padx=(10, 0))
                self.quantityBox.grid(row=4, column=1, padx=(0, 10), sticky='ew')
                self.supplierCostLabel.grid(row=5, column=0, sticky='E', padx=(10, 0))
                self.supplierCostBox.grid(row=5, column=1, padx=(0, 10), sticky='ew')
                self.supplierIDLabel.grid(row=6, column=0, sticky='E', padx=(10, 0))
                self.supplierIDDropdown.grid(row=6, column=1, padx=(0, 10), sticky='ew')
                self.errorLabel.grid(row=7, column=0, columnspan=2)
                self.saveButton.grid(row=8, column=0, columnspan=2, pady=(0, 10))
                # Inserts all the current values into the entry boxes
                self.nameBox.insert(INSERT, itemName)
                self.salePriceBox.insert(INSERT, salePrice)
                self.quantityVar.set(quantity)
                self.supplierCostBox.insert(INSERT, supplierCost)
                self.supplierIDVar.set(supplierID)

                # Runs the save function when the user presses the 'enter' button (same as saveButton)
                self.itemWin.bind('<Return>', lambda event: self.saveEditItem(itemID))

                center(self.itemWin)
            else:
                messagebox.showerror('Error', 'No Suppliers Registered')
                self.closeWindow()

        else:
            # Outputs error message is no record has been selected
            messagebox.showerror('Error', 'No Record Selected')

    def saveEditItem(self, itemID):
        # Retrieves all inputs from the form
        itemName = self.nameVar.get().strip().title()
        # Length limit prevents problems with displaying name in reports
        if len(itemName) < 17:
            supplierID = self.supplierIDVar.get()

            # checks if values entered are a valid
            salePrice, saleValid = validateFloat(self.salePriceVar.get().strip())
            supplierCost, supplierValid = validateFloat(self.supplierCostVar.get().strip())
            quantity, quantityValid = validateInt(self.quantityVar.get().strip())

            if saleValid and supplierValid and quantityValid:
                # Checks that all fields have been entered
                if itemName and supplierID != 'Select...':
                    # Confirmation box asks user to confirm that inputs are all correct
                    if messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nItemID:\t\t' + itemID +
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
                        messagebox.showinfo('Success!', 'Item Details Updated')
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
            if messagebox.askokcancel('Delete', 'Are you sure you want to permanently delete this record?'):
                for selected_item in self.tree.selection():
                    # Removes the record from itemsTbl
                    executeSQL('DELETE FROM itemTbl WHERE itemID=?', (itemID,), False)
                    # Removes the record from the treeview
                    self.tree.delete(selected_item)
        else:
            # Outputs error message is no record has been selected
            messagebox.showerror('Error', 'No Record Selected')


###########################################################################

################################## ORDER WINDOW ####################################################

class orderWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('View Orders')
        self.root.iconbitmap(icon)
        self.frame = Frame(self.root)
        self.frame.pack(fill='both', expand=True)
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.closeWindow())
        # Creates title label, 'View Order Records'
        self.titleLabel = Label(self.frame, text='View Order Records', font='none 11')
        # Creates refresh button, to reload data from the database, and the return button, to close the order window
        # and return the user to the main menu
        self.refreshButton = ttk.Button(self.frame, text='↺', command=lambda: loadDatabase(self.tree, 'orderTbl', True))
        self.returnButton = ttk.Button(self.frame, text='Main Menu', command=lambda: self.closeWindow())
        # Saves input search value from searchBox as searchVar
        self.searchVar = StringVar()
        self.searchBox = ttk.Entry(self.frame, textvariable=self.searchVar)
        # Creates a dropdown menu, with all the fields listed to search, set to orderID by default
        self.searchFieldVar = StringVar()
        self.searchField = ttk.OptionMenu(self.frame, self.searchFieldVar, 'OrderNo', 'OrderNo', 'CustomerID',
                                          'OrderTotal', 'Date', 'StaffID')
        # Creates a 'search' button, which calls the search function when pressed
        self.searchButton = ttk.Button(self.frame, text='Search', command=lambda: self.search())
        self.customersButton = Label(self.frame, text='View Customers', fg='blue', cursor='hand2')
        self.customersButton.bind('<Button-1>', lambda x: self.customer())
        # Creates a 'Create report' button, which launches the report function
        self.reportButton = ttk.Button(self.frame, text='Create Report', command=lambda: self.report())
        # Grids all the above labels, buttons and entry boxes to the frame
        self.titleLabel.grid(row=0, column=1, sticky='ns')
        self.refreshButton.grid(row=0, column=4, pady=10)
        self.returnButton.grid(row=0, column=0, pady=10, padx=10, ipadx=10, ipady=2, sticky='w')
        self.searchField.grid(row=1, column=0, padx=10, sticky='ew')
        self.searchBox.grid(row=1, column=1, sticky='ew')
        self.searchButton.grid(row=1, column=2, pady=10, padx=(10, 0), ipadx=10)
        self.reportButton.grid(row=1, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.customersButton.grid(row=0, column=2)
        # Creates the treeview, defining each column and naming its heading with the relevant field name
        columns = ('OrderNo', 'CustomerID', 'OrderTotal', 'Date', 'StaffID')
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        for col in columns:
            self.tree.column(col, width=100, minwidth=100)
            self.tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(self.tree, _col, False))
        self.tree.grid(row=2, column=0, sticky='nesw', rowspan=3, columnspan=3, padx=(10, 0), pady=(10, 0))
        self.frame.columnconfigure(1, weight=1)  # column with treeview
        self.frame.rowconfigure([2, 3, 4], weight=1)  # row with treeview
        # Creates vertical and horizontal scrollbars, linking them to the treeview
        self.scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=self.tree.yview)
        self.scrollbar.grid(row=2, column=3, sticky='ns', rowspan=3, pady=10)
        self.tree.configure(yscrollcommand=self.scrollbar.set, selectmode='browse')
        self.xscrollbar = ttk.Scrollbar(self.frame, orient='horizontal', command=self.tree.xview)
        self.xscrollbar.grid(row=5, column=0, sticky='ew', columnspan=4, pady=(0, 10))
        self.tree.configure(xscrollcommand=self.xscrollbar.set, selectmode='browse')
        # Creates the add, edit and delete order buttons, which call their respective functions when clicked
        self.addOrderButton = ttk.Button(self.frame, text='Add Order', command=lambda: self.addOrder())
        self.editOrderButton = ttk.Button(self.frame, text='Edit Order', command=lambda: self.editOrder())
        self.delOrderButton = ttk.Button(self.frame, text='Delete Order', command=lambda: self.delOrder())
        # Grids the add, edit and delete buttons to the frame
        self.addOrderButton.grid(row=2, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.editOrderButton.grid(row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delOrderButton.grid(row=4, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
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
        customerWindow(Toplevel(self.root), self.root)

    def closeWindow(self):  # destroys Order window, opens main menu
        self.root.destroy()
        app.enableMenu()

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
        records = executeSQL('SELECT * FROM orderTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
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
        customers = executeSQL('SELECT customerID,customerForename,customerSurname FROM customerTbl', (), True)
        customerIDs = [(item[0:3]) for item in customers]
        self.orderWin = Toplevel(self.root)
        self.orderWin.lift(self.root)
        self.orderWin.title('Add Order')
        self.orderWin.iconbitmap(icon)
        self.orderWin.protocol('WM_DELETE_WINDOW',
                               lambda: (enableWindow(self.orderWin, self.reportButton, self.returnButton,
                                                     self.addOrderButton, self.editOrderButton, self.delOrderButton),
                                        accesslevel(2, self.addOrderButton, self.editOrderButton),
                                        accesslevel(3, self.delOrderButton)))
        self.addOrderFrame = Frame(self.orderWin)
        self.addOrderFrame.pack(side=LEFT, fill='y')
        # Creates all the labels and entry boxes for each field
        self.detailLabel = Label(self.addOrderFrame, text='Enter Order Details:', font='none 11 bold')
        self.customerIDLabel = Label(self.addOrderFrame, text='CustomerID:', font='none 11')
        # Creates a dropdown menu populated with all the customerIDs that we retrieved earlier
        self.customerIDVar = StringVar()
        if customerIDs:
            self.customerIDDropdown = ttk.OptionMenu(self.addOrderFrame, self.customerIDVar, 'Anonymous', *customerIDs,
                                                     command=lambda x: (
                                                         self.customerIDVar.set(self.customerIDVar.get()[2:9])))
        else:
            self.customerIDDropdown = Label(self.addOrderFrame, textvariable=self.customerIDVar, font='none 11')
        # self.customerIDVar.set('Anonymous')
        self.dateLabel = Label(self.addOrderFrame, text='Date:', font='none 11')
        self.dateVar = StringVar()
        # Creates a calendar widget to pick the date from
        self.calendar = DateEntry(self.addOrderFrame, state='readonly',
                                  date_pattern='DD/MM/YYYY', textvariable=self.dateVar,
                                  showweeknumbers=False, maxdate=datetime.today())

        # Creates canvas to put all items on
        self.canvas = Canvas(self.addOrderFrame)
        self.allItemsFrame = Frame(self.canvas)
        # Creates scrollbar for canvas
        self.canvasScroll = ttk.Scrollbar(self.addOrderFrame, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.canvasScroll.set, width=200, height=150)
        self.canvas.grid(row=3, column=0, columnspan=2, sticky='ns')
        self.canvasScroll.grid(row=3, column=3, sticky='ns')
        self.canvas.create_window((0, 0), window=self.allItemsFrame, anchor='nw')
        self.allItemsFrame.bind('<Configure>', lambda x: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

        self.addOrderFrame.columnconfigure(0, weight=1)  # column with canvas
        self.addOrderFrame.rowconfigure(3, weight=1)  # row with canvas

        self.totalVar = StringVar()
        self.totalVar.set('Total: £0.00')
        self.totalLabel = Label(self.addOrderFrame, textvariable=self.totalVar, font='none 11 bold')
        # Creates text variable and error label to output any errors
        self.errorVar = StringVar()
        self.errorLabel = Label(self.addOrderFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
        # Creates save button, which calls the function saveOrder when pressed
        self.saveButton = ttk.Button(self.addOrderFrame, text='Save New Order',
                                     command=lambda: self.saveOrder())
        # Grids all the labels, entry boxes, buttons and dropdowns to the frame
        self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
        self.customerIDLabel.grid(row=1, column=0, sticky='e', padx=(10, 0))
        self.customerIDDropdown.grid(row=1, column=1, padx=(0, 10), sticky='ew')
        self.dateLabel.grid(row=2, column=0, sticky='e', padx=(10, 0))
        self.calendar.grid(row=2, column=1, padx=(0, 10), sticky='ew')
        self.totalLabel.grid(row=4, column=0, columnspan=2)
        self.errorLabel.grid(row=5, column=0, columnspan=2)
        self.saveButton.grid(row=6, column=0, columnspan=2, pady=(0, 10))
        # Runs the save function when the user presses the 'enter' button (same as saveButton)
        self.orderWin.bind('<Return>', lambda event: self.saveOrder())

        self.seperator = ttk.Separator(self.orderWin, orient='vertical')
        self.seperator.pack(side=LEFT, fill=Y, padx=10)

        self.addItemFrame = Frame(self.orderWin)
        self.addItemFrame.pack(side=LEFT, fill='both', expand=True)
        self.label = Label(self.addItemFrame, text='Double click on an item to add it to the order')
        # Creates the treeview, defining each column and naming its heading with the relevant field name
        columns = ('ItemID', 'ItemName', 'SalePrice', 'Quantity')
        self.itemTree = ttk.Treeview(self.addItemFrame, columns=columns, show='headings')
        for col in columns:
            self.itemTree.column(col, width=100, minwidth=100)
            self.itemTree.heading(col, text=col)
        self.itemTree.grid(row=1, column=0, sticky='nesw', padx=(10, 0), pady=(10, 0))

        self.addItemFrame.columnconfigure(0, weight=1)  # column with treeview
        self.addItemFrame.rowconfigure(1, weight=1)  # row with treeview

        # Creates vertical and horizontal scrollbars, linking them to the treeview
        self.scrollbar = ttk.Scrollbar(self.addItemFrame, orient='vertical', command=self.itemTree.yview)
        self.scrollbar.grid(row=1, column=1, sticky='ns', pady=10, padx=(0, 10))
        self.itemTree.configure(yscrollcommand=self.scrollbar.set, selectmode='browse')
        self.xscrollbar = ttk.Scrollbar(self.addItemFrame, orient='horizontal', command=self.itemTree.xview)
        self.xscrollbar.grid(row=2, column=0, sticky='ew')
        self.itemTree.configure(xscrollcommand=self.xscrollbar.set, selectmode='browse')
        self.itemTree.bind('<Double-1>', lambda x: self.addItemToOrder())
        self.addedVar = StringVar()
        self.addedLabel = Label(self.addItemFrame, textvariable=self.addedVar, font='none 11 bold')
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
            itemNameLabel = Label(self.allItemsFrame, text=(itemID + ' ' + itemName), font='none 11', wraplength=125)
            priceLabel = Label(self.allItemsFrame, text=(str('£{:.2f}'.format(salePrice))), font='none 11')
            removeItemLabel = Label(self.allItemsFrame, text='x', fg='red', cursor='hand2')
            removeItemLabel.bind('<Button-1>',
                                 lambda x: self.removeItem(item, itemID, itemName, itemNameLabel, priceLabel,
                                                           removeItemLabel, salePrice))
            itemNameLabel.grid(row=self.count, column=0, sticky='W', padx=(10, 0))
            priceLabel.grid(row=self.count, column=1, sticky='E')
            removeItemLabel.grid(row=self.count, column=2, sticky='E', padx=(0, 10))
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
            orderNo = 'ON' + str(''.join(['%s' % random.randint(0, 9) for num in range(0, 5)]))
            # Comfirmation box asks user to confirm that inputs are all correct
            if messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nOrderNo:\t' +
                                                      orderNo + '\nCustomerID:\t' + customerID + '\nDate:\t\t' +
                                                      date + '\nStaffID\t\t' + userID + '\nItems:\t\t' +
                                                      '\n\t\t'.join(itemNames) +
                                                      '\nTotal:\t\t£' + str('{:.2f}'.format(self.total))):
                try:
                    itemSaved = []
                    # Insert record into orderTbl
                    executeSQL('INSERT INTO orderTbl VALUES (?,?,?,?,?)',
                               (orderNo, customerID, '{:.2f}'.format(self.total), date, userID), False)
                    for item in self.itemIDs:
                        oldQuantity = executeSQL('SELECT quantity FROM itemTbl WHERE itemID = ?', (item[0],), False)[0]
                        executeSQL('UPDATE itemTbl SET quantity = ? WHERE itemID = ?', (oldQuantity - 1, item[0]),
                                   False)
                        if item[0] not in itemSaved:
                            executeSQL('INSERT INTO orderItemTbl VALUES (?,?,?)', (orderNo, item[0], 1), False)
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
                    messagebox.showinfo('Success!', 'New Order Saved')
                except sqlite3.IntegrityError:
                    # Outputs error if orderID is not unique
                    self.errorVar.set('Error: Failed To Update Database.\nPlease Try Again')
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
            customers = executeSQL('SELECT customerID,customerForename,customerSurname FROM customerTbl', (), True)
            customerIDs = [(item[0:3]) for item in customers]
            self.orderWin = Toplevel(self.root)
            self.orderWin.title('Edit Order')
            self.orderWin.iconbitmap(icon)
            self.orderWin.protocol('WM_DELETE_WINDOW',
                                   lambda: (enableWindow(self.orderWin, self.reportButton, self.returnButton,
                                                         self.addOrderButton, self.editOrderButton,
                                                         self.delOrderButton),
                                            accesslevel(2, self.addOrderButton, self.editOrderButton),
                                            accesslevel(3, self.delOrderButton)))
            self.editOrderFrame = Frame(self.orderWin)
            self.editOrderFrame.pack(side=LEFT, fill='y')
            # Creates all the labels and entry boxes for each field
            self.detailLabel = Label(self.editOrderFrame, text='Edit Order Details:', font='none 11 bold')
            self.customerIDLabel = Label(self.editOrderFrame, text='CustomerID:', font='none 11')
            # Creates a dropdown menu populated with all the customerIDs that we retrieved earlier
            self.customerIDVar = StringVar()
            if customerIDs:
                self.customerIDDropdown = ttk.OptionMenu(self.editOrderFrame, self.customerIDVar, customerID,
                                                         *customerIDs,
                                                         command=lambda x: (
                                                             self.customerIDVar.set(self.customerIDVar.get()[2:9])))
            else:
                self.customerIDDropdown = Label(self.editOrderFrame, textvariable=self.customerIDVar, font='none 11')
            self.customerIDVar.set(customerID)
            self.dateLabel = Label(self.editOrderFrame, text='Date:', font='none 11')
            self.dateVar = StringVar()
            # Creates a calendar widget to pick the date from
            self.calendar = DateEntry(self.editOrderFrame, state='readonly',
                                      date_pattern='DD/MM/YYYY', textvariable=self.dateVar,
                                      showweeknumbers=False, maxdate=datetime.today())
            self.dateVar.set(date)

            self.canvas = Canvas(self.editOrderFrame)
            self.allItemsFrame = Frame(self.canvas)
            self.canvasScrolly = ttk.Scrollbar(self.editOrderFrame, orient='vertical', command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.canvasScrolly.set, width=200, height=150)
            self.canvas.grid(row=3, column=0, columnspan=2, sticky='ns')
            self.canvasScrolly.grid(row=3, column=3, sticky='ns')
            self.canvas.create_window((0, 0), window=self.allItemsFrame, anchor='nw')
            self.allItemsFrame.bind('<Configure>',
                                    lambda x: self.canvas.configure(scrollregion=self.canvas.bbox('all')))

            self.editOrderFrame.columnconfigure(0, weight=1)  # column with canvas
            self.editOrderFrame.rowconfigure(3, weight=1)  # row with canvas

            self.totalVar = StringVar()
            self.totalVar.set(str('Total: £{:.2f}'.format(self.total)))
            self.totalLabel = Label(self.editOrderFrame, textvariable=self.totalVar, font='none 11 bold')
            # Creates text variable and error label to output any errors
            self.errorVar = StringVar()
            self.errorLabel = Label(self.editOrderFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
            # Creates save button, which calls the function saveOrder when pressed
            self.saveButton = ttk.Button(self.editOrderFrame, text='Update Order',
                                         command=lambda: self.saveEditOrder(orderNo))
            # Grids all the labels, entry boxes, buttons and dropdowns to the frame
            self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
            self.customerIDLabel.grid(row=1, column=0, sticky='e', padx=(10, 0))
            self.customerIDDropdown.grid(row=1, column=1, padx=(0, 10), sticky='ew')
            self.dateLabel.grid(row=2, column=0, sticky='e', padx=(10, 0))
            self.calendar.grid(row=2, column=1, padx=(0, 10), sticky='ew')
            self.totalLabel.grid(row=4, column=0, columnspan=2)
            self.errorLabel.grid(row=5, column=0, columnspan=2)
            self.saveButton.grid(row=6, column=0, columnspan=2, pady=(0, 10))
            # Runs the save function when the user presses the 'enter' button (same as saveButton)
            self.orderWin.bind('<Return>', lambda event: self.saveEditOrder(orderNo))

            self.seperator = ttk.Separator(self.orderWin, orient='vertical')
            self.seperator.pack(side=LEFT, fill=Y, padx=10)

            self.addItemFrame = Frame(self.orderWin)
            self.addItemFrame.pack(side=LEFT, fill='both', expand=True)
            self.label = Label(self.addItemFrame, text='Double click on an item to add it to the order')
            # Creates the treeview, defining each column and naming its heading with the relevant field name
            columns = ('ItemID', 'ItemName', 'SalePrice', 'Quantity')
            self.itemTree = ttk.Treeview(self.addItemFrame, columns=columns, show='headings')
            for col in columns:
                self.itemTree.column(col, width=100, minwidth=100)
                self.itemTree.heading(col, text=col)
            self.itemTree.grid(row=1, column=0, sticky='nesw', padx=(10, 0), pady=(10, 0))

            self.addItemFrame.columnconfigure(0, weight=1)  # column with treeview
            self.addItemFrame.rowconfigure(1, weight=1)  # row with treeview

            # Creates vertical and horizontal scrollbars, linking them to the treeview
            self.scrollbar = ttk.Scrollbar(self.addItemFrame, orient='vertical', command=self.itemTree.yview)
            self.scrollbar.grid(row=1, column=1, sticky='ns', pady=10, padx=(0, 10))
            self.itemTree.configure(yscrollcommand=self.scrollbar.set, selectmode='browse')
            self.xscrollbar = ttk.Scrollbar(self.addItemFrame, orient='horizontal', command=self.itemTree.xview)
            self.xscrollbar.grid(row=2, column=0, sticky='ew')
            self.itemTree.configure(xscrollcommand=self.xscrollbar.set, selectmode='browse')
            self.itemTree.bind('<Double-1>', lambda x: self.addItemToOrder())
            self.addedVar = StringVar()
            self.addedLabel = Label(self.addItemFrame, textvariable=self.addedVar, font='none 11 bold')
            self.addedLabel.grid(row=3, column=0, sticky='s', pady=(0, 10))
            self.label.grid(row=0, column=0, sticky='n', pady=(10, 0))

            loadDatabase(self.itemTree, 'itemTbl', False)

            center(self.orderWin)

            itemIDQuantity = executeSQL('SELECT itemID,quantity FROM orderItemTbl WHERE orderNo = ?', (orderNo,), True)
            self.count = 0
            self.itemIDs = []
            for item in itemIDQuantity:
                items = executeSQL('SELECT * FROM itemTbl WHERE itemID = ?', (item[0],), False)
                for x in range(item[1]):
                    listOfEntriesInTreeView = self.itemTree.get_children()
                    for row in listOfEntriesInTreeView:
                        if self.itemTree.set(row, '#1') == items[0]:
                            selected = row

                    self.addOldItemsToOrder(items, selected)
            self.originalItems = list(self.itemIDs)

        else:
            # Outputs error message is no record has been selected
            messagebox.showerror('Error', 'No Record Selected')

    def addOldItemsToOrder(self, items, item):
        # Goes through all items in original order, adding them to the list of all items and prices in the order,
        # as well as creating labels and buttons to remove it from the order
        itemID = items[0]
        itemName = items[1]
        salePrice = items[2]
        self.count += 1
        self.itemIDs.append([itemID, itemName])

        itemNameLabel = Label(self.allItemsFrame, text=(itemID + ' ' + itemName), font='none 11', wraplength=125)
        priceLabel = Label(self.allItemsFrame, text=(str('£{:.2f}'.format(salePrice))), font='none 11')
        removeItemLabel = Label(self.allItemsFrame, text='x', fg='red', cursor='hand2')
        removeItemLabel.bind('<Button-1>', lambda x: self.removeItem(item, itemID, itemName, itemNameLabel, priceLabel,
                                                                     removeItemLabel, salePrice))
        itemNameLabel.grid(row=self.count, column=0, sticky='W', padx=(10, 0))
        priceLabel.grid(row=self.count, column=1, sticky='E')
        removeItemLabel.grid(row=self.count, column=2, sticky='E', padx=(0, 10))

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
            if messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nOrderNo:\t' +
                                                      orderNo + '\nCustomerID:\t' + customerID + '\nDate:\t\t' +
                                                      date + '\nStaffID\t\t' + userID + '\nItems:\t\t' +
                                                      '\n\t\t'.join(itemNames) +
                                                      '\nTotal:\t\t£' + str('{:.2f}'.format(self.total))):
                try:
                    # Update record in orderTbl
                    executeSQL('UPDATE orderTbl SET customerID = ?, orderTotal = ?, date = ? WHERE orderNo = ?',
                               (customerID, '{:.2f}'.format(self.total), date, orderNo), False)
                    executeSQL('DELETE FROM orderItemTbl WHERE orderNo=?', (orderNo,), False)
                    for item in removedItems:
                        oldQuantity = executeSQL('SELECT quantity FROM itemTbl WHERE itemID = ?', (item[0],), False)[0]
                        executeSQL('UPDATE itemTbl SET quantity = ? WHERE itemID = ?', (oldQuantity + 1, item[0]),
                                   False)
                    for item in newItems:
                        oldQuantity = executeSQL('SELECT quantity FROM itemTbl WHERE itemID = ?', (item[0],), False)[0]
                        executeSQL('UPDATE itemTbl SET quantity = ? WHERE itemID = ?', (oldQuantity - 1, item[0]),
                                   False)
                    itemSaved = []
                    for item in self.itemIDs:
                        if item[0] not in itemSaved:
                            executeSQL('INSERT INTO orderItemTbl VALUES (?,?,?)', (orderNo, item[0], 1), False)
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
                    messagebox.showinfo('Success!', 'Order Updated')
                except sqlite3.IntegrityError:
                    # Outputs error if orderID is not unique
                    self.errorVar.set('Error: Failed To Update Database.\nPlease Try Again')
        else:
            # Outputs error if not all fields are filled
            self.errorVar.set('Error: No Items in Order')

    def delOrder(self):
        if self.tree.selection():
            # Retrieves the orderID from the record selected in the treeview
            for selected_item in self.tree.selection():
                orderNo = self.tree.set(selected_item, '#1')
            # Asks the user for confimation that they want to permanently delete this record
            if messagebox.askokcancel('Delete', '''Are you sure you want to permanently delete this record?
                                        \nNote: This will increase the quantity of items in stock'''):
                for selected_item in self.tree.selection():
                    # Removes the record from orderTbl
                    executeSQL('DELETE FROM orderTbl WHERE orderNo=?', (orderNo,), False)
                    items = executeSQL('SELECT itemID,quantity FROM orderItemTbl WHERE orderNo = ?', (orderNo,), True)
                    for item in items:
                        oldQuantity = executeSQL('SELECT quantity FROM itemTbl WHERE itemID = ?', (item[0],), False)[0]
                        executeSQL('UPDATE itemTbl SET quantity = ? WHERE itemID = ?', (oldQuantity + item[1], item[0]),
                                   False)
                    executeSQL('DELETE FROM orderItemTbl WHERE orderNo=?', (orderNo,), False)
                    # Removes the record from the treeview
                    self.tree.delete(selected_item)
        else:
            # Outputs error message is no record has been selected
            messagebox.showerror('Error', 'No Record Selected')

    def report(self):
        disableWindow(self.reportButton, self.returnButton, self.addOrderButton, self.editOrderButton,
                      self.delOrderButton)
        self.orderWin = Toplevel(self.root)
        self.orderWin.title('Order Report')
        self.orderWin.iconbitmap(icon)
        self.orderWin.protocol('WM_DELETE_WINDOW',
                               lambda: (enableWindow(self.orderWin, self.reportButton, self.returnButton,
                                                     self.addOrderButton, self.editOrderButton, self.delOrderButton),
                                        accesslevel(2, self.addOrderButton, self.editOrderButton),
                                        accesslevel(3, self.delOrderButton)))
        self.orderReportFrame = Frame(self.orderWin)
        self.orderReportFrame.pack()
        # Creates labels and entry boxes for start/end date of report
        self.detailLabel = Label(self.orderReportFrame, text='Enter Report Parameters', font='none 11 bold')
        self.startDateLabel = Label(self.orderReportFrame, text='Start Date:', font='none 11')
        self.startDateVar = StringVar()
        self.startCalendar = DateEntry(self.orderReportFrame, state='readonly',
                                       date_pattern='DD/MM/YYYY', textvariable=self.startDateVar,
                                       showweeknumbers=False, maxdate=datetime.today())
        self.endDateLabel = Label(self.orderReportFrame, text='End Date:', font='none 11')
        self.endDateVar = StringVar()
        self.endCalendar = DateEntry(self.orderReportFrame, state='readonly',
                                     date_pattern='DD/MM/YYYY', textvariable=self.endDateVar,
                                     showweeknumbers=False, maxdate=datetime.today())
        # Creates a text variable and error label to output any errors to
        self.errorVar = StringVar()
        self.errorLabel = Label(self.orderReportFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
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
            self.startDate = datetime.strptime(self.startDateVar.get().strip(), '%d/%m/%Y')
            self.endDate = datetime.strptime(self.endDateVar.get().strip(), '%d/%m/%Y')
            # Clears any error messages
            self.errorVar.set('')
            disableWindow(self.enterButton)
            # Creates a new toplevel window to display the report
            self.orderReportWin = Toplevel(self.orderWin)
            self.orderReportWin.title('Revenue Report')
            self.orderReportWin.iconbitmap(icon)
            self.orderReportFrame = Frame(self.orderReportWin)
            self.orderReportFrame.pack(fill='both', expand=True)
            self.orderReportWin.protocol('WM_DELETE_WINDOW',
                                         lambda: enableWindow(self.orderReportWin, self.enterButton))
            self.titleLabel = Label(self.orderReportFrame, text='Kingfisher Trust', font='algerian 14 bold',
                                    fg='#2380b7')
            self.detailLabel = Label(self.orderReportFrame, text='Revenue Report', font='none 12 bold')
            # Creates a label detailing the date constraints of the report, as input by the user
            self.datesLabel = Label(self.orderReportFrame, text='From ' + str(datetime.isoformat(self.startDate)[:10])
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
            self.reporttree = ttk.Treeview(self.orderReportFrame, columns=columns, show='headings', selectmode='none')
            for col in columns:
                self.reporttree.column(col, width=100, minwidth=100)
                self.reporttree.heading(col, text=col)
            self.reporttree.grid(row=6, column=0, sticky='nesw', columnspan=3, padx=(10, 0), pady=10)
            self.orderReportFrame.columnconfigure([0, 1, 2], weight=1)  # column with treeview
            self.orderReportFrame.rowconfigure(6, weight=1)  # row with treeview
            # Connects to database and selects all records from orderTbl
            self.orders = executeSQL('SELECT * FROM orderTbl', (), True)
            self.totalCost = 0
            self.totalRevenue = 0
            records = []
            # Iterates through all the orders, selecting all relevant fields for orders within the
            # given time period
            for order in self.orders:
                count = 0
                orderItems = executeSQL('SELECT * FROM orderItemTbl WHERE orderNo = ?', (order[0],), True)
                date = order[3]
                if self.startDate <= datetime.strptime(date, '%d/%m/%Y') <= self.endDate:
                    for orderItem in orderItems:
                        items = executeSQL('SELECT * FROM itemTbl WHERE itemID = ?', (orderItem[1],), False)

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

            self.scrollbar = ttk.Scrollbar(self.orderReportFrame, orient='vertical', command=self.reporttree.yview)
            self.scrollbar.grid(row=6, column=3, sticky='ns', pady=10, padx=(0, 10))
            self.reporttree.configure(yscrollcommand=self.scrollbar.set, selectmode='browse')

            self.totalCostLabel = Label(self.orderReportFrame, text=str('Total Cost = £{:.2f}'.format(self.totalCost)))
            self.totalRevenueLabel = Label(self.orderReportFrame,
                                           text=str('Total Revenue = £{:.2f}'.format(self.totalRevenue)))
            self.totalProfitLabel = Label(self.orderReportFrame,
                                          text=str('Total Profit = £{:.2f}'.format(self.totalProfit)))
            self.totalCostLabel.grid(row=3, column=0, padx=10, sticky='w')
            self.totalRevenueLabel.grid(row=4, column=0, padx=10, sticky='w')
            self.totalProfitLabel.grid(row=5, column=0, padx=10, sticky='w')

            center(self.orderReportWin)

        except ValueError:
            # Outputs an error if the dates input are invalid
            self.errorVar.set('Error: Invalid Input\nDD/MM/YYYY')


###########################################################################

################################## CUSTOMER WINDOW #################################################

class customerWindow:
    def __init__(self, root, parent):
        self.root = root
        self.root.title('View Customers')
        self.root.iconbitmap(icon)
        self.frame = Frame(self.root)
        self.frame.pack(fill='both', expand=True)
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.closeWindow(parent))
        # Creates title label, 'View Customer Records'
        self.titleLabel = Label(self.frame, text='View Customer Records', font='none 11')
        # Creates refresh button, to reload data from the database, and the return button, to close the customer window
        # and return the user to the main menu
        self.refreshButton = ttk.Button(self.frame, text='↺',
                                        command=lambda: loadDatabase(self.tree, 'customerTbl', True))
        self.returnButton = ttk.Button(self.frame, text='Return to Orders', command=lambda: self.closeWindow(parent))
        # Saves input search value from searchBox as searchVar
        self.searchVar = StringVar()
        self.searchBox = ttk.Entry(self.frame, textvariable=self.searchVar)
        # Creates a dropdown menu, with all the fields listed, set to customerID by default
        self.searchFieldVar = StringVar()
        self.searchField = ttk.OptionMenu(self.frame, self.searchFieldVar, 'CustomerID', 'CustomerID', 'Surname',
                                          'Forename', 'Contact')
        # Creates a 'Search' button, which calls the search function when pressed
        self.searchButton = ttk.Button(self.frame, text='Search', command=lambda: self.search())
        # Grids all the above labels, buttons and entry boxes to the frame
        self.titleLabel.grid(row=0, column=1, sticky='ns')
        self.refreshButton.grid(row=0, column=4, pady=10)
        self.returnButton.grid(row=0, column=0, pady=10, padx=10, ipadx=10, ipady=2, sticky='w')
        self.searchField.grid(row=1, column=0, padx=10, sticky='ew')
        self.searchBox.grid(row=1, column=1, sticky='ew')
        self.searchButton.grid(row=1, column=2, pady=10, padx=(10, 0), ipadx=10)
        # Creates the treeview, defining each column and naming its heading with the relevant field name
        columns = ('CustomerID', 'Surname', 'Forename', 'Contact')
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        for col in columns:
            self.tree.column(col, width=100, minwidth=100)
            self.tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(self.tree, _col, False))
        self.tree.grid(row=2, column=0, sticky='nesw', rowspan=3, columnspan=3, padx=(10, 0), pady=(10, 0))
        self.frame.columnconfigure(1, weight=1)  # column with treeview
        self.frame.rowconfigure([2, 3, 4], weight=1)  # row with treeview
        # Creates vertical and horizontal scrollbars, linking them to the treeview
        self.scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=self.tree.yview)
        self.scrollbar.grid(row=2, column=3, sticky='ns', rowspan=3, pady=10)
        self.tree.configure(yscrollcommand=self.scrollbar.set, selectmode='browse')
        self.xscrollbar = ttk.Scrollbar(self.frame, orient='horizontal', command=self.tree.xview)
        self.xscrollbar.grid(row=5, column=0, sticky='ew', columnspan=4, pady=(0, 10))
        self.tree.configure(xscrollcommand=self.xscrollbar.set, selectmode='browse')
        # Creates the add, edit and delete customer buttons, which calls their respective functions when clicked
        self.addCustomerButton = ttk.Button(self.frame, text='Add Customer', command=lambda: self.addCustomer())
        self.editCustomerButton = ttk.Button(self.frame, text='Edit Customer', command=lambda: self.editCustomer())
        self.delCustomerButton = ttk.Button(self.frame, text='Delete Customer', command=lambda: self.delCustomer())
        # Grids the add, edit and delete customer buttons to the frame
        self.addCustomerButton.grid(row=2, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.editCustomerButton.grid(row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delCustomerButton.grid(row=4, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
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
        records = executeSQL('SELECT * FROM customerTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records found into the treeview
            self.tree.insert('', 0, values=(i[0], i[1], i[2], i[3]))

    def addCustomer(self):
        disableWindow(self.returnButton, self.addCustomerButton, self.editCustomerButton, self.delCustomerButton)
        self.customerWin = Toplevel(self.root)
        self.customerWin.title('Add Customer')
        self.customerWin.iconbitmap(icon)
        self.customerWin.protocol('WM_DELETE_WINDOW',
                                  lambda: (enableWindow(self.customerWin, self.returnButton, self.addCustomerButton,
                                                        self.editCustomerButton, self.delCustomerButton),
                                           accesslevel(2, self.addCustomerButton, self.editCustomerButton),
                                           accesslevel(3, self.delCustomerButton)))
        self.addCustomerFrame = Frame(self.customerWin)
        self.addCustomerFrame.pack()
        # Creates all the labels and entry boxes for each field
        self.detailLabel = Label(self.addCustomerFrame, text='Enter Customer Details:', font='none 11 bold')
        self.forenameLabel = Label(self.addCustomerFrame, text='Forename:', font='none 11')
        self.forenameVar = StringVar()
        self.forenameBox = ttk.Entry(self.addCustomerFrame, textvariable=self.forenameVar)
        self.surnameLabel = Label(self.addCustomerFrame, text='Surname:', font='none 11')
        self.surnameVar = StringVar()
        self.surnameBox = ttk.Entry(self.addCustomerFrame, textvariable=self.surnameVar)
        self.contactLabel = Label(self.addCustomerFrame, text='Contact:', font='none 11')
        self.contactVar = StringVar()
        self.contactBox = ttk.Entry(self.addCustomerFrame, textvariable=self.contactVar)
        # Creates text variable and error label to output any error messages
        self.errorVar = StringVar()
        self.errorLabel = Label(self.addCustomerFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
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
                customerID = 'CU' + str(''.join(['%s' % random.randint(0, 9) for num in range(0, 5)]))
                # Asks for user confimation of the input details
                if messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nCustomerID:\t' + customerID +
                                                          '\nName:\t\t' + forename + ' ' + surname +
                                                          '\nContact:\t\t' + contact):
                    try:
                        # Inserts record into customerTbl
                        executeSQL('INSERT INTO customerTbl VALUES (?,?,?,?)', (customerID, surname, forename, contact),
                                   False)
                        loadDatabase(self.tree, 'customerTbl', False)  # Reloads records into treeview
                        # Destroys add customer toplevel and returns to view customers window
                        enableWindow(self.customerWin, self.returnButton, self.addCustomerButton,
                                     self.editCustomerButton, self.delCustomerButton)
                        accesslevel(2, self.addCustomerButton, self.editCustomerButton)
                        accesslevel(3, self.delCustomerButton)
                        messagebox.showinfo('Success!', 'New Customer Saved')
                    except sqlite3.IntegrityError:  # Outputs error message if customerID is not unique
                        self.errorVar.set('Error: Failed To Update Database.\nPlease Try Again')
            else:
                self.errorVar.set('Error: Please Enter a\nValid Phone No. Or Email')
        else:  # Outputs error if not all fields are filled
            self.errorVar.set('Error: Please Fill All Fields')

    def editCustomer(self):
        if self.tree.selection():  # Runs IF a record is selected from treeview
            disableWindow(self.returnButton, self.addCustomerButton, self.editCustomerButton, self.delCustomerButton)
            for selected_item in self.tree.selection():
                # Finds record from database that matches selected record
                customer = executeSQL('SELECT * FROM customerTbl WHERE customerID=?',
                                      (self.tree.set(selected_item, '#1'),), False)
                customerID = customer[0]
                forename = customer[1]
                surname = customer[2]
                contact = customer[3]
            self.customerWin = Toplevel(self.root)
            self.customerWin.title('Edit Customer')
            self.customerWin.iconbitmap(icon)
            self.customerWin.protocol('WM_DELETE_WINDOW',
                                      lambda: (enableWindow(self.customerWin, self.returnButton, self.addCustomerButton,
                                                            self.editCustomerButton, self.delCustomerButton),
                                               accesslevel(2, self.addCustomerButton, self.editCustomerButton),
                                               accesslevel(3, self.delCustomerButton)))
            self.editCustomerFrame = Frame(self.customerWin)
            self.editCustomerFrame.pack()
            # Creates all the labels and entry boxes where necessary for each field (no entry box for customerID)
            self.detailLabel = Label(self.editCustomerFrame, text='Edit Customer Details:', font='none 11 bold')
            self.customerIDLabel = Label(self.editCustomerFrame, text='CustomerID:', font='none 11')
            self.customerIDInsert = Label(self.editCustomerFrame, text=customerID, font='none 11')
            self.forenameLabel = Label(self.editCustomerFrame, text='Forename:', font='none 11')
            self.forenameVar = StringVar()
            self.forenameBox = ttk.Entry(self.editCustomerFrame, textvariable=self.forenameVar)
            self.surnameLabel = Label(self.editCustomerFrame, text='Surname:', font='none 11')
            self.surnameVar = StringVar()
            self.surnameBox = ttk.Entry(self.editCustomerFrame, textvariable=self.surnameVar)
            self.contactLabel = Label(self.editCustomerFrame, text='Contact:', font='none 11')
            self.contactVar = StringVar()
            self.contactBox = ttk.Entry(self.editCustomerFrame, textvariable=self.contactVar)
            # Creates text variable and error label to output error messages to
            self.errorVar = StringVar()
            self.errorLabel = Label(self.editCustomerFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
            # Creates save button, which calls the function saveEditCustomer
            self.saveButton = ttk.Button(self.editCustomerFrame, text='Update Customer',
                                         command=lambda: self.saveEditCustomer(customerID))
            # Grids all the labels, entry boxes and buttons to the frame
            self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
            self.customerIDLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
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
            self.forenameBox.insert(INSERT, forename)
            self.surnameBox.insert(INSERT, surname)
            self.contactBox.insert(INSERT, contact)
            # Runs the save function when the user presses the 'enter' button (same as saveButton)
            self.customerWin.bind('<Return>', lambda event: self.saveEditCustomer(customerID))

            center(self.customerWin)

        else:  # Outputs error message if no record has been selected
            messagebox.showerror('Error', 'No Record Selected')

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
                if messagebox.askyesno('Confirm Changes', 'Are these details correct?\n\nCustomerID:\t'
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
                    accesslevel(2, self.addCustomerButton, self.editCustomerButton)
                    accesslevel(3, self.delCustomerButton)
                    messagebox.showinfo('Success!', 'Customer Details Updated')
            else:
                self.errorVar.set('Error: Please Enter a\nValid Phone No. Or Email')
        else:  # Outputs error if not all fields have been filled
            self.errorVar.set('Error: Please Fill All Fields')

    def delCustomer(self):
        if self.tree.selection():
            for selected_item in self.tree.selection():
                customerID = self.tree.set(selected_item, '#1')
            # Searches through the table where the
            # customerID might be stored as a foreign key
            existsForeign = executeSQL('SELECT * FROM orderTbl WHERE customerID = ?', (customerID,), False)
            # If customerID is not stored in any other tables
            if not existsForeign:
                # Confirms that the user wants to permanently delete the record
                if messagebox.askokcancel('Delete', 'Are you sure you want to permanently delete this record?'):
                    for selected_item in self.tree.selection():
                        # Deletes the record from customerTbl
                        executeSQL('DELETE FROM customerTbl WHERE customerID=?', (customerID,), False)
                        # Removes the record from the treeview
                        self.tree.delete(selected_item)
            else:
                # If customerID is a foreign key in other tables, output error as the record cannot be deleted
                messagebox.showerror('Error', 'Error: Record in use by other tables')
        else:  # Outputs error message if no record has been selected
            messagebox.showerror('Error', 'No Record Selected')


###########################################################################

################################## RECIPIENT WINDOW ################################################

class recipientWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('View Recipients')
        self.root.iconbitmap(icon)
        self.frame = Frame(self.root)
        self.frame.pack(fill='both', expand=True)
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.closeWindow())
        # Creates title label, 'View Recipient Records'
        self.titleLabel = Label(self.frame, text='View Recipient Records', font='none 11')
        # Creates refresh button, to reload data from the database, and the return button, to close the recipient window
        # and return the user to the main menu
        self.refreshButton = ttk.Button(self.frame, text='↺',
                                        command=lambda: loadDatabase(self.tree, 'recipientTbl', True))
        self.returnButton = ttk.Button(self.frame, text='Main Menu', command=lambda: self.closeWindow())
        # Saves input search value from searchBox as searchVar
        self.searchVar = StringVar()
        self.searchBox = ttk.Entry(self.frame, textvariable=self.searchVar)
        # Creates a dropdown menu, with all the fields listed, set to recipientID by default
        self.searchFieldVar = StringVar()
        self.searchField = ttk.OptionMenu(self.frame, self.searchFieldVar, 'RecipientID', 'RecipientID', 'Surname',
                                          'Forename', 'Contact')
        # Creates a 'Search' button, which calls the search function when pressed
        self.searchButton = ttk.Button(self.frame, text='Search', command=lambda: self.search())
        # Grids all the above labels, buttons and entry boxes to the frame
        self.titleLabel.grid(row=0, column=1, sticky='ns')
        self.refreshButton.grid(row=0, column=4, pady=10)
        self.returnButton.grid(row=0, column=0, pady=10, padx=10, ipadx=10, ipady=2, sticky='w')
        self.searchField.grid(row=1, column=0, padx=10, sticky='ew')
        self.searchBox.grid(row=1, column=1, sticky='ew')
        self.searchButton.grid(row=1, column=2, pady=10, padx=(10, 0), ipadx=10)
        # Creates the treeview, defining each column and naming its heading with the relevant field name
        columns = ('RecipientID', 'Surname', 'Forename', 'Contact')
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        for col in columns:
            self.tree.column(col, width=100, minwidth=100)
            self.tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(self.tree, _col, False))
        self.tree.grid(row=2, column=0, sticky='nesw', rowspan=3, columnspan=3, padx=(10, 0), pady=(10, 0))
        self.frame.columnconfigure(1, weight=1)  # column with treeview
        self.frame.rowconfigure([2, 3, 4], weight=1)  # row with treeview
        # Creates vertical and horizontal scrollbars, linking them to the treeview
        self.scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=self.tree.yview)
        self.scrollbar.grid(row=2, column=3, sticky='ns', rowspan=3, pady=10)
        self.tree.configure(yscrollcommand=self.scrollbar.set, selectmode='browse')
        self.xscrollbar = ttk.Scrollbar(self.frame, orient='horizontal', command=self.tree.xview)
        self.xscrollbar.grid(row=5, column=0, sticky='ew', columnspan=4, pady=(0, 10))
        self.tree.configure(xscrollcommand=self.xscrollbar.set, selectmode='browse')
        # Creates the add, edit and delete recipient buttons, which calls their respective functions when clicked
        self.addRecipientButton = ttk.Button(self.frame, text='Add Recipient', command=lambda: self.addRecipient())
        self.editRecipientButton = ttk.Button(self.frame, text='Edit Recipient', command=lambda: self.editRecipient())
        self.delRecipientButton = ttk.Button(self.frame, text='Delete Recipient', command=lambda: self.delRecipient())
        # Grids the add, edit and delete recipient buttons to the frame
        self.addRecipientButton.grid(row=2, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.editRecipientButton.grid(row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delRecipientButton.grid(row=4, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
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
        app.enableMenu()

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
        records = executeSQL('SELECT * FROM recipientTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records found into the treeview
            self.tree.insert('', 0, values=(i[0], i[1], i[2], i[3]))

    def addRecipient(self):
        disableWindow(self.returnButton, self.addRecipientButton, self.editRecipientButton, self.delRecipientButton)
        self.recipientWin = Toplevel(self.root)
        self.recipientWin.title('Add Recipient')
        self.recipientWin.iconbitmap(icon)
        self.recipientWin.protocol('WM_DELETE_WINDOW',
                                   lambda: (enableWindow(self.recipientWin, self.returnButton, self.addRecipientButton,
                                                         self.editRecipientButton, self.delRecipientButton),
                                            accesslevel(2, self.addRecipientButton, self.editRecipientButton),
                                            accesslevel(3, self.delRecipientButton)))
        self.addRecipientFrame = Frame(self.recipientWin)
        self.addRecipientFrame.pack()
        # Creates all the labels and entry boxes for each field
        self.detailLabel = Label(self.addRecipientFrame, text='Enter Recipient Details:', font='none 11 bold')
        self.forenameLabel = Label(self.addRecipientFrame, text='Forename:', font='none 11')
        self.forenameVar = StringVar()
        self.forenameBox = ttk.Entry(self.addRecipientFrame, textvariable=self.forenameVar)
        self.surnameLabel = Label(self.addRecipientFrame, text='Surname:', font='none 11')
        self.surnameVar = StringVar()
        self.surnameBox = ttk.Entry(self.addRecipientFrame, textvariable=self.surnameVar)
        self.contactLabel = Label(self.addRecipientFrame, text='Contact:', font='none 11')
        self.contactVar = StringVar()
        self.contactBox = ttk.Entry(self.addRecipientFrame, textvariable=self.contactVar)
        # Creates text variable and error label to output any error messages
        self.errorVar = StringVar()
        self.errorLabel = Label(self.addRecipientFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
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
            recipientID = 'RE' + str(''.join(['%s' % random.randint(0, 9) for num in range(0, 5)]))
            # Asks for user confimation of the input details
            if messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nRecipientID:\t' + recipientID +
                                                      '\nName:\t\t' + forename + ' ' + surname +
                                                      '\nContact:\t\t' + contact):
                try:
                    # Inserts record into recipientTbl
                    executeSQL('INSERT INTO recipientTbl VALUES (?,?,?,?)', (recipientID, surname, forename, contact),
                               False)
                    loadDatabase(self.tree, 'recipientTbl', False)  # Reloads records into treeview
                    # Destroys add recipient toplevel and returns to view recipients window
                    enableWindow(self.recipientWin, self.returnButton, self.addRecipientButton,
                                 self.editRecipientButton, self.delRecipientButton)
                    accesslevel(2, self.addRecipientButton, self.editRecipientButton)
                    accesslevel(3, self.delRecipientButton)
                    messagebox.showinfo('Success!', 'New Recipient Saved')
                except sqlite3.IntegrityError:  # Outputs error message if recipientID is not unique
                    self.errorVar.set('Error: Failed To Update Database.\nPlease Try Again')
        else:  # Outputs error if not all fields are filled
            self.errorVar.set('Error: Please Fill Forename Field')

    def editRecipient(self):
        if self.tree.selection():  # Runs IF a record is selected from treeview
            disableWindow(self.returnButton, self.addRecipientButton, self.editRecipientButton, self.delRecipientButton)
            for selected_item in self.tree.selection():
                # Finds record from database that matches selected record
                recipient = executeSQL('SELECT * FROM recipientTbl WHERE recipientID=?',
                                       (self.tree.set(selected_item, '#1'),), False)
                recipientID = recipient[0]
                surname = recipient[1]
                forename = recipient[2]
                contact = recipient[3]
            self.recipientWin = Toplevel(self.root)
            self.recipientWin.title('Edit Recipient')
            self.recipientWin.iconbitmap(icon)
            self.recipientWin.protocol('WM_DELETE_WINDOW', lambda: (
                enableWindow(self.recipientWin, self.returnButton, self.addRecipientButton,
                             self.editRecipientButton, self.delRecipientButton),
                accesslevel(2, self.addRecipientButton, self.editRecipientButton),
                accesslevel(3, self.delRecipientButton)))
            self.editRecipientFrame = Frame(self.recipientWin)
            self.editRecipientFrame.pack()
            # Creates all the labels and entry boxes where necessary for each field (no entry box for recipientID)
            self.detailLabel = Label(self.editRecipientFrame, text='Edit Recipient Details:', font='none 11 bold')
            self.recipientIDLabel = Label(self.editRecipientFrame, text='RecipientID:', font='none 11')
            self.recipientIDInsert = Label(self.editRecipientFrame, text=recipientID, font='none 11')
            self.forenameLabel = Label(self.editRecipientFrame, text='Forename:', font='none 11')
            self.forenameVar = StringVar()
            self.forenameBox = ttk.Entry(self.editRecipientFrame, textvariable=self.forenameVar)
            self.surnameLabel = Label(self.editRecipientFrame, text='Surname:', font='none 11')
            self.surnameVar = StringVar()
            self.surnameBox = ttk.Entry(self.editRecipientFrame, textvariable=self.surnameVar)
            self.contactLabel = Label(self.editRecipientFrame, text='Contact:', font='none 11')
            self.contactVar = StringVar()
            self.contactBox = ttk.Entry(self.editRecipientFrame, textvariable=self.contactVar)
            # Creates text variable and error label to output error messages to
            self.errorVar = StringVar()
            self.errorLabel = Label(self.editRecipientFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
            # Creates save button, which calls the function saveEditRecipient
            self.saveButton = ttk.Button(self.editRecipientFrame, text='Update Recipient',
                                         command=lambda: self.saveEditRecipient(recipientID))
            # Grids all the labels, entry boxes and buttons to the frame
            self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
            self.recipientIDLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
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
            self.forenameBox.insert(INSERT, forename)
            self.surnameBox.insert(INSERT, surname)
            self.contactBox.insert(INSERT, contact)
            # Runs the save function when the user presses the 'enter' button (same as saveButton)
            self.recipientWin.bind('<Return>', lambda event: self.saveEditRecipient(recipientID))

            center(self.recipientWin)

        else:  # Outputs error message if no record has been selected
            messagebox.showerror('Error', 'No Record Selected')

    def saveEditRecipient(self, recipientID):
        # Retrieves forename, surname, contact from form
        newForename = self.forenameVar.get().title().strip()
        newSurname = self.surnameVar.get().title().strip()
        newContact = self.contactVar.get().replace(' ', '')
        # Checks that all fields have been filled
        if newForename:
            # Creates confirmation dialogue to confirm details are correct
            if messagebox.askyesno('Confirm Changes', 'Are these details correct?\n\nRecipientID:\t'
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
                accesslevel(2, self.addRecipientButton, self.editRecipientButton)
                accesslevel(3, self.delRecipientButton)
                messagebox.showinfo('Success!', 'Recipient Details Updated')
        else:  # Outputs error if not all fields have been filled
            self.errorVar.set('Error: Please Fill Forename Field')

    def delRecipient(self):
        if self.tree.selection():
            for selected_item in self.tree.selection():
                recipientID = self.tree.set(selected_item, '#1')
            # Searches through the table where the
            # recipientID might be stored as a foreign key
            existsForeign = executeSQL('SELECT * FROM giveFoodTbl WHERE recipientID = ?', (recipientID,), False)
            # If recipientID is not stored in any other tables
            if not existsForeign:
                # Confirms that the user wants to permanently delete the record
                if messagebox.askokcancel('Delete', 'Are you sure you want to permanently delete this record?'):
                    for selected_item in self.tree.selection():
                        # Deletes the record from recipientTbl
                        executeSQL('DELETE FROM recipientTbl WHERE recipientID=?', (recipientID,), False)
                        # Removes the record from the treeview
                        self.tree.delete(selected_item)
            else:
                # If recipientID is a foreign key in other tables, output error as the record cannot be deleted
                messagebox.showerror('Error', 'Error: Record in use by other tables')
        else:  # Outputs error message if no record has been selected
            messagebox.showerror('Error', 'No Record Selected')


###########################################################################

################################## EXPENDITURE WINDOW ##############################################

class expenditureWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('View Expenditures')
        self.root.iconbitmap(icon)
        self.frame = Frame(self.root)
        self.frame.pack(fill='both', expand=True)
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.closeWindow())
        # Creates title label, 'View Expenditure Records'
        self.titleLabel = Label(self.frame, text='View Expenditure Records', font='none 11')
        # Creates refresh button, to reload data from the database, and the return button,
        # to close the expenditure window and return the user to the main menu
        self.refreshButton = ttk.Button(self.frame, text='↺',
                                        command=lambda: loadDatabase(self.tree, 'expenditureTbl', True))
        self.returnButton = ttk.Button(self.frame, text='Main Menu', command=lambda: self.closeWindow())
        # Saves input search value from searchBox as searchVar
        self.searchVar = StringVar()
        self.searchBox = ttk.Entry(self.frame, textvariable=self.searchVar)
        # Creates a dropdown menu, with all the fields listed, set to expenditureID by default
        self.searchFieldVar = StringVar()
        self.searchField = ttk.OptionMenu(self.frame, self.searchFieldVar, 'ExpenditureID', 'ExpenditureID', 'Amount',
                                          'Details', 'Date', 'StaffID')
        # Creates a 'Search' button, which calls the search function when pressed
        self.searchButton = ttk.Button(self.frame, text='Search', command=lambda: self.search())
        # Creates a 'Create report' button, which launches the report function
        self.reportButton = ttk.Button(self.frame, text='Create Report', command=lambda: self.report())
        # Grids all the above labels, buttons and entry boxes to the frame
        self.titleLabel.grid(row=0, column=1, sticky='ns')
        self.refreshButton.grid(row=0, column=4, pady=10)
        self.returnButton.grid(row=0, column=0, pady=10, padx=10, ipadx=10, ipady=2, sticky='w')
        self.searchField.grid(row=1, column=0, padx=10, sticky='ew')
        self.searchBox.grid(row=1, column=1, sticky='ew')
        self.searchButton.grid(row=1, column=2, pady=10, padx=(10, 0), ipadx=10)
        self.reportButton.grid(row=1, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        # Creates the treeview, defining each column and naming its heading with the relevant field name
        columns = ('ExpenditureID', 'Amount', 'Details', 'Date', 'StaffID')
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        for col in columns:
            self.tree.column(col, width=100, minwidth=100)
            self.tree.heading(col, text=col, command=lambda _col=col: treeview_sort_column(self.tree, _col, False))
        self.tree.grid(row=2, column=0, sticky='nesw', rowspan=3, columnspan=3, padx=(10, 0), pady=(10, 0))
        self.frame.columnconfigure(1, weight=1)  # column with treeview
        self.frame.rowconfigure([2, 3, 4], weight=1)  # row with treeview
        # Creates vertical and horizontal scrollbars, linking them to the treeview
        self.scrollbar = ttk.Scrollbar(self.frame, orient='vertical', command=self.tree.yview)
        self.scrollbar.grid(row=2, column=3, sticky='ns', rowspan=3, pady=10)
        self.tree.configure(yscrollcommand=self.scrollbar.set, selectmode='browse')
        self.xscrollbar = ttk.Scrollbar(self.frame, orient='horizontal', command=self.tree.xview)
        self.xscrollbar.grid(row=5, column=0, sticky='ew', columnspan=4, pady=(0, 10))
        self.tree.configure(xscrollcommand=self.xscrollbar.set, selectmode='browse')
        # Creates the add, edit and delete expenditure buttons, which calls their respective functions when clicked
        self.addExpenditureButton = ttk.Button(self.frame, text='Add Expenditure',
                                               command=lambda: self.addExpenditure())
        self.editExpenditureButton = ttk.Button(self.frame, text='Edit Expenditure',
                                                command=lambda: self.editExpenditure())
        self.delExpenditureButton = ttk.Button(self.frame, text='Delete Expenditure',
                                               command=lambda: self.delExpenditure())
        # Grids the add, edit and delete expenditure buttons to the frame
        self.addExpenditureButton.grid(row=2, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.editExpenditureButton.grid(row=3, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
        self.delExpenditureButton.grid(row=4, column=4, padx=10, ipadx=10, ipady=2, sticky='ew')
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
        app.enableMenu()

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
        records = executeSQL('SELECT * FROM expenditureTbl WHERE upper(%s) LIKE (?)' % searchField, (search,), True)
        for i in records:
            # Inserts all the records found into the treeview
            self.tree.insert('', 0, values=(i[0], i[1], i[2], i[3], i[4]))

    def addExpenditure(self):
        disableWindow(self.returnButton, self.addExpenditureButton, self.editExpenditureButton,
                      self.delExpenditureButton)
        self.expenditureWin = Toplevel(self.root)
        self.expenditureWin.title('Add Expenditure')
        self.expenditureWin.iconbitmap(icon)
        self.expenditureWin.protocol('WM_DELETE_WINDOW', lambda: (
            enableWindow(self.expenditureWin, self.returnButton, self.addExpenditureButton,
                         self.editExpenditureButton, self.delExpenditureButton),
            accesslevel(2, self.addExpenditureButton, self.editExpenditureButton),
            accesslevel(3, self.delExpenditureButton)))
        self.addExpenditureFrame = Frame(self.expenditureWin)
        self.addExpenditureFrame.pack()
        # Creates all the labels and entry boxes for each field
        self.detailLabel = Label(self.addExpenditureFrame, text='Enter Expenditure Details:', font='none 11 bold')
        self.amountLabel = Label(self.addExpenditureFrame, text='Amount:', font='none 11')
        self.amountVar = StringVar()
        self.amountBox = ttk.Entry(self.addExpenditureFrame, textvariable=self.amountVar)
        self.detailsLabel = Label(self.addExpenditureFrame, text='Details:', font='none 11')
        self.detailsBox = Text(self.addExpenditureFrame, width=15, height=5)
        self.dateLabel = Label(self.addExpenditureFrame, text='Date:', font='none 11')
        self.dateVar = StringVar()
        # Creates a calendar widget to pick the date from
        self.calendar = DateEntry(self.addExpenditureFrame, state='readonly',
                                  date_pattern='DD/MM/YYYY', textvariable=self.dateVar,
                                  showweeknumbers=False, maxdate=datetime.today())
        # Creates text variable and error label to output any error messages
        self.errorVar = StringVar()
        self.errorLabel = Label(self.addExpenditureFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
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
        self.expenditureWin.bind('<Return>', lambda event: self.saveExpenditure())

        center(self.expenditureWin)

    def saveExpenditure(self):
        # Retrieves amount, details and date from the previous form

        # Checks that amount is valid
        amount, amountValid = validateFloat(self.amountVar.get().strip())

        details = self.detailsBox.get('1.0', END).strip()
        date = self.dateVar.get()

        if amountValid:
            # Checks that all fields have been filled
            if amount and details and date:
                if len(details) < 36:
                    # Generates a random expenditureID, using the random module
                    expenditureID = 'EX' + str(''.join(['%s' % random.randint(0, 9) for num in range(0, 5)]))
                    # Asks for user confimation of the input details
                    if messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nExpenditureID:\t'
                                                              + expenditureID + '\nAmount:\t\t£{:.2f}'.format(amount) +
                                                              '\nDetails:\t\t' + details + '\nDate:\t\t' + date):
                        try:
                            # Inserts record into expenditureTbl
                            executeSQL('INSERT INTO expenditureTbl VALUES (?,?,?,?,?)',
                                       (expenditureID, amount, details, date, userID), False)
                            loadDatabase(self.tree, 'expenditureTbl', False)  # Reloads records into treeview
                            # Destroys add expenditure toplevel and returns to view expenditures window
                            enableWindow(self.expenditureWin, self.returnButton, self.addExpenditureButton,
                                         self.editExpenditureButton, self.delExpenditureButton)
                            accesslevel(2, self.addExpenditureButton, self.editExpenditureButton)
                            accesslevel(3, self.delExpenditureButton)
                            messagebox.showinfo('Success!', 'New Expenditure Saved')
                        except sqlite3.IntegrityError:  # Outputs error message if expenditureID is not unique
                            self.errorVar.set('Error: Failed To Update Database.\nPlease Try Again')
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
            self.expenditureWin = Toplevel(self.root)
            self.expenditureWin.title('Edit Expenditure')
            self.expenditureWin.iconbitmap(icon)
            self.expenditureWin.protocol('WM_DELETE_WINDOW', lambda: (
                enableWindow(self.expenditureWin, self.returnButton, self.addExpenditureButton,
                             self.editExpenditureButton, self.delExpenditureButton),
                accesslevel(2, self.addExpenditureButton, self.editExpenditureButton),
                accesslevel(3, self.delExpenditureButton)))
            self.editExpenditureFrame = Frame(self.expenditureWin)
            self.editExpenditureFrame.pack()
            # Creates all the labels and entry boxes for each field
            self.detailLabel = Label(self.editExpenditureFrame, text='Update Expenditure Details:', font='none 11 bold')
            self.expenditureIDLabel = Label(self.editExpenditureFrame, text='ExpenditureID:', font='none 11')
            self.expenditureIDInsert = Label(self.editExpenditureFrame, text=expenditureID, font='none 11')
            self.amountLabel = Label(self.editExpenditureFrame, text='Amount:', font='none 11')
            self.amountVar = StringVar()
            self.amountBox = ttk.Entry(self.editExpenditureFrame, textvariable=self.amountVar)
            self.detailsLabel = Label(self.editExpenditureFrame, text='Details:', font='none 11')
            self.detailsBox = Text(self.editExpenditureFrame, width=15, height=5)
            self.dateLabel = Label(self.editExpenditureFrame, text='Date:', font='none 11')
            self.dateVar = StringVar()
            # Creates a calendar widget to pick the date from
            self.calendar = DateEntry(self.editExpenditureFrame, state='readonly',
                                      date_pattern='DD/MM/YYYY', textvariable=self.dateVar,
                                      showweeknumbers=False, maxdate=datetime.today())
            # Creates text variable and error label to output any error messages
            self.errorVar = StringVar()
            self.errorLabel = Label(self.editExpenditureFrame, textvariable=self.errorVar, font='none 11 bold',
                                    fg='red')
            # Creates save button, which calls the function saveExpenditure when pressed
            self.saveButton = ttk.Button(self.editExpenditureFrame, text='Update Expenditure',
                                         command=lambda: self.saveEditExpenditure(expenditureID))
            # Grids all the labels, entry boxes and buttons that we have created to the frame
            self.detailLabel.grid(row=0, column=0, columnspan=2, pady=10)
            self.expenditureIDLabel.grid(row=1, column=0, sticky='E', padx=(10, 0))
            self.expenditureIDInsert.grid(row=1, column=1, padx=(0, 10))
            self.amountLabel.grid(row=2, column=0, sticky='E', padx=(10, 0))
            self.amountBox.grid(row=2, column=1, padx=(0, 10))
            self.detailsLabel.grid(row=3, column=0, sticky='NE', padx=(10, 0))
            self.detailsBox.grid(row=3, column=1, padx=(0, 10))
            self.dateLabel.grid(row=4, column=0, sticky='E', padx=(10, 0))
            self.calendar.grid(row=4, column=1, padx=(0, 10), sticky='ew')
            self.errorLabel.grid(row=5, column=0, columnspan=2)
            self.saveButton.grid(row=6, column=0, columnspan=2, pady=(0, 10))

            self.amountBox.insert(INSERT, amount)
            self.detailsBox.insert(INSERT, details)
            self.dateVar.set(date)
            # Runs the saveExpenditure function when the user presses the 'enter' button (same as saveButton)
            self.expenditureWin.bind('<Return>', lambda event: self.saveEditExpenditure(expenditureID))

            center(self.expenditureWin)

        else:  # Outputs error message if no record has been selected
            messagebox.showerror('Error', 'No Record Selected')

    def saveEditExpenditure(self, expenditureID):
        # Retrieves amount, details and date from the previous form

        # Checks that newAmount is valid
        newAmount, newAmountValid = validateFloat(self.amountVar.get().strip())

        newDetails = self.detailsBox.get('1.0', END).strip()
        newDate = self.dateVar.get()
        if newAmountValid:
            # Checks that all fields have been filled
            if newAmount and newDetails and newDate:
                if len(newDetails) < 36:
                    # Creates confirmation dialogue to confirm details are correct
                    if messagebox.askyesno('Confirm Details', 'Are these details correct?\n\nExpenditureID:\t' +
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
                        accesslevel(2, self.addExpenditureButton, self.editExpenditureButton)
                        accesslevel(3, self.delExpenditureButton)
                        messagebox.showinfo('Success!', 'Expenditure Details Updated')
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
            if messagebox.askokcancel('Delete', 'Are you sure you want to permanently delete this record?'):
                for selected_item in self.tree.selection():
                    # Deletes the record from expenditureTbl
                    executeSQL('DELETE FROM expenditureTbl WHERE expenditureID=?', (expenditureID,), False)
                    # Removes the record from the treeview
                    self.tree.delete(selected_item)
        else:  # Outputs error message if no record has been selected
            messagebox.showerror('Error', 'No Record Selected')

    def report(self):
        disableWindow(self.reportButton, self.returnButton, self.addExpenditureButton, self.editExpenditureButton,
                      self.delExpenditureButton)
        self.expenditureWin = Toplevel(self.root)
        self.expenditureWin.title('Expenditure Report')
        self.expenditureWin.iconbitmap(icon)
        self.expenditureWin.protocol('WM_DELETE_WINDOW',
                                     lambda: (enableWindow(self.expenditureWin, self.reportButton, self.returnButton,
                                                           self.addExpenditureButton, self.editExpenditureButton,
                                                           self.delExpenditureButton),
                                              accesslevel(2, self.addExpenditureButton, self.editExpenditureButton),
                                              accesslevel(3, self.delExpenditureButton)))
        self.expenditureReportFrame = Frame(self.expenditureWin)
        self.expenditureReportFrame.pack()
        # Creates labels and entry boxes for start/end date of report
        self.detailLabel = Label(self.expenditureReportFrame, text='Enter Report Parameters', font='none 11 bold')
        self.startDateLabel = Label(self.expenditureReportFrame, text='Start Date:', font='none 11')
        self.startDateVar = StringVar()
        self.startCalendar = DateEntry(self.expenditureReportFrame, state='readonly',
                                       date_pattern='DD/MM/YYYY', textvariable=self.startDateVar,
                                       showweeknumbers=False, maxdate=datetime.today())
        self.endDateLabel = Label(self.expenditureReportFrame, text='End Date:', font='none 11')
        self.endDateVar = StringVar()
        self.endCalendar = DateEntry(self.expenditureReportFrame, state='readonly',
                                     date_pattern='DD/MM/YYYY', textvariable=self.endDateVar,
                                     showweeknumbers=False, maxdate=datetime.today())
        # Creates a text variable and error label to output any errors to
        self.errorVar = StringVar()
        self.errorLabel = Label(self.expenditureReportFrame, textvariable=self.errorVar, font='none 11 bold', fg='red')
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
        self.expenditureWin.bind('<Return>', lambda event: self.generateReport())

        center(self.expenditureWin)

    def generateReport(self):
        try:
            # Retrieves the start and end dates entered from the form
            self.startDate = datetime.strptime(self.startDateVar.get().strip(), '%d/%m/%Y')
            self.endDate = datetime.strptime(self.endDateVar.get().strip(), '%d/%m/%Y')
            # Clears any error messages
            self.errorVar.set('')
            disableWindow(self.enterButton)
            # Creates a new toplevel window to display the report
            self.expenditureReportWin = Toplevel(self.expenditureWin)
            self.expenditureReportWin.title('Expenditure Report')
            self.expenditureReportWin.iconbitmap(icon)
            self.expenditureReportFrame = Frame(self.expenditureReportWin)
            self.expenditureReportFrame.pack(fill='both', expand=True)
            self.expenditureReportWin.protocol('WM_DELETE_WINDOW',
                                               lambda: enableWindow(self.expenditureReportWin, self.enterButton))
            self.titleLabel = Label(self.expenditureReportFrame, text='Kingfisher Trust', font='algerian 14 bold',
                                    fg='#2380b7')
            self.detailLabel = Label(self.expenditureReportFrame, text='Expenditure Report', font='none 12 bold')
            # Creates a label detailing the date constraints of the report, as input by the user
            self.datesLabel = Label(self.expenditureReportFrame,
                                    text='From ' + str(datetime.isoformat(self.startDate)[:10])
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
            self.reporttree.grid(row=6, column=0, sticky='ewns', columnspan=3, padx=(10, 0), pady=10)
            self.expenditureReportFrame.columnconfigure([0, 1, 2], weight=1)  # column with treeview
            self.expenditureReportFrame.rowconfigure(6, weight=1)  # row with treeview

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
            self.spentLabel = Label(self.expenditureReportFrame,
                                    text=str('Total Cost = £{:.2f}'.format(self.totalSpend)))
            self.spentLabel.grid(row=3, column=0, padx=10, sticky='w')

            self.scrollbar = ttk.Scrollbar(self.expenditureReportFrame, orient='vertical',
                                           command=self.reporttree.yview)
            self.scrollbar.grid(row=6, column=3, sticky='ns', pady=10, padx=(0, 10))
            self.reporttree.configure(yscrollcommand=self.scrollbar.set, selectmode='browse')

            center(self.expenditureReportWin)

        except ValueError:
            # Outputs an error if the dates input are invalid
            self.errorVar.set('Error: Invalid Input\nDD/MM/YYYY')


###########################################################################

def main():
    global app
    while True:
        win = Tk()
        login = loginWin(win)
        win.mainloop()
        if login.authenticated:
            root = Tk()
            app = mainMenu(root)
            root.mainloop()
        else:
            break


# First checks that the database file exists (function from SQL module)
# Creates DB if necessary,
# Then runs the main program
createDatabase()
main()
