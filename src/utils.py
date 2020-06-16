import tkinter as tk
import datetime
from . import config


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
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry('+%d+%d' % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background='#ffffe0', relief=tk.SOLID, borderwidth=1,
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
    if config.accessLevel < required:
        for i in buttons:
            toolTip = ToolTip(i)
            i['state'] = 'disabled'
            i.bind('<Enter>', lambda x: toolTip.showtip(
                'Insufficient Access Level'))
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
    for index, (_, k) in enumerate(l):
        tv.move(k, '', index)

    # Sets the command for the column to reverse the sort when clicked
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))
