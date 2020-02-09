class Discount:
    def __init__(self, code, condition, start_date, expiry_date, status, used):
        self.set_code(code)
        self.set_condition(condition)
        self.set_start_date(start_date)
        self.set_expiry_date(expiry_date)
        self.set_status(status)
        self.set_used(used)

    def set_code(self, code):
        self.__code = code

    def set_condition(self, condition):
        self.__condition = condition

    def set_start_date(self, start_date):
        self.__start_date = start_date

    def set_expiry_date(self, expiry_date):
        self.__expiry_date = expiry_date

    def set_status(self,status):
        self.__status = status

    def set_used(self,used):
        self.__used = used

    def get_code(self):
        return self.__code

    def get_condition(self):
        return self.__condition

    def get_start_date(self):
        return self.__start_date

    def get_expiry_date(self):
        return self.__expiry_date

    def get_status(self):
        return self.__status
     def get_used(self):
         return self.__status

class AmountDiscount(Discount):
    def __init__(self, code, condition, start_date, expiry_date, status, used, discount_amount):
        super().__init__(code, condition, start_date, expiry_date, status, used)
        self.set_discount_amount(discount_amount)

    def set_discount_amount(self, discount_amount):
        self.__discount_amount = discount_amount

    def get_discount_amount(self):
        return self.__discount_amount

class PercentageDiscount(Discount):
    def __init__(self, code, condition, start_date, expiry_date,status, used, discount_percentage):
        super().__init__(code, condition, start_date, expiry_date), status, used
        self.set_discount_percentage(discount_percentage)

    def set_discount_percentage(self, discount_percentage):
        self.__discount_percentage = discount_percentage

    def get_discount_percentage(self):
        return self.__discount_percentage
