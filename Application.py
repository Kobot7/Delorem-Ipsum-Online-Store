import shelve, string, random
from flask import Flask, render_template, request, redirect, url_for
from Forms import *
from StorageClass import *
from Functions import *
from User import *
from deliveryDetails import *
from Discount import *
from feedback import *
from datetime import date
import re


# Image download
from werkzeug.utils import secure_filename
import os
from pathlib import Path

# Graphing
import json, plotly
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import flask_excel as excel


# Flask mail
from flask_mail import Mail, Message
import sys
import asyncio
from threading import Thread

# print('MAIL_PASSWORD' in os.environ)

app = Flask(__name__, static_url_path='/static')
app.config.update(
    MAIL_SERVER= 'smtp.office365.com',
    MAIL_PORT= 587,
    MAIL_USE_TLS= True,
    MAIL_USE_SSL= False,
	MAIL_USERNAME = 'deloremipsumonlinestore@outlook.com',
	# MAIL_PASSWORD = os.environ["MAIL_PASSWORD"],
	MAIL_DEBUG = True,
	MAIL_SUPPRESS_SEND = False,
    MAIL_ASCII_ATTACHMENTS = True
	)

mail = Mail(app)

def searchBar():
    return SearchBar(request.form)

def testing():
    productDict = {}
    db = shelve.open('storage.db', 'a')
    productDict = db['Products']
    for product in productDict:
        productDict[product].increase_purchases(random.randint(1,50))
        for x in range(random.randint(40,150)):
            productDict[product].increase_views()
    db['Products'] = productDict
    db.close()

@app.route('/search/<searchString>/<category>/<order>', methods=['GET', 'POST'])
def search(searchString, category, order):
    db = shelve.open('storage.db', 'r')
    try:
        Products = db["Products"]
    except:
        print("Error in retrieving products from shelve")

    try:
        current = db["Current User"]
        cart = current.get_shopping_cart()
        Items = len(cart)
    except:
        print("Error in retrieving current user")
        current = False
        Items = 0
    products = []
    for id in Products:
        product = Products[id]
        if searchString in product.get_product_name().lower() or searchString in product.get_brand().lower():
            if product.get_activated() == True:
                products.append(product)

    products = sort_by(products, category, order)

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        return redirect('/search/' + searchForm.search_input.data + '/view/descending')
    return render_template('search.html', productList=products, searchString=searchString, productCount=len(products), searchForm=searchForm, current=current, Items=len(cart))

# Homepage
@app.route('/home', methods=['GET', 'POST'])
def home():
    productDict = {}

    db = shelve.open('storage.db', 'c')
    try:
        current = db["Current User"]
        cart = current.get_shopping_cart()
        Items = len(cart)
    except:
        print("Error while retrieving current user: user not logged in")
        current = False
        Items = 0
    try:
        productDict = db['Products']
        db.close()
    except:
        print('Error in retrieving Products from storage.db.')
    productList = []
    for key in productDict:
        product = productDict[key]
        productList.append(product)


    purchasesList = sort_by(productList, 'purchase', 'descending')[:6]
    viewsList = sort_by(productList,'view','descending')[:6]

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        return redirect('/search/' + searchForm.search_input.data + '/view/descending')

    return render_template("home.html", current=current, searchForm=searchForm, purchasesList=purchasesList, viewsList=viewsList, Items=Items)

# Profile/Username
@app.route('/my-account/<username>', methods=['GET', 'POST'])
def view_profile(username):
    db = shelve.open("storage.db", "c")
    try:
        usersDict = db["Users"]
        namesDict = db["Usernames"]
        current = db["Current User"]
        cart = current.get_shopping_cart()
        Items = len(cart)
    except:
        print("Error while retrieving usersDict")
        return redirect(url_for("home"))

    editProfileForm = EditProfileForm(request.form)
    if request.method == "POST":
        current_id = current.get_user_id()
        del namesDict[current.get_username()]
        current.set_username(editProfileForm.username.data)
        current.set_address(editProfileForm.address.data)
        current.set_phone(editProfileForm.phone.data)
        current.set_email(editProfileForm.email.data)
        if current.get_password() == editProfileForm.password.data:
            if editProfileForm.newpassword.data != "":
                current.set_password(editProfileForm.newpassword.data)
                print("New password set for user " + current.get_username() + ", " + current.get_password() + ".")
            elif editProfileForm.newpassword.data == "":
                print("New password field was left empty.")
                print("No new password was set.")
        elif current.get_password() != editProfileForm.password.data:
            if editProfileForm.password.data == "":
                print("Current password field was left empty.")
            else:
                print("Current user password was incorrect.")
        else:
            print("\n\n\nAn unexpected error has occured.\n\n\n")

        usersDict[current_id] = current
        namesDict[current.get_username()] = current_id
        db["Users"] = usersDict
        db["Usernames"] = namesDict
        db["Current User"] = current


        searchForm = searchBar()
        if request.method == "POST" and searchForm.validate():
            print(searchForm.search_input.data)
        db.close()
        return render_template('my-account.html', current=current, name=current.get_username(), address=current.get_address(), phone=current.get_phone(), email=current.get_email(), searchForm=searchForm, Items=Items)
    else:
        searchForm = searchBar()
        if request.method == "POST" and searchForm.validate():
            print(searchForm.search_input.data)
        db.close()
        return render_template('my-account.html', current=current, name=current.get_username(), address=current.get_address(), phone=current.get_phone(), email=current.get_email(), searchForm=searchForm, Items=Items)

# Login/Register
@app.route('/login', methods=['GET', 'POST'])
def login():
    db = shelve.open("storage.db", "c")
    try:
        current = db["Current User"]
    except:
        current = ""
        print("Error in retrieving current user")
    if current == "":
        loginForm = LoginForm(request.form)
        registrationForm = RegistrationForm(request.form)
        if request.method == "POST" and registrationForm.validate():
            db = shelve.open('storage.db', 'c')
            namesDict = {}
            usersDict = {}
            try:
                usersDict = db['Users']
            except:
                print('Error while retrieving usersDict')
            try:
                namesDict = db['Usernames']
            except:
                print("Error while retrieving namesDict")

            unique_email = True
            valid_email_registration = True
            secure_pwd = True
            regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
            SpecialSym =['$', '@', '#', '%']

            for user in usersDict.values():
                #check email is correct format
                if not(re.search(regex, registrationForm.email.data)):
                    print("Invalid Email")
                    valid_email_registration = False
                    break
                    #check for registered email in system
                if registrationForm.email.data == user.get_email():
                    unique_email = False
                    print("Email in use, you cannot create an account with the same email.")
                    break
                    #check password meets minimum requirement for strong pwd
                if len(registrationForm.password.data) < 6:
                    print('length should be at least 6')
                    secure_pwd= False
                if not any(char.isdigit() for char in registrationForm.password.data):
                    print('Password should have at least one numeral')
                    secure_pwd = False
                if not any(char.isupper() for char in registrationForm.password.data):
                    print('Password should have at least one uppercase letter')
                    secure_pwd = False
                if not any(char.islower() for char in registrationForm.password.data):
                    print('Password should have at least one lowercase letter')
                    secure_pwd = False
                if not any(char in SpecialSym for char in registrationForm.password.data):
                    print('Password should have at least one of the symbols $@#')
                    secure_pwd = False

            if unique_email and valid_email_registration:
                U = User(registrationForm.username.data, registrationForm.password.data, registrationForm.email.data)
                usersDict[U.get_user_id()] = U
                namesDict[U.get_username()] = U.get_user_id()
                db['Users'] = usersDict
                db['Usernames'] = namesDict
                db.close()
                print("User created with name", U.get_username(), "id", U.get_user_id(),
                 "Password", U.get_password(), "and Email", U.get_email())

            else:
                searchForm = searchBar()
                if request.method == "POST" and searchForm.validate():
                    print(searchForm.search_input.data)
                return render_template("login.html", unique_email=unique_email, valid_email_registration=valid_email_registration, secure_pwd = secure_pwd, form=loginForm, form2=registrationForm, searchForm=searchForm)

        if request.method =="POST" and loginForm.validate():
            usersDict = {}
            namesDict = {}
            db = shelve.open('storage.db', 'r')
            try:
                usersDict = db["Users"]
            except:
                print("Error while retrieving usersDict")
            try:
                namesDict = db["Usernames"]
            except:
                print("Error while retrieving namesDict")

            if loginForm.username.data == "admin" and loginForm.password.data == "admin":
                return redirect('/dashboard/1')

            username_exist = False
            login_correct = False
            success_login = False

            for name in namesDict:
                if name == loginForm.username.data:
                    username_exist = True
                    username_id = namesDict[loginForm.username.data]
                    break

            searchForm = searchBar()
            if request.method == "POST" and searchForm.validate():
                print(searchForm.search_input.data)

            if username_exist:
                user_obj = usersDict[username_id]
                if user_obj.get_password() == loginForm.password.data:
                    db["Current User"] = user_obj
                    print("User successfully logged in")
                    success_login = True
                    return redirect(url_for("home"))
                else:
                    searchForm = searchBar()
                    if request.method == "POST" and searchForm.validate():
                        print(searchForm.search_input.data)
                    print("Credentials are incorrect.")
                    return render_template('login.html', username_correct=False,  unique_email=True, valid_email_registration=True, secure_pwd = True, form=loginForm, form2=registrationForm, searchForm=searchForm)
            else:
                searchForm = searchBar()
                if request.method == "POST" and searchForm.validate():
                    print(searchForm.search_input.data)
                print("User does not exist.")
                return render_template('login.html', username_correct=False,  unique_email=True, valid_email_registration=True, secure_pwd = True, form=loginForm, form2=registrationForm, searchForm=searchForm)

        else:
            searchForm = searchBar()
            if request.method == "POST" and searchForm.validate():
                print(searchForm.search_input.data)
            return render_template('login.html', username_correct=True,  unique_email=True, valid_email_registration=True, secure_pwd = True, form=loginForm, form2=registrationForm, searchForm=searchForm)
            print("Exception Error: navigating home.html to login.html")

        searchForm = searchBar()
        if request.method == "POST" and searchForm.validate():
            return redirect('/search/' + searchForm.search_input.data + '/view/descending')
        return render_template('login.html', username_correct=True,  unique_email=True, valid_email_registration=True, secure_pwd = True, form=loginForm, form2=registrationForm, searchForm=searchForm)
    else:
        return redirect(url_for("home"))

@app.route('/logout')
# @login_required
def logout():
    db = shelve.open("storage.db", "c")
    db["Current User"] = ""
    print("User logged out successfully")
    return redirect(url_for('home'))
# return render_template("home.html", current="", logged_out=True)

@app.route('/orderHistory')
def orderHistory():
    db = shelve.open("storage.db", "r")
    try:
        current = db["Current User"]
        cart = current.get_shopping_cart()
        Items = len(cart)
    except:
        current = False
        Items = 0
    db.close()
    searchForm = searchBar()
    #METHOD GET - history of order transaction
    return render_template('orderHistory.html', searchForm = searchForm, Items=Items, current = current)

@app.route('/mainCategory/<mainCategory>/<category>/<order>/', methods=['GET', 'POST'])
def mainCategory(mainCategory, category, order):
    db = shelve.open('storage.db', 'r')
    try:
        Products = db["Products"]
    except:
        print("Error in retrieving products from shelve")
    try:
        current = db["Current User"]
        Items = len(current.get_shopping_cart())
    except:
        print("Error in retrieving current user, subcat")
        current = False
        Items = 0

    db.close()

    products = []

    for id in Products:
        product = Products[id]
        if get_main_category(product.get_sub_category()).replace(' ','') == mainCategory:
            if product.get_activated() == True:
                products.append(product)

    products = sort_by(products, category, order)

    mainCategory = get_name_with_space(mainCategory)
    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        return redirect('/search/' + searchForm.search_input.data + '/view/descending')
    return render_template('mainCategory.html', productList=products, productCount=len(products), mainCategory=mainCategory, searchForm=searchForm, current=current, Items=Items)

# Supplements(one of the subsections)
@app.route('/subCategory/<subCategory>/<category>/<order>/', methods=['GET', 'POST'])
def subCategory(subCategory, category, order):
    db = shelve.open('storage.db', 'r')
    try:
        Products = db["Products"]
    except:
        print("Error in retrieving products from shelve")
    try:
        current = db["Current User"]
        Items = len(current.get_shopping_cart())
    except:
        print("Error in retrieving current user, subcat")
        current = False
        Items = 0

    db.close()

    products = []
    for id in Products:
        product = Products[id]
        if product.get_sub_category() == subCategory:
            if product.get_activated() == True:
                products.append(product)

    mainCategory = get_main_category(subCategory)
    products = sort_by(products, category, order)

    subCategory = get_name_with_space(subCategory)
    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        return redirect('/search/' + searchForm.search_input.data + '/view/descending')
    return render_template('subCategory.html', productList=products, subCategory=subCategory, productCount=len(products), mainCategory=mainCategory, searchForm=searchForm, current=current, Items=Items)

# Ribena(one of the products)
@app.route('/IndItem/<serialNo>', methods=['GET', 'POST'])
def IndItem(serialNo):
    db = shelve.open('storage.db','w')
    current = ""
    try:
        products = db['Products']
    except:
        print("Error while retrieving products from storage.")
    try:
        current = db['Current User']
        Items = len(current.get_shopping_cart())
    except:
        print("Unable to get the current dude!")
        Items = 0
    IndItem = products[serialNo]
    IndItem.increase_views()
    class QuantityForm(Form):
        quantity = IntegerField("Quantity", [validators.NumberRange(min=0, max=IndItem.get_quantity(), message="Please select a valid quantity. There are only " + str(IndItem.get_quantity()) + " of this product currently."), validators.DataRequired()])
    Quantity = QuantityForm(request.form)
    try:
        wishlist = current.get_wishlist()
        taken = False
        for serial_no in wishlist:
            if serial_no == serialNo:
                taken = True
                break
    except:
        taken = False
    db['Products'] = products
    db.close()
    subCategory = IndItem.get_sub_category()
    mainCategory = get_main_category(subCategory)
    relatedProducts = []
    for serial_no in products:
        if get_main_category(products[serial_no].get_sub_category()) == mainCategory:
            relatedProducts.append(products[serial_no])
    relatedProducts.remove(IndItem)
    related = []
    for i in range(4):
        max = len(relatedProducts)
        max -= 1
        number = random.randint(0,max)
        related.append(relatedProducts[number])
        relatedProducts.pop(number)
    searchForm = searchBar()
    # if request.method == "POST" and searchForm.validate():
    #     return redirect('/search/' + searchForm.search_input.data + '/view/descending')
    if request.method == "POST" and Quantity.validate():
        quantity = Quantity.quantity.data
        return redirect(url_for('addToCart', name = IndItem.get_product_name(), quantity = quantity))
    return render_template('IndItem.html', product=IndItem, mainCategory=mainCategory, searchForm=searchForm, current=current, taken=taken, related=related, Items=Items, QuantityForm = Quantity)

# Shopping Cart
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    discount=  ''
    new_total = ''
    Delivery = NoCollectForm(request.form)
    Discount = DiscountForm(request.form)
    db = shelve.open('storage.db','r')
    try:
        current = db['Current User']
        products = db["Products"]
    except:
        print('Error reading Current User.')
        current = False
        products = {}

    cart = current.get_shopping_cart()
    codes = current.get_discount_codes()
    db.close()
    cartList = []
    totalCost = 0
    for serial_no in cart:
        product = products[serial_no]
        totalCost += float(product.get_price())*int(cart[serial_no])
        product.set_quantity(cart[serial_no])
        cartList.append(product)
    totalCost = '%.2f' %float(totalCost)
    Items = len(cartList)

    if request.method == "POST" and Delivery.validate():
        NoCollect = Delivery.home_delivery.data
        if NoCollect == True:
            return redirect(url_for('checkout',delivery=NoCollect))
        else:
            searchForm = searchBar()
            # if request.method == "POST" and searchForm.validate():
            #     return redirect('/search/' + searchForm.search_input.data + '/view/descending')
            return redirect(url_for('checkout', delivery=False))
    #
    # if request.method == "POST" and Discount.validate():
    #     code = Discount.discount_code.data

    searchForm = searchBar()
    # discount = ''
    # if request.method == "POST" and searchForm.validate():
    #     return redirect('/search/' + searchForm.search_input.data + '/view/descending')
    # return render_template('cart.html', cartList=cartList, totalCost=totalCost, searchForm=searchForm, current=current, NoCollectForm = Delivery, Discount=Discount, codes=codes, Items = Items, discount=discount)
    return render_template('cart.html', cartList=cartList, totalCost=totalCost, searchForm=searchForm, current=current, NoCollectForm = Delivery, Discount=Discount, Items = Items, discount=discount, new_total= new_total)

@app.route('/useDiscount',  methods=['POST'])
def useDiscount():
    searchForm = searchBar()
    Delivery = NoCollectForm(request.form)
    Discount = DiscountForm(request.form)
    discount= ""
    current = ""
    valid_discount = {}
    users_codes = []
    new_total =0
    error_msg=''

    if request.method == "POST" and Discount.validate():
        print("YOOOOOOOOOOOOOOOOOOOOO")
        code = Discount.discount_code.data
        db = shelve.open('storage.db', 'c')
        valid_discount = {}
        try:
            print("Get current")
            current = db["Current User"]
        except:
            print("Error in retrieving current user from storage.db")

        users_codes = current.get_discount_codes()

        try:
            print("gettinng valid discounts")
            valid_discount = db["Valid Discount"]
        except:
            print("Error in retrieving valid discounts from storage.db")

        try:
            print("gettinng Products cuz we need em now")
            products = db["Products"]
        except:
            print("Error in retrieving valid discounts from storage.db")

        cart = current.get_shopping_cart()
        codes = current.get_discount_codes()
        db.close()
        cartList = []
        totalCost = 0
        for product in cart:
            item = products[product]
            totalCost += float(item.get_price()) * int(cart[product])
            cartList.append(item)
        totalCost = '%.2f' %float(totalCost)
        Items = len(cartList)

        #check use
        valid = False
        check_used = False
        empty = not bool(users_codes)

        if empty == True:
            print("check empty")
            check_used = False
        else:
            for used in users_codes:
                if used == code:
                    check_used = True
                    error_msg = "You have already used this code!"
                    break
                    return render_template('cart.html', cartList=cartList, totalCost=totalCost, current=current, NoCollectForm = Delivery, Discount=Discount, Items=Items, error_msg=error_msg, discount=discount, new_total=new_total , searchForm=searchForm)
                    # return render_template('cart.html', cartList=cartList, totalCost=totalCost, searchForm=searchForm, current=current, NoCollectForm = Delivery, Discount=Discount, Items = Items)

        amount_discounts = {}
        percentage_discounts = {}
        test_amount = valid_discount.get("Amount")
        if test_amount:
            amount_discounts = valid_discount["Amount"]
            for key in amount_discounts:
                if key == code:
                    valid = True
                    type = "amount"
                    discount_in_storage = amount_discounts[key]
                    break
        else:
            valid_discount["Amount"] = amount_discounts

        test_percentage = valid_discount.get("Percentage")
        if test_percentage:
            percentage_discounts = valid_discount["Percentage"]
            for key in percentage_discounts:
                if key == code:
                    valid = True
                    type = "percentage"
                    discount_in_storage = percentage_discounts[key]
                    break
        else:
            valid_discount["Amount"] = amount_discounts


        # for key in valid_discount["Amount"]:
        #     if valid_discount[key].get_code() == code:
        #         valid = True
        #         discount_in_strorage = valid_discount[key]
        #         break

        if valid == False:
            print("Code deosnt exist")
            error_msg = "This code doesn't exist."
            return render_template('cart.html', cartList=cartList, totalCost=totalCost, current=current, NoCollectForm = Delivery, Discount=Discount, Items=Items, error_msg=error_msg, discount=discount, new_total=new_total, searchForm=searchForm)

        if valid is True and check_used==False:
            print("TRUUUUU")
            discount = discount_in_storage
            print(discount)
            print(users_codes)
            totalCost = '%.2f' %float(totalCost)
            # totalCost = totalCost
            condition = discount.get_condition()
            if float(totalCost) >= (condition):
                # if isinstance(discount, AmountDiscount):
                if type == "amount":
                    amount = discount.get_discount_amount()
                    new_total = float(totalCost) - float(amount)

                else:
                    percentage = float(discount.get_discount_percentage())
                    new_total = totalCost - (totalCost * percentage/100)

                return render_template('cart.html', cartList=cartList, totalCost=totalCost, current=current, NoCollectForm = Delivery, Discount=Discount, Items=Items, error_msg=error_msg, discount=discount,new_total=new_total, searchForm=searchForm)

@app.route("/addToCart/<name>/<quantity>", methods=['GET', 'POST'])
def addToCart(name, quantity):
    current_user = ""
    productsDict= {}
    db = shelve.open('storage.db', 'c')
    try:
        current_user = db["Current User"]
    except:
        print('Error in retrieving current user from storage.db.')

    try:
        productsDict = db["Products"]

    except:
        print('Error in retrieving current products from storage.db.')

    for thing in productsDict:
        if productsDict[thing].get_product_name() == name:
            product = productsDict[thing]
            break
    print("Form submitted")
    current_user.add_to_cart(product, quantity)
    db['Current User'] = current_user
    db.close()
    serial_no = product.get_serial_no()
    return redirect(url_for("IndItem",serialNo = serial_no ))

    # searchForm = searchBar()
    # if request.method == "POST" and searchForm.validate():
    #     return redirect('/search/' + searchForm.search_input.data + '/view/descending')

@app.route('/deleteShoppingCartItem/<serialNo>', methods=['GET', 'POST'])
def deleteShoppingCartItem(serialNo):
    current_user = ""
    productsDict = {}
    db = shelve.open('storage.db', 'c')
    try:
        current_user = db["Current User"]
    except:
        print('Error in retrieving current user from storage.db.')

    try:
        productsDict = db['Products']
    except:
        print("Error retrieving products")

    product = productsDict[serialNo]
    current_user.remove_from_cart(product)
    db["Current User"] = current_user
    db.close()

    # searchForm = searchBar()
    # if request.method == "POST" and searchForm.validate():
    #     return redirect('/search/' + searchForm.search_input.data + '/view/descending')
    return redirect('/cart')

@app.route('/moveToWishlist/<serialNo>', methods=['GET', 'POST'])
def moveToWishlist(serialNo):
    current_user = ""
    productsDict={}
    db = shelve.open('storage.db', 'c')
    try:
        current_user = db["Current User"]
    except:
        print('Error in retrieving current user from storage.db.')

    try:
        productsDict = db["Products"]

    except:
        print('Error in retrieving current products from storage.db.')

    wishlist = current_user.get_wishlist()

    product = productsDict[serialNo]
    wishlist[serialNo] = product
    current_user.set_wishlist(wishlist)
    current_user.remove_from_cart(product)
    db["Current User"] = current_user
    db.close()
    return redirect('/cart')

# Wishlist
@app.route('/wishlist/<filter>/', methods=['GET', 'POST'])
def wishlist(filter):
    filterDict = {"hightolow": "Price: High to low", "lowtohigh":"Price: Low to high", "a-z": "A-Z", "z-a":"Z-A" }
    for key in filterDict:
        filter_breadcrumb = ""
        if filter == key:
            filter_breadcrumb = filterDict[filter]
            break
    db = shelve.open('storage.db', 'r')
    try:
        current = db["Current User"]
        Items = len(current.get_shopping_cart())
    except:
        print('Error in retrieving current user from storage.db.')
        Items = 0

    wishlist = current.get_wishlist()

    db.close()

    filtered_list = []
    for key in wishlist:
        product = wishlist[key]
        filtered_list.append(product)
        filtered_list = filter_function(filtered_list, filter)

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        return redirect('/search/' + searchForm.search_input.data + '/view/descending')
    return render_template('wishlist.html', filtered_list=filtered_list, searchForm=searchForm, filter_breadcrumb=filter_breadcrumb, current=current, Items=Items)

@app.route("/addToWishlist/<name>", methods=['GET', 'POST'])
def addToWishlist(name):
    current_user = ""
    productsDict= {}
    db = shelve.open('storage.db', 'c')
    try:
        current_user = db["Current User"]
    except:
        print('Error in retrieving current user from storage.db.')

    try:
        productsDict = db["Products"]

    except:
        print('Error in retrieving current products from storage.db.')

    for thing in productsDict:
        product = ""
        if productsDict[thing].get_product_name() == name:
            product = productsDict[thing]
            current_user.add_to_wishlist(product)
            break

    db['Current User'] = current_user
    wishlist = current_user.get_wishlist()
    db.close()
    # if request.method == "POST" and searchForm.validate():
    #     return redirect('/search/' + searchForm.search_input.data + '/view/descending')
    return redirect("/wishlist/a-z")

@app.route('/deleteWishListItem/<serialNo>', methods=['GET', 'POST'])
def deleteWishListItem(serialNo):

    current_user = ""
    productsDict = {}
    db = shelve.open('storage.db', 'r')
    try:
        current_user = db["Current User"]
    except:
        print('Error in retrieving current user from storage.db.')

    try:
        productsDict = db['Products']
    except:
        print("Error retrieving products")

    product = productsDict[serialNo]
    current_user.remove_from_wishlist(product)
    db["Current User"] =current_user
    db.close()
    print(product)
    return redirect('/wishlist/a-z')

@app.route('/moveToCart/<serialNo>', methods=['GET', 'POST'])
def moveToCart(serialNo):
    current_user = ""
    productsDict={}
    db = shelve.open('storage.db', 'r')
    try:
        current_user = db["Current User"]
    except:
        print('Error in retrieving current user from storage.db.')

    try:
        productsDict = db["Products"]

    except:
        print('Error in retrieving current products from storage.db.')

    cart = current_user.get_shopping_cart()

    product = productsDict[serialNo]
    cart[serialNo] = 1
    current_user.set_shopping_cart(cart)
    current_user.remove_from_wishlist(product)
    db["Current User"] = current_user
    db.close()
    return redirect('/wishlist/a-z')
# Checkout
@app.route('/checkout/<delivery>', methods=['GET', 'POST'])
def checkout(delivery):

    NoCollect = delivery

    current = ""
    searchForm = searchBar()
    deliveryForm = DeliveryForm(request.form)
    collectionForm = CollectionForm(request.form)
    db = shelve.open('storage.db', 'c')
    try:
        current = db["Current User"]
    except:
        print("Error in retrieving current user for checkout")
    try:
        transactions = db["Transactions"]
    except:
        print("error in retrieving transaction information")

    try:
        products = db["Products"]
    except:
        print("Yo prods missin at checkout")
    cart = current.get_shopping_cart()
    prodlist = []
    subtotal = 0
    for key in cart:
        product = products[key]
        product.set_quantity(int(cart[key]))
        prodlist.append(product)
        subtotal += float(product.get_price()) * int(cart[key])
    number = len(prodlist)
    total = subtotal + 12
    db.close()
    today = date.today()
    currentDate = today.strftime("%d %B %Y")
    if request.method == "POST" and deliveryForm.validate():
        db = shelve.open('storage.db','c')
        transactions = {}
        try:
            transactions = db["Transactions"]
        except:
            print("error in retrieving transaction information")
        try:
            current = db["Current User"]
        except:
            print("Can't get user")
        print(deliveryForm.unit_no.data)
        deliveryInfo = Delivery(currentDate, deliveryForm.name.data, deliveryForm.phone.data,
                    current.get_email(),total, prodlist, deliveryForm.payment_mode.data,
                     deliveryForm.credit_card_number.data, deliveryForm.credit_card_expiry.data, deliveryForm.credit_card_cvv.data,
                     deliveryForm.street_name.data,
                     deliveryForm.postal_code.data,
                     deliveryForm.unit_no.data)
        deliveryId = deliveryInfo.get_id()
        transactions[deliveryId] = deliveryInfo
        db["Transactions"] = transactions
        current.set_transactions(deliveryId)
        db["Current User"] = current
        db.close()
        return redirect(url_for("summary", deliveryId= deliveryId))
    if request.method == "POST" and collectionForm.validate():
        db = shelve.open('storage.db','c')
        transactions = {}
        try:
            transactions = db["Transactions"]
        except:
            print("Error in retrieving transactions")
        try:
            current = db["Current User"]
        except:
            print("Current dude for collection MIA")
        collection = Collection(currentDate, collectionForm.name.data, collectionForm.phone.data, current.get_email(), total, prodlist,
        collectionForm.payment_mode.data, collectionForm.credit_card_number.data, collectionForm.credit_card_expiry.data, collectionForm.credit_card_cvv.data,
        collectionForm.date.data, collectionForm.time.data)
        collectionId = collection.get_id()
        transactions[collectionId] = collection
        db["Transactions"] = transactions
        current.set_transactions(collectionId)
        db["Current User"] = current
        db.close()
        return redirect(url_for("summary",deliveryId=collectionId))
        # current_user.set_transactions(deliveryInfo.get_id())
        # transactions[deliveryInfo.get_id()] = deliveryInfo
        # db["Transactions"] = transactions
    #     current_user.set_orders(deliveryInfo.get_id())
    #     db["Current User"] = current_user
    #     db.close()
    #     return render_template('checkout.html', current=current, completedForm=deliveryInfo, searchForm=searchForm, cart=prodlist, total=total, number=number)
        print(deliveryInfo.get_name())
    total = "%.2f" %float(total)
    subtotal = "%.2f" %float(subtotal)
    # if request.method == "POST" and searchForm.validate():
    #     return redirect('/search/' + searchForm.search_input.data)

    return render_template('checkout.html', deliveryform=deliveryForm, current=current, collectionform =collectionForm, searchForm=searchForm, cart=prodlist, total=total, number=number, subtotal =subtotal, delivery = NoCollect, Items = 0)



# Summary page
@app.route('/summary/<deliveryId>', methods= ["GET", "POST"])
def summary(deliveryId):
    db = shelve.open('storage.db','r')
    transactions = {}
    D = ""

    try:
        transactions = db["Transactions"]
    except:
        print("error in retrieving transaction information")
    for id in transactions:
        if str(id) == deliveryId:
            details = transactions[id]
            print("Got em")
            break

        else:
            print("Cant find the below id")
            print(id)
    searchForm = searchBar()
        # if request.method == "POST" and searchForm.validate():
        #     return redirect('/search/' + searchForm.search_input.data)

    type = details.get_type()
    if type == "delivery":
        D = True
    else:
        D = False

    if request.method == "POST":
        print(str(transactions) + "\n\n\n")
        transactions.pop(int(deliveryId))
        return redirect(url_for("checkout", delivery = D))

    return render_template('summary.html', searchForm=searchForm, details=details, Items = 0, type = D)

# feedback page
@app.route('/feedback', methods = ["GET", "POST"])
def feedback():
    feedbackForm = FeedbackForm(request.form)
    searchForm = searchBar()

    if request.method == "POST" and feedbackForm.validate():
        db = shelve.open('db', 'c')
        feedbacks = []
        try:
            feedbacks = db["Feedback"]
        except:
            print("error")

        feedback = Feedback(feedbackForm.name.data, feedbackForm.agenda.data, feedbackForm.comment.data, feedbackForm.rating.data)
        feedbacks.append(feedback)
        db["Feedback"] = feedbacks
        db.close()

        return redirect('/home')

    return render_template('feedback.html', searchForm=searchForm, feedbackForm=feedbackForm)

@app.route('/displayFeedback')
def displayFeedback():
    db = shelve.open('db', 'c')
    try:
        feedbacks = db["Feedback"]
    except:
        print("error")

    return render_template('adminFeedback.html', feedbackList = feedbacks)

# Admin Side
@app.route('/dashboard/<int:stockPage>')
def dashboard(stockPage):
    productDict = {}
    transactions = []
    db = shelve.open('storage.db', 'r')

    try:
        productDict = db['Products']
    except:
        print('Error in retrieving Products from storage.db.')
    try:
        transactions = db['Transactions']
        db.close()
    except:
        print('Error in retrieving Products from storage.db.')

    productList = []
    lowStockList = []
    midStockList = []

    for key in productDict:
        product = productDict[key]
        productList.append(product)

        if product.get_quantity()<product.get_stock_threshold():
            lowStockList.append(product)

        elif product.get_quantity()<(product.get_stock_threshold()*1.25):
            midStockList.append(product)

        else:
            continue

    stockList = lowStockList + midStockList
    startCount = stockPage*3 - 3
    endCount = stockPage*3
    stockList = stockList[startCount:endCount]

    viewsList = sort_by(productList, 'view', 'descending')[:5]
    purchasesList = sort_by(productList, 'purchase', 'descending')[:5]
    viewsList.reverse()
    purchasesList.reverse()

    purchasesName = []
    purchasesSerial = []
    purchasesAmount = []
    for product in purchasesList:
        purchasesName.append(product.get_product_name())
        purchasesSerial.append(product.get_serial_no())
        purchasesAmount.append(product.get_purchases())

    purchasesData = {
            'data':  [go.Bar(name='Purchases', x=purchasesAmount, y=purchasesSerial, text=purchasesName, textposition='auto', orientation='h', marker_color='#d1f082')],

            'layout': {}
            }

    purchasesGraph = json.dumps(purchasesData, cls=plotly.utils.PlotlyJSONEncoder)

    viewsName = []
    viewsSerial = []
    viewsAmount = []
    for product in viewsList:
        viewsName.append(product.get_product_name())
        viewsSerial.append(product.get_serial_no())
        viewsAmount.append(product.get_views())

    viewsData = {
            'data':  [go.Bar(name='Views', x=viewsAmount, y=purchasesSerial, text=viewsName, textposition='auto', orientation='h', marker_color='#82f0c0')],

            'layout': {}
            }

    viewsGraph = json.dumps(viewsData, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('dashboard.html', currentPage='Dashboard', viewsList = viewsList, purchasesGraph = purchasesGraph
    , viewsGraph = viewsGraph, lowStockList=lowStockList, midStockList=midStockList, transactions=transactions, stockPage=stockPage, stockList=stockList)

@app.route('/products/<category>/<order>/', methods=['GET', 'POST'])
def products(category, order):
    productDict = {}
    db = shelve.open('storage.db', 'c')

    try:
        productDict = db['Products']
        db.close()
    except:
        print('Error in retrieving Products from storage.db.')

    productList = []
    for key in productDict:
        product = productDict.get(key)
        productList.append(product)
        productList = sort_by(productList, category, order)

    adminSearchForm = AdminSearch(request.form)
    if request.method == "POST" and adminSearchForm.validate():
        return redirect('/products/search/' + adminSearchForm.search_cat.data + '/' + adminSearchForm.search_input.data)

    return render_template('products.html', adminSearchForm = adminSearchForm, productList=productList, searchString='', searchCat='', currentPage='Catalog')

@app.route('/products/search/<searchCat>/<searchString>', methods=['GET', 'POST'])
def productsSearch(searchCat, searchString):
    productDict = {}
    db = shelve.open('storage.db', 'c')

    try:
        productDict = db['Products']
        db.close()
    except:
        print('Error in retrieving Products from storage.db.')

    productList = []
    for key in productDict:
        product = productDict[key]
        if searchCat=='name-brand':
            if searchString in product.get_product_name().lower() or searchString in product.get_brand().lower():
                productList.append(product)

        elif searchCat=='sub-category':
            if searchString.replace(' ','') in product.get_sub_category().lower():
                productList.append(product)

        elif searchCat=='serial-no':
            if searchString in product.get_serial_no().lower():
                productList.append(product)

        else:
            print('error')

    adminSearchForm = AdminSearch(request.form)
    if request.method == "POST" and adminSearchForm.validate():
        return redirect('/products/search/' + adminSearchForm.search_cat.data + '/' + adminSearchForm.search_input.data)

    return render_template('products.html', adminSearchForm = adminSearchForm, productList=productList, searchString=searchString, searchCat=searchCat, currentPage='Catalog')

@app.route('/productSettings/<serialNo>/', methods=['GET', 'POST'])
def productSettings(serialNo):
    editProductForm = EditProductForm(request.form)

    if request.method == 'POST' and editProductForm.validate():
        productDict = {}
        db = shelve.open('storage.db', 'w')
        productDict = db['Products']

        product = productDict.get(serialNo)
        product.set_product_name(editProductForm.productName.data)
        product.set_brand(editProductForm.brand.data)
        product.set_sub_category(editProductForm.subCategory.data)
        product.set_price(editProductForm.price.data)
        product.set_description(editProductForm.description.data)
        product.set_quantity(editProductForm.quantity.data)
        product.set_stock_threshold(editProductForm.stockThreshold.data)
        product.set_activated(editProductForm.activated.data)

        image = request.files["image"]
        if image.filename!='':
            product.set_thumbnail(image.filename)
            this_folder = os.path.dirname(os.path.abspath(__file__))
            image_to_copy = os.path.join(this_folder, image.filename)
            image.save(image_to_copy)

            try:
                Path(image_to_copy).rename(this_folder + '/static/images/' + image.filename)
                print("Image saved.")
            except:
                os.remove(image_to_copy)
                print("Image already exists in database.")

        db['Products'] = productDict
        db.close()
        return redirect('/products/name/ascending')

    else:
        productDict = {}
        db = shelve.open('storage.db', 'r')
        productDict = db['Products']
        db.close()

        product = productDict.get(serialNo)
        editProductForm.productName.data = product.get_product_name()
        editProductForm.brand.data = product.get_brand()
        editProductForm.subCategory.data = product.get_sub_category()
        editProductForm.price.data = float(product.get_price())
        editProductForm.quantity.data = int(product.get_quantity())
        editProductForm.stockThreshold.data = int(product.get_stock_threshold())
        editProductForm.description.data = product.get_description()
        editProductForm.activated.data = product.get_activated()
        editProductForm.serialNo.data = product.get_serial_no()

    return render_template('productSettings.html', form=editProductForm, label=product.get_thumbnail(), currentPage='Catalog')

@app.route('/addProduct', methods=['GET', 'POST'])
def addProduct():
    createProductForm = CreateProductForm(request.form)
    if request.method=='POST' and createProductForm.validate():
        productDict = {}
        db = shelve.open('storage.db', 'c')
        try:
            productDict = db['Products']
        except:
            print('Error in retrieving Products from storage.db.')

        image = request.files["image"]
        this_folder = os.path.dirname(os.path.abspath(__file__))
        image_to_copy = os.path.join(this_folder, image.filename)
        image.save(image_to_copy)
        try:
            Path(image_to_copy).rename(this_folder + '/static/images/' + image.filename)
            print("Image saved.")
        except:
            os.remove(image_to_copy)
            print("Image already exists in database.")

        product = Product(createProductForm.productName.data, createProductForm.brand.data, image.filename
        , createProductForm.subCategory.data, createProductForm.price.data, createProductForm.description.data
        , createProductForm.activated.data, createProductForm.quantity.data, createProductForm.stockThreshold.data)

        serialNo = ''
        while True:
            for x in range(6):
                serialNo += random.choice(string.digits)
            serialNo += random.choice(string.ascii_uppercase)

            if serialNo not in productDict:
                break

        product.set_serial_no(serialNo)
        productDict[product.get_serial_no()] = product
        db['Products'] = productDict

        db.close()

        return redirect('/products/name/ascending')

    return render_template('addProduct.html', form=createProductForm, currentPage='Catalog')

@app.route('/productStats/<category>/<order>/', methods=['GET', 'POST'])
def viewAll(category, order):
    productDict = {}
    db = shelve.open('storage.db', 'r')

    try:
        productDict = db['Products']
        db.close()
    except:
        print('Error in retrieving Products from storage.db.')

    lowStockList = []
    midStockList = []
    highStockList = []

    for key in productDict:
        product = productDict[key]

        if product.get_quantity()<product.get_stock_threshold():
            lowStockList.append(product)

        elif product.get_quantity()<(product.get_stock_threshold()*1.25):
            midStockList.append(product)

        else:
            highStockList.append(product)

    lowStockList = sort_by(lowStockList, category, order)
    midStockList = sort_by(midStockList, category, order)
    highStockList = sort_by(highStockList, category, order)

    nameList = []
    purchasesList = []
    viewsList = []
    for product in lowStockList:
        nameList.append(product.get_product_name())
        purchasesList.append(product.get_purchases())
        viewsList.append(product.get_views())
    for product in midStockList:
        nameList.append(product.get_product_name())
        purchasesList.append(product.get_purchases())
        viewsList.append(product.get_views())
    for product in highStockList:
        nameList.append(product.get_product_name())
        purchasesList.append(product.get_purchases())
        viewsList.append(product.get_views())

    nameList.reverse()
    purchasesList.reverse()
    viewsList.reverse()

    graph = {}
    graph= {
            'data':  [go.Bar(name='Purchases', x=purchasesList, y=nameList, orientation='h', marker_color='#d1f082', width=0.3),
                      go.Bar(name='Views', x=viewsList, y=nameList, orientation='h', marker_color='#a182f0', width=0.3)],

            'layout': {}
            }

    graphJSON = json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)

    adminSearchForm = AdminSearch(request.form)
    if request.method == "POST" and adminSearchForm.validate():
        return redirect('/productStats/search/' + adminSearchForm.search_cat.data + '/' + adminSearchForm.search_input.data)

    return render_template('productStats.html', graphJSON=graphJSON, currentPage='Statistics', adminSearchForm=adminSearchForm
    , lowStockList=lowStockList, midStockList=midStockList, highStockList=highStockList, length=len(nameList), searchCat='')

@app.route('/productStats/search/<searchCat>/<searchString>', methods=['GET', 'POST'])
def statsSearch(searchCat, searchString):
    productDict = {}
    db = shelve.open('storage.db', 'r')

    try:
        productDict = db['Products']
        db.close()
    except:
        print('Error in retrieving Products from storage.db.')

    lowStockList = []
    midStockList = []
    highStockList = []
    productList = []

    for key in productDict:
        product = productDict[key]

        if searchCat=='name-brand':
            if searchString in product.get_product_name().lower() or searchString in product.get_brand().lower():
                productList.append(product)

        elif searchCat=='sub-category':
            if searchString.replace(' ','') in product.get_sub_category().lower():
                productList.append(product)

        elif searchCat=='serial-no':
            if searchString in product.get_serial_no().lower():
                productList.append(product)

        else:
            print('error')

    for product in productList:
        if product.get_quantity()<product.get_stock_threshold():
            lowStockList.append(product)

        elif product.get_quantity()<(product.get_stock_threshold()*1.25):
            midStockList.append(product)

        else:
            highStockList.append(product)

    nameList = []
    purchasesList = []
    viewsList = []
    for product in lowStockList:
        nameList.append(product.get_product_name())
        purchasesList.append(product.get_purchases())
        viewsList.append(product.get_views())
    for product in midStockList:
        nameList.append(product.get_product_name())
        purchasesList.append(product.get_purchases())
        viewsList.append(product.get_views())
    for product in highStockList:
        nameList.append(product.get_product_name())
        purchasesList.append(product.get_purchases())
        viewsList.append(product.get_views())

    nameList.reverse()
    purchasesList.reverse()
    viewsList.reverse()

    graph = {}
    graph= {
            'data':  [go.Bar(name='Purchases', x=purchasesList, y=nameList, orientation='h', marker_color='#d1f082', width=0.3),
                      go.Bar(name='Views', x=viewsList, y=nameList, orientation='h', marker_color='#a182f0', width=0.3)],

            'layout': {}
            }

    graphJSON = json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)

    adminSearchForm = AdminSearch(request.form)
    if request.method == "POST" and adminSearchForm.validate():
        return redirect('/productStats/search/' + adminSearchForm.search_cat.data + '/' + adminSearchForm.search_input.data)

    return render_template('productStats.html', graphJSON=graphJSON, currentPage='Statistics', adminSearchForm=adminSearchForm
    , lowStockList=lowStockList, midStockList=midStockList, highStockList=highStockList, length=len(nameList), searchCat=searchCat, searchString=searchString)

@app.route('/addStock', methods=['GET', 'POST'])
def addStock():
    db = shelve.open('storage.db', 'c')
    productDict = {}
    newStock = {}
    try:
        productDict = db['Products']
    except:
        print('Error in retrieving Products from storage.db.')
    try:
        newStock = db['New Stock']
    except:
        print('Error in retrieving New Stock from storage.db.')

    productList = []

    for key in productDict:
        productList.append(productDict[key])
    productList = sort_by(productList, 'name', 'ascending')

    tupleList = [('', 'Select Product')]
    for product in productList:
        field = [product.get_serial_no(), product.get_serial_no() + ' - ' + product.get_product_name()]
        tupleList.append(tuple(field))

    class AddStockForm(Form):
        product = SelectField('', choices=tupleList, default='')
        quantity = IntegerField('', [validators.DataRequired(message='This is a required field.')
                                    , validators.NumberRange(min=0, message='Value has to be more than 0')])

    addStockForm = AddStockForm(request.form)

    if request.method=='POST' and addStockForm.validate():
        newStock[addStockForm.product.data] = addStockForm.quantity.data
        db['New Stock'] = newStock
        db.close()

    return render_template('addStock.html', form=addStockForm, currentPage='Catalog', newStock=newStock, productDict=productDict)

@app.route('/processAdditionOfStock')
def processAdditionOfStock():
    db = shelve.open('storage.db', 'c')
    productDict = {}
    newStock = {}
    try:
        productDict = db['Products']
    except:
        print('Error in retrieving Products from storage.db.')
    try:
        newStock = db['New Stock']
    except:
        print('Error in retrieving New Stock from storage.db.')

    for product in newStock:
        productDict[product].increase_quantity(newStock[product])

    db['Products'] = productDict
    db['New Stock'] = {}
    db.close()
    print('yay')

    return redirect('/products/name/ascending')

@app.route('/cancelAdditionOfStock')
def cancelAdditionOfStock():
    db = shelve.open('storage.db', 'c')
    db['New Stock'] = {}
    db.close()

    return redirect('/products/name/ascending')

@app.route('/transactions')
def transactions():
    transactionsDict = {}
    deliveryList = []
    collectionList = []

    db = shelve.open('storage.db', 'c')

    try:
        transactionsDict = db['Transactions']
        db.close()
    except:
        print('Error in retrieving Transactions from storage.db.')

    for key in transactionsDict:
        if transactionsDict[key].get_type()=='delivery':
            deliveryList.append(transactionsDict[key])
        else:
            collectionList.append(transactionsDict[key])

    return render_template('transactions.html', currentPage='Transactions', deliveryList=deliveryList, collectionList=collectionList)

@app.route('/downloadProducts', methods=['GET'])
def download():
    db = shelve.open('storage.db', 'c')

    try:
        productDict = db['Products']
        db.close()
    except:
        print('Error in retrieving Products from storage.db.')

    productArray = [['Name'
                    , 'Brand'
                    , 'Sub-Category'
                    , 'Serial No.'
                    , 'Price'
                    , 'Description'
                    , 'Activated'
                    , 'Quantity'
                    , 'Stock Threshold']]


    for key in productDict:
        product = productDict[key]

        if product.get_activated():
            activated = 'Show'
        else:
            activated = 'Hide'

        data = [product.get_product_name()
                , product.get_brand()
                , product.get_sub_category()
                , product.get_serial_no()
                , product.get_price()
                , product.get_description()
                , activated
                , product.get_quantity()
                , product.get_stock_threshold()]

        productArray.append(data)

    return excel.make_response_from_array(productArray, file_type='xls', file_name='Delorem Ipsum product records')


# Other stuff
@app.route('/discount', methods=['GET', 'POST'])
def discount():
    AddDiscountAmount = AddDiscountAmountForm(request.form)
    AddDiscountPercentage = AddDiscountPercentageForm(request.form)
    db = shelve.open('storage.db', 'c')
    amount_discounts = {}
    percentage_discounts = {}
    valid_discount = {}
    try:
        valid_discount = db['Valid Discount']

    except:
        print('Error in retrieving valid discounts from storage.db.')

    test = valid_discount.get('Amount')
    if test:
        amount_discounts = valid_discount['Amount']
    else:
        valid_discount['Amount'] = amount_discounts

    test = valid_discount.get('Percentage')
    if test:
        percentage_discounts = valid_discount['Percentage']
    else:
        valid_discount['Percentage'] = percentage_discounts

    print(valid_discount)

    if request.method == "POST" and AddDiscountAmount.validate():
        code=AddDiscountAmount.discount_code.data
        discount = AmountDiscount(AddDiscountAmount.discount_code.data, AddDiscountAmount.discount_condition.data, AddDiscountAmount.discount_start.data, AddDiscountAmount.discount_expiry.data, AddDiscountAmount.discount_amount.data)
            # empty = bool(valid_discount['Amount'])
        test = valid_discount.get('Amount')
        if test:
            amount_discounts = valid_discount['Amount']
            amount_discounts[AddDiscountAmount.discount_code.data] = discount
            valid_discount['Amount'] = amount_discounts
            db['Valid Discount'] = valid_discount
        else:
            valid_discount['Amount'] = amount_discounts
            amount_discounts[AddDiscountAmount.discount_code.data] = discount
            valid_discount['Amount'] = amount_discounts
            db['Valid Discount'] = valid_discount

        test = valid_discount.get('Percentage')
        if test:
            percentage_discounts =  valid_discount['Percentage']

        else:
            percentage_discounts = percentage_discounts

    elif request.method == "POST" and AddDiscountPercentage.validate():
        code=AddDiscountPercentage.discount_code.data
        discount = PercentageDiscount(AddDiscountPercentage.discount_code.data, AddDiscountPercentage.discount_condition.data, AddDiscountPercentage.discount_start.data,AddDiscountPercentage.discount_expiry.data, AddDiscountPercentage.discount_percentage.data)
        test = valid_discount.get('Percentage')
        if test:
            percentage_discounts = valid_discount['Percentage']
            percentage_discounts[AddDiscountPercentage.discount_code.data] = discount
            valid_discount['Percentage'] = percentage_discounts
            db['Valid Discount'] = valid_discount
        else:
            valid_discount['Percentage'] = percentage_discounts
            percentage_discounts[AddDiscountPercentage.discount_code.data] = discount
            valid_discount['Percentage'] = percentage_discounts
            db['Valid Discount'] = valid_discount
        test = valid_discount.get('Amount')

        if test:
            amount_discounts = valid_discount['Amount']
        else:
            amount_discounts = amount_discounts



        return render_template('discount.html', currentPage="Discount", AddDiscountAmount=AddDiscountAmount, AddDiscountPercentage=AddDiscountPercentage, valid_discount=valid_discount, amount_discounts=amount_discounts, percentage_discounts=percentage_discounts, code=code)

    db.close()
    return render_template('discount.html', currentPage="Discount", AddDiscountAmount=AddDiscountAmount, AddDiscountPercentage=AddDiscountPercentage, valid_discount=valid_discount, amount_discounts=amount_discounts, percentage_discounts=percentage_discounts)

@app.route('/deleteDiscount/<code>', methods=['POST'])
def deleteDiscount(code):
    valid_discount = {}
    amount_discounts = {}
    percentage_discounts = {}
    db = shelve.open('storage.db', 'c')

    try:
        valid_discount = db['Valid Discount']
    except:
        print("Error retrieving valid discount from storage.db")

    amount_discounts = valid_discount['Amount']
    percentage_discounts = valid_discount["Percentage"]

    found = False

    for key in amount_discounts:
        if key == code:
            del amount_discounts[key]
            valid_discount['Amount'] = amount_discounts
            found = True
            break

    if found == False:
        for key in percentage_discounts:
            if key == code:
                del percentage_discounts[key]
                valid_discount['Percentage'] = percentage_discounts
                found=True
                break

    db['Valid Discount'] = valid_discount

    return redirect('/discount')

@app.route('/categories')
def categories():
    return render_template('categories.html')

@app.route('/deliveryInvoice/<email>/',  methods=['get','POST'])
def deliveryInvoice(email):
    print("hey!")
    current_user = ""
    db = shelve.open('storage.db', 'r')
    try:
        current_user = db["Current User"]
    except:
        print('Error in retrieving current user from storage.db.')

    cart = current_user.get_shopping_cart()
    order_ID = current_user.get_transactions()

    cartList = []
    images = []
    for product in cart:
        cartList.append(cart[product])
        images.append(cart[product].get_thumbnail())

    # try:
    #     deliveryDetails = db["deliveryDetails"]
    #
    # except:
    #         print("error in retrieving information")
    #
    # orders = current_user.get_orders()
    # order_ID = orders[-1]
    # deliveryInfo = deliveryDetails[order_ID]
    # date = deliveryInfo.get_date()

    try:
        msg = Message("Delorem Ipsum Pharmacy",
        sender="deloremipsumonlinestore@outlook.com",
        recipients=[email])

        for image in images:
            print("Goes into images")
            this_folder = os.path.dirname(os.path.abspath(__file__))
            print("This_folder")
            source = this_folder + "/static/images/" + image
            print(source)
            with app.open_resource(source) as fp:
                # msg.attach(source, "image/png" fp.read())
                msg.attach(source, "image/jpg", fp.read())
                print("attached")

        msg.body = "This ur e reciept"
        msg.html = render_template('html_in_invoice.html',  cartList=cartList, current_user=current_user )
        print("testinggggggggggggggg")
        mail.send(msg)
        print("MAIL SENT")
		#return 'Mail sent!'

    except Exception as e:
		# return("gxyaishuxa")
        print(e)
        print("Error:", sys.exc_info()[0])
        print("goes into except")

    db.close()

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        print(searchForm.search_input.data)
    return redirect('/home')

@app.route('/listOfBrands')
def listOfBrands():
    productsDict ={}
    db = shelve.open('storage.db', 'c')
    try:
        productsDict = db["Products"]
    except:
        print("Error retrieving products from storage.db")

    try:
        current = db["Current User"]
        Items = len(current.get_shopping_cart())
    except:
        print('Error in retrieving current user from storage.db.')
        current = False
        Items = 0

    start_with_letter = []
    start_with_other = []

    brandsDict = {}
    for letter in string.ascii_lowercase:
        brandsDict[letter]=[]


    for product in productsDict:
        brand = productsDict[product].get_brand()
        first_letter = brand[0].lower()
        brandsDict[first_letter].append(brand)

    db.close()
    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        print(searchForm.search_input.data)
    return render_template('listOfBrands.html', searchForm=searchForm, brandsDict=brandsDict, current=current, Items=Items)

@app.route('/Brand/<brand>', methods=['GET', 'POST'])
def brand(brand):
    db = shelve.open('storage.db', 'r')
    try:
        Products = db["Products"]
    except:
        print("Error in retrieving products from shelve")

    try:
        current = db["Current User"]
        Items = len(current.get_shopping_cart())

    except:
        print('Error in retrieving current user from storage.db.')
        current = False
        Items = 0

    products = []
    for id in Products:
        product = Products[id]
        if brand.lower() == product.get_brand().lower():
            if product.get_activated() == True:
                products.append(product)

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        return redirect('/search/' + searchForm.search_input.data)
    return render_template('productByBrand.html', productList=products, productCount=len(products), searchForm=searchForm, brand=brand, current=current, Items = Items)

app.jinja_env.filters['get_name_with_space'] = get_name_with_space
if __name__=='__main__':
    excel.init_excel(app)
    app.run(debug=True)
