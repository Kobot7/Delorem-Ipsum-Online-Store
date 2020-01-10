class Product:
    def __init__(self, productName, brand, thumbnail, subCategory, serialNo, price, activated, quantity):
        self.__productName = productName
        self.__brand = brand
        self.__thumbnail = thumbnail
        self.__subCategory = subCategory
        self.__serialNo = serialNo
        self.__price = price
        self.__activated = activated
        self.__quantity = quantity

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

    def set_serial_no(self, serialNo):
        self.__serialNo = serialNo

    def set_price(self, price):
        self.__price = price

    def set_activated(self, activated):
        self.__activated = activated

    def set_quantity(self, quantity):
        self.__quantity = quantity
