import re
from datetime import datetime


# Performs validation on an input phone number, using
# Regular Expression criteria to check that the input follows a specific
# pattern, i.e. valid UK Phone number
def validatePhone(phoneNumber):
    valid = re.match('^(([0]{1})|([\+][4]{2}))([1]|[2]|[3]|[7]){1}\d{8,9}$', phoneNumber)
    # Returns a boolean value, which is true if the input matches
    # the regular expression criteria
    return valid


# Performs validation on an input email, using
# Regular Expression criteria to check that the input follows a specific
# pattern, i.e. ___@___.___
def validateEmail(email):
    valid = re.match('^[^@]+@[^@]+\.[^@]+$', email)
    # Returns a boolean value, which is true if the input matches
    # the regular expression criteria
    return valid


# Performs validation to confirm that a value is a float,
# using try-except
def validateFloat(value):
    try:
        value = float(value)
        valid = True
    except ValueError:
        valid = False

    # returns the converted (if successful) float value,
    # and a boolean value, which is true if the value is a float
    return value, valid


# Performs validation to confirm that a value is an integer,
# using try-except
def validateInt(value):
    try:
        value = int(value)
        valid = True
    except ValueError:
        valid = False

    # returns the converted (if successful) integer value,
    # and a boolean value, which is true if the value is a integer
    return value, valid


# Performs validation to confirm that the date is valid,
# by using a try-except to convert the input to a datetime object
def validateDate(value, errorLabel):
    try:
        # Trues to convert value into a datetime object, following the
        # format DD/MM/YYYY
        datetime.strptime(value, '%d/%m/%Y')
        valid = True
    except ValueError:
        valid = False

    if not valid:
        # Outputs error message if not valid. Since the GUI now uses
        # A calendar datepicker, this should never occur, however the message
        # is kept just in case
        errorLabel.set('Error: Invalid Input\nDD/MM/YYYY')

    # Returns only the boolean value, which is true when the input date
    # is of the correct format
    return valid
