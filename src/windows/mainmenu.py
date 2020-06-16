import tkinter as tk
from tkinter import ttk

from .. import config
from ..utils import accesslevel, center

from .donation import donationWindow
from .donor import donorWindow
from .expenditure import expenditureWindow
from .item import itemWindow
from .order import orderWindow
from .recipient import recipientWindow
from .staff import staffWindow
from .supplier import supplierWindow


class mainMenu:
    # Creates main menu window
    def __init__(self, root):
        self.root = root
        self.root.title('Main Menu')
        self.root.iconbitmap(config.icon)
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        # Calls the logout function when the main menu is closed
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.logout())
        # Creates labels with the Trust's name, a welcome message and the user's access level
        self.kingfisherLabel = tk.Label(
            self.frame, text='Kingfisher Trust', font='algerian 18 bold', fg='#2380b7')
        self.userLabel = tk.Label(
            self.frame, text='Welcome\n' + config.fullName, font='none 11')
        self.userAccessLabel = tk.Label(
            self.frame, text='Access Level: ' + str(config.accessLevel), font='none 9')
        # Creates all the buttons for the user to navigate the system, and
        # states what functions are called when the buttons are pressed
        self.orderButton = ttk.Button(
            self.frame, text='New Order', command=lambda: self.newOrder())
        self.donatButton = ttk.Button(
            self.frame, text='New Donation', command=lambda: self.newDonat())
        self.viewOrdersButton = ttk.Button(
            self.frame, text='View Orders', command=lambda: self.viewOrders())
        self.viewDonationsButton = ttk.Button(
            self.frame, text='View Donations', command=lambda: self.viewDonations())
        self.viewItemsButton = ttk.Button(
            self.frame, text='View Items', command=lambda: self.viewItems())
        self.viewDonorsButton = ttk.Button(
            self.frame, text='View Donors', command=lambda: self.viewDonors())
        self.viewSuppliersButton = ttk.Button(
            self.frame, text='View Suppliers', command=lambda: self.viewSuppliers())
        self.viewStaffButton = ttk.Button(
            self.frame, text='View Staff', command=lambda: self.viewStaff())
        self.viewRecipientsButton = ttk.Button(self.frame, text='View Recipients',
                                               command=lambda: self.viewRecipients())
        self.viewExpendituresButton = ttk.Button(self.frame, text='View Expenditures',
                                                 command=lambda: self.viewExpenditures())
        self.logoutButton = ttk.Button(
            self.frame, text='Logout', command=lambda: self.logout())

        # Grids all the buttons/labels to the frame
        self.kingfisherLabel.grid(row=0, column=0, columnspan=2)
        self.userLabel.grid(row=1, column=0)
        self.userAccessLabel.grid(row=2, column=0)
        self.logoutButton.grid(row=1, column=1, rowspan=2, ipadx=10, ipady=2)
        self.orderButton.grid(row=3, column=0, padx=(
            10, 0), pady=(5, 10), ipadx=10, ipady=2, sticky='news')
        self.donatButton.grid(row=3, column=1, padx=(
            0, 10), pady=(5, 10), ipadx=10, ipady=2, sticky='news')
        self.viewOrdersButton.grid(row=4, column=0, padx=(
            10, 0), ipadx=10, ipady=2, sticky='news')
        self.viewDonationsButton.grid(row=4, column=1, padx=(
            0, 10), ipadx=10, ipady=2, sticky='news')
        self.viewItemsButton.grid(row=5, column=0, padx=(
            10, 0), ipadx=10, ipady=2, sticky='news')
        self.viewDonorsButton.grid(row=5, column=1, padx=(
            0, 10), ipadx=10, ipady=2, sticky='news')
        self.viewSuppliersButton.grid(row=6, column=0, padx=(
            10, 0), ipadx=10, ipady=2, sticky='news')
        self.viewRecipientsButton.grid(row=6, column=1, padx=(
            0, 10), ipadx=10, ipady=2, sticky='news')
        self.viewStaffButton.grid(row=7, column=0, padx=(
            10, 0), pady=(0, 10), ipadx=10, ipady=2, sticky='news')
        self.viewExpendituresButton.grid(row=7, column=1, padx=(
            0, 10), pady=(0, 10), ipadx=10, ipady=2, sticky='news')

        # Checks access level and disables relevant buttons
        accesslevel(2, self.donatButton, self.orderButton)

        center(self.root)

    def logout(self):
        # Creates dialogue box to confirm whether the user wants to logout of the system
        if tk.messagebox.askyesno('Logout', 'Are you sure you want to logout?', icon='warning'):
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
        self.staffRoot = tk.Toplevel(self.root)
        self.createstaffWindow = staffWindow(self.staffRoot)

    def viewDonors(self):
        # Hides the main menu and creates the view donor window as a toplevel window
        self.disableMenu()
        self.donorRoot = tk.Toplevel(self.root)
        self.createDonorWindow = donorWindow(self.donorRoot)

    def newDonat(self):
        # Hides the main menu and opens the view donation window, as well as the add new donation form
        self.disableMenu()
        self.donationRoot = tk.Toplevel(self.root)
        self.createDonationWindow = donationWindow(self.donationRoot)
        self.createDonationWindow.addDonation()

    def viewDonations(self):
        # Hides the main menu and creates the view donation window as a toplevel window
        self.disableMenu()
        self.donationRoot = tk.Toplevel(self.root)
        self.createDonationWindow = donationWindow(self.donationRoot)

    def viewSuppliers(self):
        # Hides the main menu and creates the view supplier window as a toplevel window
        self.disableMenu()
        self.supplierRoot = tk.Toplevel(self.root)
        self.createSupplierWindow = supplierWindow(self.supplierRoot)

    def viewItems(self):
        # Hides the main menu and creates the view items window as a toplevel window
        self.disableMenu()
        self.itemRoot = tk.Toplevel(self.root)
        self.createItemWindow = itemWindow(self.itemRoot)

    def newOrder(self):
        # Hides the main menu and opens the view order window, as well as the add new order form
        self.disableMenu()
        self.orderRoot = tk.Toplevel(self.root)
        self.createOrderWindow = orderWindow(self.orderRoot)
        self.createOrderWindow.addOrder()

    def viewOrders(self):
        # Hides the main menu and creates the view orders window as a toplevel window
        self.disableMenu()
        self.orderRoot = tk.Toplevel(self.root)
        self.createOrderWindow = orderWindow(self.orderRoot)

    def viewRecipients(self):
        # Hides the main menu and creates the view recipients window as a toplevel window
        self.disableMenu()
        self.recipientRoot = tk.Toplevel(self.root)
        self.createRecipientWindow = recipientWindow(self.recipientRoot)

    def viewExpenditures(self):
        # Hides the main menu and creates the view expenditures window as a toplevel window
        self.disableMenu()
        self.expenditureRoot = tk.Toplevel(self.root)
        self.createExpenditureWindow = expenditureWindow(self.expenditureRoot)
