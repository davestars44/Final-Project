import shelve
import sqlite3


class Storage():
    FILENAME = "Contactform.db"

    def __init__(self):
        self.conn = sqlite3.connect(self.FILENAME)
        self.data_access = self.conn.cursor()


    def get_record(self, rid):

        self.data_access.execute(
            """SELECT * from contacts WHERE contact_id = ?;""", (rid,))
        row = self.data_access.fetchone()

        contact = Contact(row[1], row[2], row[0])

        self.data_access.execute(
            """SELECT * from addresses WHERE address_id = ?;""", (row[3],))
        row = self.data_access.fetchone()
        contact.address = Address(row[1], row[2], row[3], row[4],row [5],row[0])
        return contact

    def get_all_records(self):
        """ returns all records stored
        """
        self.data_access.execute("""SELECT * from contacts;""")
        contacts = []
        for row in self.data_access:
            # index into tuple using position, id is last
            contacts.append(
                Contact(row[1], row[2], row[0]))
        return contacts

    def save_record(self, record):
        #adds a record

        # see if it exists
        if record.address.a_id == 0:
            self.data_access.execute("""INSERT INTO addresses(street, postal, city, phonenumber,message) VALUES (?,?,?,?,?)
            """, (record.address.street, record.address.postal, record.address.city, record.address.phone_number, record.address.message))
            record.address.a_id = self.data_access.lastrowid
        else:
            self.data_access.execute("""UPDATE addresses SET street = ?, postal = ?, city = ?, phonenumber = ?,message = ?
            WHERE address_id = ?""", (record.address.street, record.address.postal, record.address.city, record.address.phone_number, record.address.message, record.address.a_id))

        if record.rid == 0:
            self.data_access.execute("""INSERT INTO contacts(name,email,address_id) VALUES (?,?,?)
            """, (record.name, record.email, record.address.a_id))
            record.rid = self.data_access.lastrowid
        else:
            self.data_access.execute("""UPDATE contacts SET name = ?, email = ?, address_id = ?
            WHERE contact_id = ?""", (record.name, record.email, record.address.a_id, record.rid))
        self.conn.commit()

    def get_all_sorted_records(self):
        return sorted(self.get_all_records(), key=lambda x: x.rid)

    def delete_record(self, rid):
        # deletes
        self.data_access.execute("""DELETE FROM contacts WHERE contact_id = ?""",
                                 (int(rid),))
        self.conn.commit()

    def cleanup(self):
        ''' call this before the app closes to ensure data is stored properly
        '''
        if (self.data_access):
            self.conn.commit()
            self.data_access.close()


class ShelveStorage():
    FILENAME = "project_data.db"

    def __init__(self):
        # using writeback is slower but avoids some weird caching issues
        self.data_access = shelve.open(self.FILENAME, writeback=True)

    def get_record(self, rid):
        ''' return a single record identified by the record id
        '''
        record_id = "record" + str(rid)
        return self.data_access[record_id]

    def get_all_records(self):
        ''' return all records stored in the database
        '''
        return list(self.data_access.values())

    def save_record(self, record):
        ''' add a record represented by a dict with a new id
        '''
        # if it's still 0 then it's a new record, otherwise it's not
        if record.rid == 0:
            record.rid = self.get_new_id()

        record_key = "record" + str(record.rid)

        self.data_access[record_key] = record

    def get_all_sorted_records(self):
        return sorted(self.get_all_records(), key=lambda x: x.rid)

    def delete_record(self, rid):
        del self.data_access["record" + str(rid)]

    def get_new_id(self):
        all_sorted_records = self.get_all_sorted_records()
        if len(all_sorted_records) == 0:
            return 1
        else:
            return int(self.get_all_sorted_records()[-1].rid) + 1
# checks what is the safe number

    def cleanup(self):
        self.data_access.close()


class Contact():
    def __init__(self, name="", email="", rid=0):
        self.rid = rid
        self.name = name
        self.email = email

    def add_address(self, a):
        self.address = a

    def __str__(self):
        if self.address:
            return f'Contact#: {self.rid}; Name: {self.name}, Email: {self.email}, {self.address}'
        else:
            return f'Contact#: {self.rid}; Name: {self.name}, Email: {self.email}'


class Address():
    def __init__(self, street="", postal="", city="",phonenumber ="",message ="", a_id=0):
        self.street = street
        self.postal = postal
        self.city = city
        self.phone_number = phonenumber
        self.message = message
        self.a_id = 0

    def __str__(self):
        return f'Address: {self.street}; Postal: {self.postal}; City: {self.city}; phone number: {self.phone_number}; message: {self.message}'
