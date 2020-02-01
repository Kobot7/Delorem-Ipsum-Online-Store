import random
class Transaction:
    def __init__(self, name, phone, email, total, items, payment_mode, credit_card_number, credit_card_expiry, credit_card_cvv ):
        self.set_name(name)
        self.set_phone(phone)
        self.set_email(email)
        self.set_total(total)
        self.set_items(items)
        self.set_payment_mode(payment_mode)
        self.set_credit_card_number(credit_card_number)
        self.set_credit_card_expiry(credit_card_expiry)
        self.set_credit_card_cvv(credit_card_cvv)
        self.__id = random.randint(100000, 999999)

    def set_name(self, name):
        self.__name = name

    def set_phone(self, phone):
        self.__phone = phone

    def set_email(self, email):
        self.__email = email

    def set_total(self, total):
        self.__total = total

    def set_items(self, items):
        self.__items = items

    def set_payment_mode(self, payment_mode):
        self.__payment_mode = payment_mode

    def set_credit_card_number(self, credit_card_number):
        self.__credit_card_number = credit_card_number

    def set_credit_card_expiry(self, expiry):
        self.__expiry = expiry

    def set_credit_card_cvv(self, cvv):
        self.__cvv = cvv

    def get_name(self):
        return self.__name

    def get_phone(self):
        return self.__phone

    def get_email(self):
        return self.__email

    def get_total(self):
        return self.__total

    def get_items(self):
        return self.__items

    def get_payment_mode(self):
        return self.__payment_mode

    def get_credit_card_number(self):
        return self.__credit_card_number

    def get_credit_card_expiry(self):
        return self.__credit_card_expiry

    def get_credit_card_cvv(self):
        return self.__credit_card_cvv

    def get_id(self):
        return self.__id


class Delivery(Transaction):
    def __init__(self,name, phone, email, total, items, payment_mode, credit_card_number, credit_card_expiry, credit_card_cvv, street_name, postal_code, unit_no):
        super().__init__(name, phone, email, total, items, payment_mode, credit_card_number, credit_card_expiry, credit_card_cvv)
        self.__street_name = street_name
        self.__postal_code = postal_code
        self.__unit_no = unit_no

    def set_street_name(self, street_name):
        self.__street_name = street_name

    def set_postal_code(self, postal_code):
        self.__postal_code = postal_code

    def set_unit_no(self, unit_no):
        self.__unit_no = unit_no

    def get_street_name(self):
        return self.__street_name

    def get_postal_code(self):
        return self.__postal_code

    def get_unit_no(self):
        return self.__unit_no

class Collection(Transaction):
    def __init__(self,name, phone, email, total, items, payment_mode, credit_card_number, credit_card_expiry, credit_card_cvv, date, time):
        super().__init__(name, phone, email, total, items, payment_mode, credit_card_number, credit_card_expiry, credit_card_cvv)
        self.__date = date
        self.__time = time

    def set_date(self, date):
        self.__date = date

    def set_time(self, time):
        self.__time = time

    def get_date(self):
        return self.__date

    def get_time(self):
        return self.__time
