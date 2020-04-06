from prettytable import PrettyTable
from fpdf import FPDF
from tkinter import messagebox
from datetime import datetime
import subprocess

logo = 'logo.jpg'
font = 'ALGER.TTF'


# Using the records fetched from the previous report, which was output into a treeview,
# this puts the same records (i.e. exact same report) into a table, which is then pasted into
# a PDF document. The process is identical for donation reports, order and expenditure reports.

class donationReport:

    def __init__(self, startDate, endDate, records, totalDonat):
        self.startDate = startDate
        self.endDate = endDate
        records.reverse()
        self.records = records
        self.totalDonat = totalDonat
        self.createPDF()

    def createPDF(self):
        self.table = PrettyTable()
        self.table.field_names = ['DonationID', 'Amount', 'Cash/Bank', 'Reference No', 'Date', 'DonorID', 'Donor Name',
                                  'StaffID']

        for record in self.records:
            self.table.add_row(record)

        header, data = self.get_data_from_prettytable(self.table)
        self.export_to_pdf(header, data)

    def get_data_from_prettytable(self, data):
        """
        Get a list of list from pretty_data table
        Arguments:
            :param data: data table to process
            :type data: PrettyTable
        """

        def remove_space(liste):
            """
            Remove space for each word in a list
            Arguments:
                :param liste: list of strings
            """
            list_without_space = []
            for mot in liste:  # For each word in list
                list_without_space.append(mot)  # list of word without space
            return list_without_space

        # Get each row of the table
        string_x = str(self.table).split('\n')  # Get a list of row
        header = string_x[1].split('|')[1: -1]  # Columns names
        rows = string_x[3:len(string_x) - 1]  # List of rows

        list_word_per_row = []
        for row in rows:  # For each word in a row
            row_resize = row.split('|')[1:-1]  # Remove first and last arguments
            list_word_per_row.append(remove_space(row_resize))  # Remove spaces

        return header, list_word_per_row

    def export_to_pdf(self, header, data):
        """
        Create a a table in PDF file from a list of row
            :param header: columns name
            :param data: List of row (a row = a list of cells)
            :param spacing=1:
        """
        pdf = FPDF()  # New  pdf object

        pdf.set_font('Arial', size=10)  # Font style
        epw = pdf.w - 2 * pdf.l_margin  # Width of document
        col_width = pdf.w / 9  # Column width in table
        row_height = pdf.font_size * 1.5  # Row height in table
        spacing = 1.3  # Space in each cell

        pdf.add_page()  # add new page
        pdf.image(logo, 20, 5, 12, 13)
        pdf.image(logo, epw - 20, 5, 12, 13)
        pdf.add_font('algerian', '', font, uni=True)
        pdf.set_font('algerian', size=14)
        pdf.set_text_color(35, 128, 183)  # Trust logo colour
        pdf.cell(epw, 0, 'Kingfisher Trust', align='C')
        pdf.ln(row_height * spacing)
        pdf.set_font('Arial', size=10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(epw, 0, 'Donation Report', align='C')  # create title cell
        pdf.ln(row_height * spacing)  # Define title line style
        pdf.cell(epw, 0, 'From ' + str(datetime.isoformat(self.startDate)[:10]) + ' to '
                 + str(datetime.isoformat(self.endDate)[:10]) + ':', align='L')
        pdf.ln(row_height * spacing)
        pdf.cell(10, 0, 'Total Donated = £{:.2f}'.format(self.totalDonat), align='L')
        pdf.cell(epw - 10, 0, 'Report Created: ' + str(datetime.isoformat(datetime.today())[:10]), align='R')
        pdf.ln(row_height * spacing)

        # Add header
        for item in header:  # for each column
            pdf.cell(col_width, row_height * spacing,  # Add a new cell
                     txt=item, border='B', align='C')
        pdf.ln(row_height * spacing)  # New line after header

        for row in data:  # For each row of the table
            for item in row:  # For each cell in row
                pdf.cell(col_width, row_height * spacing,  # Add cell
                         txt=item, border=0, align='C')
            pdf.ln(row_height * spacing)  # Add line at the end of row

        title = ('reports/DONATION ' + str(datetime.isoformat(self.startDate)[:10]) + ' to ' +
                 str(datetime.isoformat(self.endDate)[:10]) + '.pdf')

        try:
            pdf.output(title)  # Create pdf file
            pdf.close()
            openFile = messagebox.askyesno('Success',
                                           'PDF File Created\n' + title + '\n\nOpen File?')  # Outputs success dialogue
        except OSError:
            openFile = messagebox.askyesno('Error', 'Unable to Overwrite Existing File\n\nOpen File?', icon='error')

        if openFile:
            subprocess.Popen([title], shell=True)  # Opens file


class orderReport:

    def __init__(self, startDate, endDate, records, totalCost, totalRevenue, totalProfit):
        self.startDate = startDate
        self.endDate = endDate
        records.reverse()
        self.records = records
        self.totalCost = totalCost
        self.totalRevenue = totalRevenue
        self.totalProfit = totalProfit
        self.createPDF()

    def createPDF(self):

        self.table = PrettyTable()
        self.table.field_names = ['OrderID', 'CustomerID', 'Date', 'ItemID', 'ItemName', 'Quantity', 'SalePrice',
                                  'SupplierCost', 'SupplierID']

        for record in self.records:
            self.table.add_row(record)

        header, data = self.get_data_from_prettytable(self.table)
        self.export_to_pdf(header, data)

    def get_data_from_prettytable(self, data):
        """
        Get a list of list from pretty_data table
        Arguments:
            :param data: data table to process
            :type data: PrettyTable
        """

        def remove_space(liste):
            """
            Remove space for each word in a list
            Arguments:
                :param liste: list of strings
            """
            list_without_space = []
            for mot in liste:  # For each word in list
                list_without_space.append(mot)  # list of word without space
            return list_without_space

        # Get each row of the table
        string_x = str(self.table).split('\n')  # Get a list of row
        header = string_x[1].split('|')[1: -1]  # Columns names
        rows = string_x[3:len(string_x) - 1]  # List of rows

        list_word_per_row = []
        for row in rows:  # For each word in a row
            row_resize = row.split('|')[1:-1]  # Remove first and last arguments
            list_word_per_row.append(remove_space(row_resize))  # Remove spaces

        return header, list_word_per_row

    def export_to_pdf(self, header, data):
        """
        Create a a table in PDF file from a list of row
            :param header: columns name
            :param data: List of row (a row = a list of cells)
            :param spacing=1:
        """
        pdf = FPDF()  # New  pdf object

        pdf.set_font('Arial', size=10)  # Font style
        epw = pdf.w - 2 * pdf.l_margin  # Width of document
        col_width = pdf.w / 10  # Column width in table
        row_height = pdf.font_size * 1.5  # Row height in table
        spacing = 1.3  # Space in each cell

        pdf.add_page()  # add new page
        pdf.image(logo, 20, 5, 12, 13)
        pdf.image(logo, epw - 20, 5, 12, 13)
        pdf.add_font('algerian', '', font, uni=True)  # Adds algerian font
        pdf.set_font('algerian', size=14)
        pdf.set_text_color(35, 128, 183)  # Trust logo colour
        pdf.cell(epw, 0, 'Kingfisher Trust', align='C')
        pdf.ln(row_height * spacing)
        pdf.set_font('Arial', size=10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(epw, 0, 'Revenue Report', align='C')  # create title cell
        pdf.ln(row_height * spacing)  # Define title line style
        pdf.cell(epw, 0, 'From ' + str(datetime.isoformat(self.startDate)[:10]) + ' to '
                 + str(datetime.isoformat(self.endDate)[:10]) + ':', align='L')
        pdf.ln(row_height * spacing)
        pdf.cell(10, 0, str('Total Cost = £{:.2f}'.format(self.totalCost)), align='L')
        pdf.cell(epw - 10, 0, 'Report Created: ' + str(datetime.isoformat(datetime.today())[:10]), align='R')
        pdf.ln(row_height * spacing)
        pdf.cell(10, 0, str('Total Revenue = £{:.2f}'.format(self.totalRevenue)), align='L')
        pdf.ln(row_height * spacing)
        pdf.cell(10, 0, str('Total Profit = £{:.2f}'.format(self.totalProfit)), align='L')
        pdf.ln(row_height * spacing)

        # Add header
        for item in header:  # for each column
            pdf.cell(col_width, row_height * spacing,  # Add a new cell
                     txt=item, border='B', align='C')
        pdf.ln(row_height * spacing)  # New line after header

        for row in data:  # For each row of the table
            for item in row:  # For each cell in row
                pdf.cell(col_width, row_height * spacing,  # Add cell
                         txt=item, border=0, align='C')
            pdf.ln(row_height * spacing)  # Add line at the end of row
        title = ('reports/REVENUE ' + str(datetime.isoformat(self.startDate)[:10]) + ' to ' +
                 str(datetime.isoformat(self.endDate)[:10]) + '.pdf')

        try:
            # Will overwrite any existing file
            pdf.output(title)  # Create pdf file
            pdf.close()
            openFile = messagebox.askyesno('Success',
                                           'PDF File Created\n' + title + '\n\nOpen File?')  # Outputs success dialogue
        except OSError:
            openFile = messagebox.askyesno('Error', 'Unable to Overwrite Existing File\n\nOpen File?', icon='error')

        if openFile:
            subprocess.Popen([title], shell=True)  # Opens file


class expenditureReport:

    def __init__(self, startDate, endDate, records, totalSpent):
        self.startDate = startDate
        self.endDate = endDate
        records.reverse()
        self.records = records
        self.totalSpent = totalSpent
        self.createPDF()

    def createPDF(self):
        self.table = PrettyTable()
        self.table.field_names = ['ExpenditureID', 'Amount', 'Details', 'Date', 'StaffID']

        for record in self.records:
            self.table.add_row(record)

        header, data = self.get_data_from_prettytable(self.table)
        self.export_to_pdf(header, data)

    def get_data_from_prettytable(self, data):
        """
        Get a list of list from pretty_data table
        Arguments:
            :param data: data table to process
            :type data: PrettyTable
        """

        def remove_space(liste):
            """
            Remove space for each word in a list
            Arguments:
                :param liste: list of strings
            """
            list_without_space = []
            for mot in liste:  # For each word in list
                list_without_space.append(mot)  # list of word without space
            return list_without_space

        # Get each row of the table
        string_x = str(self.table).split('\n')  # Get a list of row
        header = string_x[1].split('|')[1: -1]  # Columns names
        rows = string_x[3:len(string_x) - 1]  # List of rows

        list_word_per_row = []
        for row in rows:  # For each word in a row
            row_resize = row.split('|')[1:-1]  # Remove first and last arguments
            list_word_per_row.append(remove_space(row_resize))  # Remove spaces

        return header, list_word_per_row

    def export_to_pdf(self, header, data):
        """
        Create a a table in PDF file from a list of row
            :param header: columns name
            :param data: List of row (a row = a list of cells)
            :param spacing=1:
        """
        pdf = FPDF()  # New  pdf object

        pdf.set_font('Arial', size=10)  # Font style
        epw = pdf.w - 2 * pdf.l_margin  # Width of document
        col_width = pdf.w / 5.5  # Column width in table
        row_height = pdf.font_size * 1.5  # Row height in table
        spacing = 1.3  # Space in each cell

        pdf.add_page()  # add new page
        pdf.image(logo, 20, 5, 12, 13)
        pdf.image(logo, epw - 20, 5, 12, 13)
        pdf.add_font('algerian', '', font, uni=True)
        pdf.set_font('algerian', size=14)
        pdf.set_text_color(35, 128, 183)  # Trust logo colour
        pdf.cell(epw, 0, 'Kingfisher Trust', align='C')
        pdf.ln(row_height * spacing)
        pdf.set_font('Arial', size=10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(epw, 0, 'Expenditure Report', align='C')  # create title cell
        pdf.ln(row_height * spacing)  # Define title line style
        pdf.cell(epw, 0, 'From ' + str(datetime.isoformat(self.startDate)[:10]) + ' to '
                 + str(datetime.isoformat(self.endDate)[:10]) + ':', align='L')
        pdf.ln(row_height * spacing)
        pdf.cell(10, 0, 'Total Spent = £{:.2f}'.format(self.totalSpent), align='L')
        pdf.cell(epw - 10, 0, 'Report Created: ' + str(datetime.isoformat(datetime.today())[:10]), align='R')
        pdf.ln(row_height * spacing)

        # Add header
        for item in header:  # for each column
            pdf.cell(col_width, row_height * spacing,  # Add a new cell
                     txt=item, border='B', align='C')
        pdf.ln(row_height * spacing)  # New line after header

        for row in data:  # For each row of the table
            for item in row:  # For each cell in row
                pdf.cell(col_width, row_height * spacing,  # Add cell
                         txt=item, border=0, align='C')
            pdf.ln(row_height * spacing)  # Add line at the end of row

        title = ('reports/EXPENDITURE ' + str(datetime.isoformat(self.startDate)[:10]) + ' to ' +
                 str(datetime.isoformat(self.endDate)[:10]) + '.pdf')

        try:
            pdf.output(title)  # Create pdf file
            pdf.close()
            openFile = messagebox.askyesno('Success',
                                           'PDF File Created\n' + title + '\n\nOpen File?')  # Outputs success dialogue
        except OSError:
            openFile = messagebox.askyesno('Error', 'Unable to Overwrite Existing File\n\nOpen File?', icon='error')

        if openFile:
            subprocess.Popen([title], shell=True)  # Opens file
