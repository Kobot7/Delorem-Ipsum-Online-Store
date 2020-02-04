class Discount:
    def __init__(self, code, condition, expiry_date):
        self.set_code(code)
        self.set_condition(condition)
        self.set_expiry_date(expiry_date)

    def set_code(self, code):
        self.__code = code

    def set_condition(self, condition):
        self.__condition = condition

    def set_expiry_date(self, expiry_date):
        self.__expiry_date = expiry_date

    def get_code(self,code):
        return self.__code

    def get_condition(self):
        return self.__condition

    def get_expiry_date(self):
        return self.__expiry_date

class AmountDiscount(Discount):
    def __init__(self, code, condition, expiry_date, discount_amount):
        super().__init__(code, condition,expiry_date)
        self.set_discount_amount(discount_amount)

    def set_discount_amount(self, discount_amount):
        self.__discount_amount = discount_amount

    def get_discount_amount(self):
        return self.__discount_amount

class PercentageDiscount(Discount):
    def __init__(self, code, condition, expiry_date, discount_percentage):
        super().__init__(code, condition, expiry_date)
        self.set_discount_percentage(discount_percentage)

    def set_discount_percentage(self, discount_percentage):
        self.__discount_percentage = discount_percentage

    def get_discount_percentage(self):
        return self.__discount_percentage
