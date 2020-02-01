import random
import shelve
from Functions import*
from StorageClass import*

class User:
    def __init__(self, username, password, email):
        self.set_user_id()
        self.set_username(username)
        self.set_password(password)
        self.set_email(email)
        # self.set_profile_pic(r"..\static\images\default-profile-picture1.jpg")
        self.__phone = ""
        self.__address = ""
        self.__shopping_cart = {}
        self.__wishlist = {}
        self.__transactions = []

    def set_user_id(self):
        user_id = random.randint(0, 9999999999999999999999999)
        db = shelve.open('storage.db')
        usersDict = {}
        try:
            usersDict = db['Users']
        except:
            print("This is an error in User.py")
        current = []
        for user in usersDict:
            id = user
            current.append(id)
        same = True
        while same:
            if user_id in current:
                user_id = random.randint(0, 9999999999999999999999999)
            else:
                same = False
                self.__user_id = str(user_id)

    def set_username(self, username):
        self.__username = username

    def set_password(self, password):
        self.__password = password

    def set_profile_pic(self, pic):
        self.__profile_pic = pic

    def set_phone(self, phone):
        self.__phone = phone

    def set_wishlist(self, wishlist):
        self.__wishlist = wishlist

    def set_shopping_cart(self, shopping_cart):
        self.__shopping_cart = shopping_cart

    def set_address(self, address):
        self.__address = address

    def set_email(self, email):
        self.__email = email

    def set_transactions(self, transactions):
        self.__transactions.append(transactions)

    def get_user_id(self):
        return self.__user_id

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password

    # def get_profile_pic(self):
    #     return self.__profile_pic

    def get_phone(self):
        return self.__phone

    def get_wishlist(self):
        return self.__wishlist

    def get_shopping_cart(self):
        return self.__shopping_cart

    def get_address(self):
        return self.__address

    def get_email(self):
        return self.__email

    def get_transactions(self):
        return self.__transactions

    def add_to_wishlist(self, item):
        wishlist = self.get_wishlist()
        serial_no = item.get_serial_no()
        empty = not bool(wishlist)
        if empty == True:
            wishlist[serial_no] = item
        else:
            for key in wishlist:
                same = False
                if key == serial_no:
                    same = True
                    break
                else:
                    same = False
            if same == False:
                wishlist[serial_no] = item
        self.set_wishlist(wishlist)

    def remove_from_wishlist(self, item):
        wishlist = self.get_wishlist()
        serial_no = item.get_serial_no()
        del wishlist[serial_no]
        self.set_wishlist(wishlist)

    def default_wishlist(self):
        db = shelve.open('storage.db')
        productsDict = {}
        try:
            productsDict = db['Products']
        except:
            print("Error retrieving products")
        wishlist = {}
        for key in productsDict:
            product = productsDict.get(key)
            wishlist[key] = product
        self.set_wishlist(wishlist)
        return self.__wishlist

    def add_to_cart(self, item):
        cart = self.get_shopping_cart()
        serial_no = item.get_serial_no()
        if not bool(cart):
            cart[serial_no] = item
        else:
            for key in cart:
                same = False
                if key == serial_no:
                    same = True
                    break
                else:
                    same = False
            if same == False:
                cart[serial_no] = item
        self.set_shopping_cart(cart)

    def remove_from_cart(self, item):
        cart = self.get_shopping_cart()
        serial_no = item.get_serial_no()
        del cart[serial_no]
        self.set_shopping_cart(cart)
