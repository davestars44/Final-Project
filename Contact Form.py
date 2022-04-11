# imports
import tkinter as tk
from tkinter import font as tkfont
import tkinter.ttk as ttk  # treeview
import entry_field
from models import *


class App(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # this is the main database access object
        # note you must run the init_db.py script before using Storage
        self.data = Storage()

        #  a single font to be used throughout the app
        self.title_font = tkfont.Font(
            family='Times New Roman', size=18, weight="bold", slant="italic")

        # the container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginPage, ContactForms, ReadPage, CreationPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self, persist=self.data)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, page_name, rid=0):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        # the edit screen requires knowledge of the id of the item
        if not rid == 0:
            frame.update(rid)
        else:
            frame.update()
        # bring it to the front of the stacking order
        frame.tkraise()


class LoginPage(tk.Frame):
    ''' simulates login
    '''

    def __init__(self, parent, controller, persist=None):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Company Sign in",
                         font=controller.title_font)
        label.grid(column=0, pady=10)

        tk.Label(self, text="User Name").grid(row=3, column=0)
        tk.Entry(self, ).grid(row=3, column=1)

        tk.Label(self, text="Password").grid(row=4, column=0)
        tk.Entry(self, show='*').grid(row=4, column=1)

        new_button = tk.Button(self, text="Login in",
                               command=lambda: controller.show_frame("ContactForms"))
        new_button.grid(column=0)


class ContactForms(tk.Frame):

    def __init__(self, parent, controller, persist=None):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Contacts Forms",
                         font=controller.title_font)
        label.grid(column=0, pady=10)

        ''' '''
        # set up the treeview
        contact_table = tk.Frame(self, width=500)
        contact_table.grid(column=0)
        scrollbarx = tk.Scrollbar(contact_table, orient=tk.HORIZONTAL)
        scrollbary = tk.Scrollbar(contact_table, orient=tk.VERTICAL)
        self.tree = ttk.Treeview(contact_table, columns=("id", "name", "email"),
                                 selectmode="extended", yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
        scrollbary.config(command=self.tree.yview)
        scrollbary.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbarx.config(command=self.tree.xview)
        scrollbarx.pack(side=tk.BOTTOM, fill=tk.X)
        # this section would allow for expanding the viewable columns
        self.tree.heading('id', text="ID", anchor=tk.W)
        self.tree.heading('name', text="Name", anchor=tk.W)
        self.tree.heading('email', text="Email", anchor=tk.W)
        self.tree.column('#0', stretch=tk.NO, minwidth=0, width=0)
        self.tree.column('#1', stretch=tk.NO, minwidth=0, width=60)
        self.tree.column('#2', stretch=tk.NO, minwidth=0, width=200)
        self.tree.column('#3', stretch=tk.NO, minwidth=0, width=200)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.pack()
        self.selected = []

        self.persist = persist
        all_records = self.persist.get_all_sorted_records()
        # grab all records from db and puts them to the treeview widget
        for record in all_records:
            self.tree.insert("", 0, values=(
                record.rid, record.name, record.email))

        ''' '''

        edit_button = tk.Button(self, text="Edit Record",
                                command=self.edit_selected)
        edit_button.grid(column=0)

        delete_button = tk.Button(self, text="Delete Record(s)",
                                  command=self.delete_selected)
        delete_button.grid(column=0)

        new_button = tk.Button(self, text="Add New Record",
                               command=lambda: controller.show_frame("CreationPage"))
        new_button.grid(column=0)
        exit_button = tk.Button(self, text="Exit", command=self.quit)
        exit_button.grid(column=0)

    def edit_selected(self):
        idx = self.selected[0]  # use first selected item if multiple
        record_id = self.tree.item(idx)['values'][0]
        self.controller.show_frame("ReadPage", record_id)

    def on_select(self, event):
        ''' add the currently highlighted items to a list
        '''
        self.selected = event.widget.selection()

    def delete_selected(self):
        ''' uses the selected list to remove and delete certain records
        '''
        for idx in self.selected:
            record_id = self.tree.item(idx)['values'][0]
            # remove from the db
            self.persist.delete_record(record_id)
            # remove from the treeview
            self.tree.delete(idx)

    def update(self):
        ''' to refresh the treeview, delete all its rows and repopulate from the db 
        '''
        for row in self.tree.get_children():
            self.tree.delete(row)
        all_records = self.persist.get_all_sorted_records()
        for record in all_records:
            self.tree.insert("", 0, values=(
                record.rid, record.name, record.email))


class ReadPage(tk.Frame):
    ''' set up as an edit form the same as the create page form
    this is incredibly redundant, refactoring the similar behaviour into a
    separate function would be a key step before adding or changing the form
    '''

    def __init__(self, parent, controller, persist=None):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Edit Entry",
                         font=controller.title_font)
        label.grid(row=0, column=0)
        # this object is the data persistence model
        self.persist = persist
        # this empty dict will hold each of the data entry fields
        self.data = {}
        """ Use EntryField classes to set up the form, along with a submit button """
        self.data['Name'] = entry_field.EntryField(self, label='Name')
        self.data['Name'].grid(row=1, column=0, pady=2)

        self.data['Email'] = entry_field.EntryField(self, label='Email')
        self.data['Email'].grid(row=2, column=0, pady=2)

        self.data['Street'] = entry_field.EntryField(
            self, label='Street Address')
        self.data['Street'].grid(row=3, column=0, pady=2)

        self.data['Postal'] = entry_field.EntryField(self, label='Postal')
        self.data['Postal'].grid(row=4, column=0, pady=2)

        self.data['City'] = entry_field.EntryField(self, label='City')
        self.data['City'].grid(row=5, column=0, pady=2)

        self.data['phone_number'] = entry_field.EntryField(self, label='PhoneNumber')
        self.data['phone_number'].grid(row=6, column=0, pady=2)

        self.data['message'] = entry_field.EntryField(self, label='message')
        self.data['message'].grid(row=7, column=0, pady=2)

        self.Button1 = tk.Button(self, text='Update', activebackground="green",
                                 activeforeground="blue", command=self.submit)
        self.Button1.grid(row=8, column=0, pady=10)

        button = tk.Button(self, text="Return to the Contact page",
                           command=lambda: controller.show_frame("ContactForms"))
        button.grid(row=9, column=0)

    def update(self, rid):
        record = self.controller.data.get_record(rid)
        # expand this by adding each of the separate field names
        # or come up with an introspective method (for key in ..)
        self.data['Name'].dataentry.set(record.name)
        self.data['Email'].dataentry.set(record.email)

        self.data['Street'].dataentry.set(record.address.street)
        self.data['Postal'].dataentry.set(record.address.postal)
        self.data['City'].dataentry.set(record.address.city)
        self.data['phone_number'].dataentry.set(record.address.phone_number)
        self.data['message'].dataentry.set(record.address.message)
        self.contact = self.persist.get_record(rid)

    def submit(self):
        ''' grab the text placed in the entry widgets accessed through the dict
        '''
        self.contact.name = self.data['Name'].get()
        self.contact.email = self.data['Email'].get()
        if not hasattr(self.contact, 'address'):
            self.contact.address = Address()
        self.contact.address.street = self.data['Street'].get()
        self.contact.address.city = self.data['City'].get()
        self.contact.address.phone_number = self.data['phone_number'].get()
        self.contact.address.message = self.data['message'].get()
        self.contact.address.postal = self.data['Postal'].get()

        self.persist.save_record(self.contact)


class CreationPage(tk.Frame):
    ''' provides a form for creating a new Contact
    '''

    def __init__(self, parent, controller, persist=None):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Create New Entry",
                         font=controller.title_font)
        label.grid(row=0, column=0)
        # this object is the data persistence model
        self.persist = persist
        # this empty dict will hold each of the data entry fields
        self.data = {}
        """ Use EntryField classes to set up the form, along with a submit button """
        self.data['Name'] = entry_field.EntryField(self, label='Name')
        self.data['Name'].grid(row=1, column=0, pady=2)

        self.data['Email'] = entry_field.EntryField(self, label='Email')
        self.data['Email'].grid(row=2, column=0, pady=2)

        self.data['Street'] = entry_field.EntryField(
            self, label='Street Address')
        self.data['Street'].grid(row=3, column=0, pady=2)

        self.data['Postal'] = entry_field.EntryField(self, label='Postal')
        self.data['Postal'].grid(row=4, column=0, pady=2)

        self.data['City'] = entry_field.EntryField(self, label='City')
        self.data['City'].grid(row=5, column=0, pady=2)

        self.data['phone_number'] = entry_field.EntryField(self, label='PhoneNumber')
        self.data['phone_number'].grid(row=6, column=0, pady=2)

        self.data['message'] = entry_field.EntryField(self, label='message')
        self.data['message'].grid(row=7, column=0, pady=2)

        self.Button1 = tk.Button(self, text='Submit', activebackground="green",
                                 activeforeground="blue", command=self.submit)
        self.Button1.grid(row=8, column=0, pady=10)

        button = tk.Button(self, text="Return to the Contact page",
                           command=lambda: controller.show_frame("ContactForms"))
        button.grid(row=9, column=0)

    def reset(self):
        ''' on every new entry, blank out the fields
        '''
        for key in self.data:
            self.data[key].reset()

    def update(self):
        self.reset()

    def submit(self):
        ''' make a new contact based on the form
        '''
        c = Contact(name=self.data['Name'].get(),
                    email=self.data['Email'].get())
        a = Address(street=self.data['Street'].get(),
                    city=self.data['City'].get(),
                    postal=self.data['Postal'].get(),
                    phonenumber=self.data['phone_number'].get(),
                    message=self.data['message'].get())

        c.add_address(a)
        self.persist.save_record(c)
        self.update()


if __name__ == "__main__":
    app = App()
    app.title("Contact form app")
    app.mainloop()
