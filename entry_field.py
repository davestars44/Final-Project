import tkinter as tk
import sys


class EntryField(tk.Frame):
    def __init__(self, parent, label='', passwordField=False, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.data = tk.StringVar()
        self.label = label

        self.title = tk.Label(self, text=label, width=10)
        self.title.grid(row=0, column=0, padx=10, sticky=(tk.W + tk.E))
        if passwordField:
            self.field = tk.Entry(
                self, width=30, textvariable=self.data, show="*")
        else:
            self.field = tk.Entry(
                self, width=30, textvariable=self.data)
        self.field.grid(row=0, column=1, padx=15, sticky=(tk.W + tk.E))

    def reset(self):
        self.data.set("")

    def get(self):
        return self.data.get()
