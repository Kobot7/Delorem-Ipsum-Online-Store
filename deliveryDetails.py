import random
class Transaction:
    def __init__(self, dateOfOrder, name, phone, email, total, deducted, discount, items, payment_mode, credit_card_number, credit_card_expiry, credit_card_cvv ):
        self.__completed = False
        self.__date_of_order = dateOfOrder
        self.set_name(name)
        self.set_phone(phone)
        self.set_email(email)
        self.set_total(total)
        self.set_deducted(deducted)
        self.set_discount(discount)
        self.set_items(items)
        self.set_payment_mode(payment_mode)
        self.set_credit_card_number(credit_card_number)
        self.set_credit_card_expiry(credit_card_expiry)
        self.set_credit_card_cvv(credit_card_cvv)
        self.__id = random.randint(100000, 999999)

    def set_completion(self, status):
        self.__completed = status

    def set_name(self, name):
        self.__name = name

    def set_phone(self, phone):
        self.__phone = phone

    def set_email(self, email):
        self.__email = email

    def set_total(self, total):
        self.__total = total

    def set_deducted(self, deducted):
        self.__deducted = deducted

    def set_discount(self, discount):
        self.__discount = discount

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

    def get_completion(self):
        return self.__completed

    def get_date_of_order(self):
        return self.__date_of_order

    def get_name(self):
        return self.__name

    def get_phone(self):
        return self.__phone

    def get_email(self):
        return self.__email

    def get_total(self):
        return '%.2f' %float(self.__total)

    def get_deducted(self):
        return self.__deducted

    def get_discount(self):
        return self.__discount

    def get_items(self):
        return self.__items

    def get_payment_mode(self):
        return self.__payment_mode

    def get_credit_card_number(self):
        return self.__credit_card_number

    def get_credit_card_expiry(self):
        return self.__expiry

    def get_credit_card_cvv(self):
        return self.__cvv

    def get_id(self):
        return self.__id


class Delivery(Transaction):
    def __init__(self, dateOfOrder, name, phone, email, total, deducted, discount, items, payment_mode, credit_card_number, credit_card_expiry, credit_card_cvv, street_name, postal_code, unit_no):
        super().__init__(dateOfOrder, name, phone, email, total, deducted, discount, items, payment_mode, credit_card_number, credit_card_expiry, credit_card_cvv)
        self.__street_name = street_name
        self.__postal_code = postal_code
        self.__unit_no = unit_no
        self.__type = "delivery"

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

    def get_type(self):
        return self.__type

class Collection(Transaction):
    def __init__(self, dateOfOrder, name, phone, email, total, deducted, discount, items, payment_mode, credit_card_number, credit_card_expiry, credit_card_cvv, date, time):
        super().__init__(dateOfOrder, name, phone, email, total, deducted, discount, items, payment_mode, credit_card_number, credit_card_expiry, credit_card_cvv)
        self.__date = date
        self.__time = time
        self.__type = "collection"

    def set_date(self, date):
        self.__date = date

    def set_time(self, time):
        self.__time = time

    def get_date(self):
        return self.__date

    def get_time(self):
        return self.__time

    def get_type(self):
        return self.__type
