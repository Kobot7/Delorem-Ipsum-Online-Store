import random
class Product:
    def __init__(self, productName, brand, thumbnail, subCategory, price, activated, quantity):
        self.set_product_name(productName)
        self.set_brand(brand)
        self.set_thumbnail(thumbnail)
        self.set_sub_category(subCategory)
        self.set_price(price)
        self.set_activated(activated)
        self.set_quantity(quantity)
        self.__serial_no = random.randint(100000, 999999)

    # Accessors
    def get_product_name(self):
        return self.__productName

    def get_brand(self):
        return self.__brand

    def get_thumbnail(self):
        return self.__thumbnail

    def get_sub_category(self):
        return self.__subCategory

    def get_serial_no(self):
        return self.__serial_no

    def get_price(self):
        return self.__price

    def get_activated(self):
        return self.__activated

    def get_quantity(self):
        return self.__quantity

    # Mutators
    def set_product_name(self, productName):
        self.__productName = productName

    def set_brand(self, brand):
        self.__brand = brand

    def set_thumbnail(self, thumbnail):
        self.__thumbnail = thumbnail

    def set_sub_category(self, subCategory):
        self.__subCategory = subCategory

    def set_serial_no(self, serial_no):
        self.__serial_no = serial_no

    def set_price(self, price):
        self.__price = price

    def set_activated(self, activated):
        self.__activated = activated

    def set_quantity(self, quantity):
        self.__quantity = quantity
