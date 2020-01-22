import random
class Delivery:
    def __init__(self, street_name, postal_code, unit_no, date, time):
        self.__street_name = street_name
        self.__postal_code = postal_code
        self.__unit_no = unit_no
        self.__date = date
        self.__time = time
        self.__id = random.randint(100000, 999999)

    def get_street_name(self):
        return self.__street_name

    def get_postal_code(self):
        return self.__postal_code

    def get_unit_no(self):
        return self.__unit_no

    def get_date(self):
        return self.__date

    def get_time(self):
        return self.__time

    def get_id(self):
        return self.__id


    def set_street_name(self, street_name):
        self.__street_name = street_name

    def set_postal_name(self, postal_code):
        self.__postal_code = postal_code

    def set_unit_no(self, unit_no):
        self.__unit_no = unit_no

    def set_date(self, date):
        self.__date = date

    def set_time(self, time):
        self.__time = time
