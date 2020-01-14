class Product:
    def __init__(self, productName, brand, thumbnail, subCategory, price, description, activated, quantity):
        self.__productName = productName
        self.__brand = brand
        self.__thumbnail = thumbnail
        self.__subCategory = subCategory
        self.__serialNo = ''
        self.__price = float(price)
        self.__description = description
        self.__activated = activated
        self.__quantity = quantity
        self.__views = 0
        self.__purchases = 0

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
        return self.__serialNo

    def get_price(self):
        return '%.2f' %float(self.__price)

    def get_description(self):
        return self.__description

    def get_activated(self):
        return self.__activated

    def get_quantity(self):
        return self.__quantity

    def get_views(self):
        return self.__views

    def get_purchases(self):
        return self.__purchases

    # Mutators
    def set_product_name(self, productName):
        self.__productName = productName

    def set_brand(self, brand):
        self.__brand = brand

    def set_thumbnail(self, thumbnail):
        self.__thumbnail = thumbnail

    def set_sub_category(self, subCategory):
        self.__subCategory = subCategory

    def set_serial_no(self, serialNo):
        self.__serialNo = serialNo

    def set_price(self, price):
        self.__price = price

    def set_description(self, description):
        self.__description = description

    def set_activated(self, activated):
        self.__activated = activated

    def set_quantity(self, quantity):
        self.__quantity = quantity

    def increase_views(self):
        self.__views += 1

    def increase_purchases(self, amount):
        self.__purchases += int(amount)
