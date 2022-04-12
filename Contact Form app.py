# imports
import tkinter as tk
from tkinter import font as tkfont
import tkinter.ttk as ttk  # treeview
import entry_field
from models import *
import pygame
from pygame import mixer

# inspiration from demo app because i was going to make a contact form
# startup windows noise from the computer files
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
startup = pygame.mixer.Sound("Windows XP Startup.wav")
startup.set_volume(0.25)
# noise for confirmed submission
ding = pygame.mixer.Sound("Ding.wav")
ding.set_volume(0.25)


class App(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # main database access object
        self.data = Storage()
        #  a single font to be used throughout the app
        self.title_font = tkfont.Font(
            family='Times New Roman', size=18, weight="bold", slant="italic")
        self.small_font = tkfont.Font(
            family='Times New Roman', size=10, weight="bold", slant="italic")

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
        '''Show a frame of the page name'''
        frame = self.frames[page_name]
        if not rid == 0:
            frame.update(rid)
        else:
            frame.update()
        frame.tkraise()


class LoginPage(tk.Frame):
    ''' simulates login'''

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
                               command=lambda: [controller.show_frame("ContactForms"), startup.play()])
        new_button.grid(column=0)


class ContactForms(tk.Frame):

    def __init__(self, parent, controller, persist=None):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.config(bg='#4a7a8c')
        label = tk.Label(self, text="Contacts Forms",
                         font=controller.title_font)
        label.grid(column=0, pady=10)

        ''' '''
        # set up the treeview
        contact_table = tk.Frame(self, width=500)
        contact_table.grid(column=0)
        scrollbarx = tk.Scrollbar(contact_table, orient=tk.HORIZONTAL)
        scrollbary = tk.Scrollbar(contact_table, orient=tk.VERTICAL)
        self.tree = ttk.Treeview(contact_table, columns=("id number", "name", "email"),
                                 selectmode="extended", yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
        scrollbary.config(command=self.tree.yview)
        scrollbary.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbarx.config(command=self.tree.xview)
        scrollbarx.pack(side=tk.BOTTOM, fill=tk.X)
        # headings and columns
        self.tree.heading('id number', text="ID Number", anchor=tk.W)
        self.tree.heading('name', text="Name", anchor=tk.W)
        self.tree.heading('email', text="Email", anchor=tk.W)
        self.tree.column('#0', stretch=tk.NO, minwidth=0, width=0)
        self.tree.column('#1', stretch=tk.NO, minwidth=0, width=120)
        self.tree.column('#2', stretch=tk.NO, minwidth=0, width=250)
        self.tree.column('#3', stretch=tk.NO, minwidth=0, width=300)
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

        edit_button = tk.Button(self, text="Edit",
                                command=self.edit_selected)
        edit_button.grid(column=0)

        delete_button = tk.Button(self, text="Delete",
                                  command=self.delete_selected)
        delete_button.grid(column=0)

        new_button = tk.Button(self, text="Add Record",
                               command=lambda: controller.show_frame("CreationPage"))
        new_button.grid(column=0)
        exit_button = tk.Button(self, text="Exit", command=self.quit)
        exit_button.grid(column=0)

    def edit_selected(self):
        idx = self.selected[0]
        record_id = self.tree.item(idx)['values'][0]
        self.controller.show_frame("ReadPage", record_id)

    def on_select(self, event):
        ''' highlighted items that you click on
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
        ''' to refresh the treeview'''
        for row in self.tree.get_children():
            self.tree.delete(row)
        all_records = self.persist.get_all_sorted_records()
        for record in all_records:
            self.tree.insert("", 0, values=(
                record.rid, record.name, record.email))


class ReadPage(tk.Frame):

    def __init__(self, parent, controller, persist=None):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Edit Entry",
                         font=controller.title_font)
        label.grid(row=0, column=0)
        label = tk.Label(self, text="please fill every field and under message what you need",
                         font=controller.small_font)
        label.grid(row=1, column=0)
        self.persist = persist
        # this empty dict that holds the data entries
        self.data = {}
        """ Use EntryField classes to set up the form, along with a submit button """
        self.data['Name'] = entry_field.EntryField(self, label='Name')
        self.data['Name'].grid(row=2, column=0, pady=2)

        self.data['Email'] = entry_field.EntryField(self, label='Email')
        self.data['Email'].grid(row=3, column=0, pady=2)

        self.data['Street'] = entry_field.EntryField(
            self, label='Street Address')
        self.data['Street'].grid(row=4, column=0, pady=2)

        self.data['Postal'] = entry_field.EntryField(self, label='Postal')
        self.data['Postal'].grid(row=5, column=0, pady=2)

        self.data['City'] = entry_field.EntryField(self, label='City')
        self.data['City'].grid(row=6, column=0, pady=2)

        self.data['phone_number'] = entry_field.EntryField(self, label='PhoneNumber')
        self.data['phone_number'].grid(row=7, column=0, pady=2)

        self.data['message'] = entry_field.EntryField(self, label='message')
        self.data['message'].grid(row=8, column=0, pady=2)

        self.Button1 = tk.Button(self, text='Update', activebackground="green",
                                 activeforeground="blue", command=self.submit)
        self.Button1.grid(row=9, column=0, pady=10)

        button = tk.Button(self, text="Return to the Contact page",
                           command=lambda: controller.show_frame("ContactForms"))
        button.grid(row=10, column=0)

    def update(self, rid):
        record = self.controller.data.get_record(rid)
        self.data['Name'].data.set(record.name)
        self.data['Email'].data.set(record.email)

        self.data['Street'].data.set(record.address.street)
        self.data['Postal'].data.set(record.address.postal)
        self.data['City'].data.set(record.address.city)
        self.data['phone_number'].data.set(record.address.phone_number)
        self.data['message'].data.set(record.address.message)
        self.contact = self.persist.get_record(rid)

    def submit(self):
        ''' gets the text placed in the entry widgets'''
        self.contact.name = self.data['Name'].get()
        self.contact.email = self.data['Email'].get()
        if not hasattr(self.contact, 'address'):
            self.contact.address = Address()
        self.contact.address.street = self.data['Street'].get()
        self.contact.address.city = self.data['City'].get()
        self.contact.address.phone_number = self.data['phone_number'].get()
        self.contact.address.message = self.data['message'].get()
        self.contact.address.postal = self.data['Postal'].get()
        ding.play()
        self.persist.save_record(self.contact)


class CreationPage(tk.Frame):
    ''' for creating a form'''

    def __init__(self, parent, controller, persist=None):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Create New Entry",
                         font=controller.title_font)
        label.grid(row=0, column=0)
        label = tk.Label(self, text="please fill every field and under message what you need",
                         font=controller.small_font)
        label.grid(row=1, column=0)
        self.persist = persist
        self.data = {}
        """ Use EntryField classes to set up the form with a submit button """
        self.data['Name'] = entry_field.EntryField(self, label='Name')
        self.data['Name'].grid(row=2, column=0, pady=2)

        self.data['Email'] = entry_field.EntryField(self, label='Email')
        self.data['Email'].grid(row=3, column=0, pady=2)

        self.data['Street'] = entry_field.EntryField(
            self, label='Street Address')
        self.data['Street'].grid(row=4, column=0, pady=2)

        self.data['Postal'] = entry_field.EntryField(self, label='Postal')
        self.data['Postal'].grid(row=5, column=0, pady=2)

        self.data['City'] = entry_field.EntryField(self, label='City')
        self.data['City'].grid(row=6, column=0, pady=2)

        self.data['phone_number'] = entry_field.EntryField(self, label='PhoneNumber')
        self.data['phone_number'].grid(row=7, column=0, pady=2)

        self.data['message'] = entry_field.EntryField(self, label='message')
        self.data['message'].grid(row=8, column=0, pady=2)

        self.Button1 = tk.Button(self, text='Submit', activebackground="green",
                                 activeforeground="blue", command=self.submit)
        self.Button1.grid(row=9, column=0, pady=10)

        button = tk.Button(self, text="Return to the Contact page",
                           command=lambda: controller.show_frame("ContactForms"))
        button.grid(row=10, column=0)

    def reset(self):
        for key in self.data:
            self.data[key].reset()

    def update(self):
        self.reset()

    def submit(self):
        ''' creates a new contact using the form information'''
        c = Contact(name=self.data['Name'].get(),
                    email=self.data['Email'].get())
        a = Address(street=self.data['Street'].get(),
                    city=self.data['City'].get(),
                    postal=self.data['Postal'].get(),
                    phonenumber=self.data['phone_number'].get(),
                    message=self.data['message'].get())
        ding.play()
        c.add_address(a)
        self.persist.save_record(c)
        self.update()


if __name__ == "__main__":
    app = App()
    app.title("Contact form app")
    app.mainloop()
