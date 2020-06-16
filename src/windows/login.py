import bcrypt
import tkinter as tk
from tkinter import ttk

from .. import config
from ..sql import executeSQL
from ..utils import center


class loginWin:
    # Creates login window
    def __init__(self, root):
        self.authenticated = False
        self.root = root
        self.root.title('Login')
        self.root.iconbitmap(config.icon)
        self.frame = tk.Frame(root)
        self.frame.pack(expand=True)
        # Creates a label with ‘Kingfisher Trust’ in bold, blue text with ‘Algerian’ font – the same text
        # as is used on their website, to maintain brand consistency.
        self.titleLabel = tk.Label(
            self.frame, text='Kingfisher Trust', font='algerian 18 bold', fg='#2380b7')
        # Creates the username and password labels and entry boxes, as well as defining variables for the
        # inputted data
        self.usernameLabel = tk.Label(
            self.frame, text='Username:', font='none 11')
        self.usernameVar = tk.StringVar()
        self.usernameBox = ttk.Entry(self.frame, textvariable=self.usernameVar)
        self.passwordLabel = tk.Label(
            self.frame, text='Password:', font='none 11')
        self.passwordVar = tk.StringVar()
        # Password will only show *s when data is input, to protect the user’s password
        # from falling victim to shoulder surfing.
        self.passwordBox = ttk.Entry(
            self.frame, show='•', textvariable=self.passwordVar)
        self.forgotPass = tk.Label(
            self.frame, text='Forgotten Password?', fg='blue', cursor='hand2')
        # Defines a text variable and creates a label so that errors can be shown
        # This is initially blank, and the variable can be set to display any suitable message
        self.errorVar = tk.StringVar()
        self.errorLabel = tk.Label(
            self.frame, textvariable=self.errorVar, font='none 11 bold', fg='red')
        # Creates the exit and login buttons, and calls the functions when the buttons are clicked
        self.exitButton = ttk.Button(
            self.frame, text='Exit', command=lambda: self.closeWindow())
        self.loginButton = ttk.Button(
            self.frame, text='Login', command=lambda: self.login())
        # Grids all the labels, boxes and buttons that we have created to the frame
        self.titleLabel.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.usernameLabel.grid(row=1, column=0, sticky='e')
        self.usernameBox.grid(row=1, column=1, pady=10, padx=(0, 10))
        self.passwordLabel.grid(row=2, column=0, sticky='e')
        self.passwordBox.grid(row=2, column=1, pady=10, padx=(0, 10))
        self.forgotPass.grid(row=3, column=0, columnspan=2)
        self.forgotPass.bind('<Button-1>', lambda x: self.forgotPassword())
        self.errorLabel.grid(row=4, column=0, columnspan=2)
        self.exitButton.grid(row=5, column=0, pady=(
            0, 25), padx=10, ipadx=10, ipady=2, sticky='news')
        self.loginButton.grid(row=5, column=1, pady=(
            0, 25), padx=10, ipadx=10, ipady=2, sticky='news')
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
            user = executeSQL(
                'SELECT * FROM staffTbl WHERE staffID = ?', (username,), False)
            # If a matching records is found, it drops into the following code
            if user:
                config.userID = username
                config.accessLevel = user[4]
                config.fullName = user[2] + ' ' + user[1]
                salt = user[6]
                storedPass = user[5]
                # If access level ‘x’ i.e. no longer have access to system, a suitable error message is output
                if config.accessLevel == 'x':
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
                        self.errorVar.set(
                            'Error: Incorrect\nUsername or Password')
            # If no records matched, the errorVar text variable is set to a suitable error message
            else:
                self.errorVar.set('Error: Incorrect\nUsername or Password')
        else:
            self.errorVar.set('Error: Please Fill all Fields')

    # Creates password reset window
    def forgotPassword(self):
        # Creates a frame for admin login
        self.passWin = tk.Toplevel(self.root)
        self.passWin.iconbitmap(config.icon)
        self.passWin.protocol('WM_DELETE_WINDOW', lambda: (self.passWin.destroy(),
                                                           self.forgotPass.bind('<Button-1>',
                                                                                lambda x: self.forgotPassword())))
        self.forgotPass.bind('<Button-1>', lambda x: self.passWin.lift())
        self.passWin.title('Password Reset')
        self.adminFrame = tk.Frame(self.passWin)
        # packs frame to window
        self.adminFrame.pack(side=tk.LEFT, expand=True)
        self.adminUsernameLabel = tk.Label(
            self.adminFrame, text='Admin Username:', font='none 11')
        self.adminUsernameVar = tk.StringVar()
        self.adminUsernameBox = ttk.Entry(
            self.adminFrame, textvariable=self.adminUsernameVar)
        self.adminPasswordLabel = tk.Label(
            self.adminFrame, text='Admin Password:', font='none 11')
        self.adminPasswordVar = tk.StringVar()
        self.adminPasswordBox = ttk.Entry(
            self.adminFrame, show='•', textvariable=self.adminPasswordVar)
        self.adminErrorVar = tk.StringVar()
        self.adminErrorLabel = tk.Label(
            self.adminFrame, textvariable=self.adminErrorVar, font='none 11 bold', fg='red')
        self.loginButton = ttk.Button(
            self.adminFrame, text='Login', command=lambda: self.adminLogin())
        # Grids buttons/labels/entries to frame
        self.adminUsernameLabel.grid(row=1, column=0, padx=(10, 0))
        self.adminUsernameBox.grid(row=1, column=1, pady=10, padx=10)
        self.adminPasswordLabel.grid(row=2, column=0, padx=(10, 0))
        self.adminPasswordBox.grid(row=2, column=1, pady=10, padx=10)
        self.adminErrorLabel.grid(row=3, column=0, columnspan=2)
        self.loginButton.grid(row=4, column=0, columnspan=2, pady=(
            0, 20), padx=10, ipadx=10, ipady=2, sticky='news')

        # Creates a seperator between the frames
        self.seperator = ttk.Separator(self.passWin, orient='vertical')
        self.seperator.pack(side=tk.LEFT, fill=tk.Y)

        # Creates a frame to enter a username and new password
        # Entry boxes and buttons are readonly/disabled until the admin password is entered
        self.passFrame = tk.Frame(self.passWin)
        self.passFrame.pack(side=tk.LEFT, expand=True)
        self.usernameLabel = tk.Label(
            self.passFrame, text='Staff Username:', font='none 11')
        self.staffUsernameVar = tk.StringVar()
        self.usernameBox = ttk.Entry(
            self.passFrame, textvariable=self.staffUsernameVar, state='readonly')
        self.passwordLabel = tk.Label(
            self.passFrame, text='New Password:', font='none 11', )
        self.newPasswordVar = tk.StringVar()
        self.passwordBox = ttk.Entry(
            self.passFrame, show='•', textvariable=self.newPasswordVar, state='readonly')
        self.newPassErrorVar = tk.StringVar()
        self.newPassErrorLabel = tk.Label(
            self.passFrame, textvariable=self.newPassErrorVar, font='none 11 bold', fg='red')
        self.confirmButton = ttk.Button(self.passFrame, text='Confirm', state='disabled',
                                        command=lambda: self.changePass())
        # Grids buttons/labels/entries to frame
        self.usernameLabel.grid(row=1, column=0)
        self.usernameBox.grid(row=1, column=1, pady=10, padx=10)
        self.passwordLabel.grid(row=2, column=0)
        self.passwordBox.grid(row=2, column=1, pady=10, padx=10)
        self.newPassErrorLabel.grid(row=3, column=0, columnspan=2)
        self.confirmButton.grid(row=4, column=0, columnspan=2, pady=(
            0, 20), padx=10, ipadx=10, ipady=2, sticky='news')

        center(self.passWin)

    # Verifies admin credentials
    def adminLogin(self):
        # Retrieves admin username/password from form
        username = self.adminUsernameVar.get()
        password = self.adminPasswordVar.get()
        # Fetches record with the same username as inputted
        user = executeSQL(
            'SELECT * FROM staffTbl WHERE staffID = ?', (username,), False)
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
                self.adminErrorVar.set(
                    'Error: Incorrect\nUsername or Password')
        else:
            self.adminErrorVar.set('Error: Incorrect\nUsername or Password')

    # Changed password of input user
    def changePass(self):
        username = self.staffUsernameVar.get()
        password = self.newPasswordVar.get()
        if username and password:
            user = executeSQL(
                'SELECT * FROM staffTbl WHERE staffID = ?', (username,), False)
            if user:
                salt = user[6]
                password = bcrypt.hashpw(password.encode('utf-8'), salt)
                executeSQL(
                    'UPDATE staffTbl SET password = ? WHERE staffID = ?', (password, username), False)
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
