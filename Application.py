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
from decimal import Decimal


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

#Saving the transaction data temporarily before confirmation
import pickle
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

# Getting valid discount codes and checking if they are expired
# db = shelve.open('storage.db','c')
# try:
#     valid_discount = db["Valid Discount"]
# except:
#     print("Either we got none or like we can't get discounts stuffy")
# AmountDiscount = valid_discount["Amount"]
# PercentageDiscount = valid_discount["Percentage"]
# amount_discount = {}
# percentage_discount = {}
# updated_discount = {}
# for code in AmountDiscount:
#     if AmountDiscount[code].get_start_date() < date.today() and AmountDiscount[code].get_expiry_date() > date.today():
#         amount_discount[code] = AmountDiscount[code]
# for code in PercentageDiscount:
#     if PercentageDiscount[code].get_start_date() < date.today() and PercentageDiscount[code].get_expiry_date() > date.today():
#         percentage_discount[code] = PercentageDiscount[code]
# updated_discount["Amount"] = amount_discount
# updated_discount["Percentage"] = percentage_discount
# db["Valid Discount"] = updated_discount
# db.close()
# def checkfordiscounts():
#     db = shelve.open('storage.db', 'c')
#     try:
#         valid_discount = db["Valid Discount"]
#     except:
#         print("bchscbweucw")
#     amount_discounts = valid_discount["Amount"]
#     percentage_discounts = valid_discount["Percentage"]
#     valid_amount_discounts = {}
#     valid_percentage_discounts =  {}
#     for code in amount_discounts:
#         if amount_discounts[code].get_start_date() < date.today() and amount_discounts[code].get_expiry_date() > date.today():
#             valid_amount_discounts[code] = amount_discounts[code]
#
#     for code in percentage_discounts:
#         if percentage_discounts[code].get_start_date() < date.today() and percentage_discounts[code].get_expiry_date() > date.today():
#             valid_percentage_discounts[code] = percentage_discounts[code]
#
#     valid_discount["Amount"] = valid_amount_discounts
#     valid_discount["Percentage"] = valid_percentage_discounts
#     db["Valid Discount"]  =valid_discount
#
#     db.close()
#     return valid_discount
def checkfordiscounts():
    db = shelve.open('storage.db', 'c')
    valid_discount = {}
    discount_master =[]
    try:
        valid_discount = db["Valid Discount"]
        # expired_discount = db["Expired"]
        discount_master = db["Discount Master"]
    except:
        print("bchscbweucw")

    amount_discounts = valid_discount["Amount"]
    percentage_discounts = valid_discount["Percentage"]
    valid_amount_discounts = {}
    valid_percentage_discounts =  {}
    for code in amount_discounts:
        if amount_discounts[code].get_start_date() < date.today() and amount_discounts[code].get_expiry_date() > date.today():
            valid_amount_discounts[code] = amount_discounts[code]
            status = "active"
        elif amount_discounts[code].get_start_date() < date.today() and amount_discounts[code].get_expiry_date() <date.today():
            status = "expired"
        else:
            status = "inactive"

        for discount in discount_master:
            if discount == amount_discounts[code]:
                discount.set_status(status)
                break
        amount_discounts[code].set_status(status)


    for code in percentage_discounts:
        if percentage_discounts[code].get_start_date() < date.today() and percentage_discounts[code].get_expiry_date() > date.today():
            valid_percentage_discounts[code] = percentage_discounts[code]
            status = "active"
        elif percentage_discounts[code].get_start_date() < date.today() and percentage_discounts[code].get_expiry_date() <date.today():
            status = "expired"
        else:
            status = "inactive"
        for discount in discount_master:
            if discount == percentage_discounts[code]:
                discount.set_status(status)
        percentage_discounts[code].set_status(status)

    valid_discount["Amount"] = valid_amount_discounts
    valid_discount["Percentage"] = valid_percentage_discounts
    db["Valid Discount"] = valid_discount
    db["Discount Master"] = discount_master

    db.close()
    return valid_discount
checkfordiscounts()

mail = Mail(app)

def searchBar():
    return SearchBar(request.form)

def testing():
    productDict = {}
    db = shelve.open('storage.db', 'c')
    productDict = db['Products']
    print(productDict)
    for product in productDict:
        productDict[product].increase_purchases(random.randint(1,50))
        for x in range(random.randint(40,150)):
            productDict[product].increase_views()
    db['Products'] = productDict
    db.close()

def discount_box(user):
    amount_show = {}
    percentage_show = {}
    show = {}
    amount_dont = []
    percentage_dont = []
    db = shelve.open('storage.db', 'r')
    try:
        valid_discount = db['Valid Discount']
    except:
        valid_discount = False
    amount_discounts = valid_discount.get("Amount")
    percentage_discounts = valid_discount.get("Percentage")
    # print(amount_discounts)
    db.close()

    if user is False:
        show["Amount"] = amount_discounts
        show["Amount"] = amount_discounts
    else:
        users_codes = user.get_discount_codes()
        print(users_codes)

        if valid_discount is not False and bool(users_codes) is True:

            if bool(amount_discounts) is True:
                amount_show = amount_discounts
                for user_code in users_codes:
                    for stored_code in amount_discounts:
                        if user_code.get_code() == stored_code:
                            print("HERE BIVH")
                            amount_dont.append(stored_code)
                if bool(amount_dont) is True:
                    for code in amount_dont:
                        del amount_show[code]
                        print(amount_show)

            if bool(percentage_discounts) is True:
                percentage_show = percentage_discounts
                for user_code in users_codes:
                    for stored_code in percentage_discounts:
                        if user_code.get_code() == stored_code:
                            # dont_show.append(user_code)
                            percentage_dont.append(stored_code)
                if bool(percentage_dont):
                    for code in percentage_dont:
                            del percentage_show[code]
                            print(percentage_show)

        elif valid_discount is not False and bool(users_codes) is False:
            if bool(amount_discounts) is True:
                amount_show = amount_discounts
            if bool(percentage_discounts) is True:
                percentage_show = percentage_discounts

        show["Amount"] = amount_show
        show["Percentage"] = percentage_show
    return show

@app.route('/search/<searchString>/<category>/<order>', methods=['GET', 'POST'])
def search(searchString, category, order):
    searchString = searchString.lower()
    cart=[]
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
    checkfordiscounts()
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

    show = discount_box(current)


    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        return redirect('/search/' + searchForm.search_input.data + '/view/descending')

    return render_template("home.html", current=current, searchForm=searchForm, purchasesList=purchasesList, viewsList=viewsList, Items=Items, show=show)

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

    if editProfileForm.address.data or editProfileForm.phone.data != "":
        activate_disabled_btn = True

    invalid_phone_num_error = False
    edit_email_valid = False
    empty_username_error = False

    if not editProfileForm.username.data.isalnum():
        if editProfileForm.username.data == "":
            empty_username_error = True

    if request.method == "POST":
        current_id = current.get_user_id()
        del namesDict[current.get_username()]
        if empty_username_error:
            print("Username cannot be left blank.")
        else:
            current.set_username(editProfileForm.username.data)
        current.set_address(editProfileForm.address.data)
        # check for valid phone number
        try:
            number = str(editProfileForm.phone.data)
            print("\n\n\n\n\n")
            if number[0] == "6" or number[0] == "8" or number[0] == "9":
                if (len(number) == 8):
                    current.set_phone(editProfileForm.phone.data)
                else:
                    current.set_phone("None")
                    invalid_phone_num_error = True;
            else:
                current.set_phone("None")
                invalid_phone_num_error = True;
        except:
            current.set_phone("None")
        #check for valid email
        try:
            regexEmail = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
            if (re.search(regexEmail,editProfileForm.email.data)):
                #email is valid
                edit_email_valid = True
                current.set_email(editProfileForm.email.data)
            else:
                edit_email_valid = False
                print("Email is incorrect format/cannot be left blank.")
        except:
            current.set_email("None")

        print(current.get_password())
        if current.get_password() == editProfileForm.password.data:
            if editProfileForm.newpassword.data != "":
                current.set_password(editProfileForm.newpassword.data)
                print("New password set for user " + current.get_username() + ", " + editProfileForm.newpassword.data + ".")
            elif editProfileForm.newpassword.data == "":
                print("New password field was left empty.")
                print("No new password was set.")
        elif editProfileForm.newpassword.data != editProfileForm.password.data:
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

        # edit_email_valid = True
        # empty_username_error = True
        # invalid_phone_num_error = True

        searchForm = searchBar()
        if request.method == "POST" and searchForm.validate():
            print(searchForm.search_input.data)
        db.close()
        return render_template('my-account.html', current=current, edit_email_valid=edit_email_valid, empty_username_error=empty_username_error, invalid_phone_num_error=invalid_phone_num_error, name=current.get_username(), address=current.get_address(), phone=current.get_phone(), email=current.get_email(), searchForm=searchForm, Items=Items)
    else:
        searchForm = searchBar()
        if request.method == "POST" and searchForm.validate():
            print(searchForm.search_input.data)
        db.close()
        return render_template('my-account.html', current=current,edit_email_valid=True, empty_username_error=False, invalid_phone_num_error=False, name=current.get_username(), address=current.get_address(), phone=current.get_phone(), email=current.get_email(), searchForm=searchForm, Items=Items)

@app.route('/my-account/delete_account')
def deleteUser():
    db = shelve.open("storage.db", "c")
    try:
        usersDict = db["Users"]
        namesDict = db["Usernames"]
        current = db["Current User"]
    except:
        print("Error while retrieving usersDict")
    current_id = current.get_user_id()
    print("\n\n\n")
    print(f"{usersDict[current_id].get_username()} is deleted.")
    print("\n\n\n")
    del usersDict[current_id]
    db["Users"] = usersDict
    del namesDict[current.get_username()]
    db["Usernames"] = namesDict
    db["Current User"] = ""
    db.close()
    return redirect(url_for("home"))


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
            unique_username = True
            valid_email_registration = True
            secure_pwd = True
            regexEmail = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

            for user in usersDict.values():
                #check email is correct format
                if not(re.search(regexEmail, registrationForm.email.data)):
                    print("Invalid Email")
                    valid_email_registration = False
                    break
                    #check for registered username in system
                if registrationForm.username.data == user.get_username():
                    unique_username = False
                    print("Username in use, you cannot create an account with the same username.")
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
                    break
                if not any(char.isdigit() for char in registrationForm.password.data):
                    print('Password should have at least one numeral')
                    secure_pwd = False
                    break
                if not any(char.isupper() for char in registrationForm.password.data):
                    print('Password should have at least one uppercase letter')
                    secure_pwd = False
                    break
                if not any(char.islower() for char in registrationForm.password.data):
                    print('Password should have at least one lowercase letter')
                    secure_pwd = False
                    break
                # if not any(char in SpecialSym for char in registrationForm.password.data):
                #     print('Password should have at least one of the symbols $@#')
                #     secure_pwd = False
                    break

            if unique_email and valid_email_registration and secure_pwd and unique_username:
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
                return render_template("login.html", edit_email_valid=True, empty_username_error=False, invalid_phone_num_error=False, unique_email=unique_email, unique_username=unique_username, valid_email_registration=valid_email_registration, secure_pwd = secure_pwd, form=loginForm, form2=registrationForm, searchForm=searchForm)

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
                    success_login = True
                    db["Current User"] = user_obj
                    print("User successfully logged in")
                    return redirect(url_for("home"))
                else:
                    searchForm = searchBar()
                    if request.method == "POST" and searchForm.validate():
                        print(searchForm.search_input.data)
                    print("Credentials are incorrect.")
                    return render_template('login.html', username_correct=False, edit_email_valid=True, empty_username_error=False, invalid_phone_num_error=False, unique_email=True, unique_username=True, valid_email_registration=True, secure_pwd = True, form=loginForm, form2=registrationForm, searchForm=searchForm)
            else:
                searchForm = searchBar()
                if request.method == "POST" and searchForm.validate():
                    print(searchForm.search_input.data)
                print("User does not exist.")
                return render_template('login.html', username_correct=False, edit_email_valid=True, empty_username_error=False, invalid_phone_num_error=False, unique_email=True, unique_username=True, valid_email_registration=True, secure_pwd = True, form=loginForm, form2=registrationForm, searchForm=searchForm)

        else:
            searchForm = searchBar()
            if request.method == "POST" and searchForm.validate():
                print(searchForm.search_input.data)
            return render_template('login.html', username_correct=True, edit_email_valid=True, empty_username_error=False, invalid_phone_num_error=False, unique_email=True, unique_username=True, valid_email_registration=True, secure_pwd = True, form=loginForm, form2=registrationForm, searchForm=searchForm)
            print("Exception Error: navigating home.html to login.html")

        searchForm = searchBar()
        if request.method == "POST" and searchForm.validate():
            return redirect('/search/' + searchForm.search_input.data + '/view/descending')
        return render_template('login.html', username_correct=True, edit_email_valid=True, empty_username_error = False, invalid_phone_num_error=False, unique_email=True, unique_username=True, valid_email_registration=True, secure_pwd = True, form=loginForm, form2=registrationForm, searchForm=searchForm)
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

@app.route('/FAQ')
def viewFAQ():
    db = shelve.open("storage.db", "r")
    current = db["Current User"]
    cart = current.get_shopping_cart()
    Items = len(cart)
    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        return redirect('/search/' + searchForm.search_input.data + '/view/descending')
    return render_template("FAQ.html", current=current, searchForm=searchForm, Items=Items)


@app.route('/orderHistory', methods=['GET'])
def orderHistory():
    db = shelve.open("storage.db", "r")
    transactions ={}
    # try:
    current = db["Current User"]
    cart = current.get_shopping_cart()
    Items = len(cart)
    transactions = db["Transactions"]
    current_transac_list = current.get_transactions()
    print("\n\n\n")
    for transaction in current_transac_list:
        obj = transactions[transaction]
        print(transaction) #prints order ID
        print(obj.get_date_of_order())
        date_of_order = obj.get_date_of_order()
        print(obj) #prints object
        items = obj.get_items()

    print("\n\n\n")
    searchForm = searchBar()
    return render_template('orderHistory.html', date_of_order=date_of_order, transaction=obj, current_transac_list=current_transac_list, searchForm=searchForm, Items=Items, current=current, items=transactions)
@app.route('/mainCategory/<mainCategory>/<category>/<order>/', methods=['GET', 'POST'])
def mainCategory(mainCategory, category, order):
    checkfordiscounts()
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
    show = discount_box(current)

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
    return render_template('mainCategory.html', productList=products, productCount=len(products), mainCategory=mainCategory, searchForm=searchForm, current=current, Items=Items, show=show)

# Supplements(one of the subsections)
@app.route('/subCategory/<subCategory>/<category>/<order>/', methods=['GET', 'POST'])
def subCategory(subCategory, category, order):
    checkfordiscounts
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
    show = discount_box(current)

    db.close()

    products = []
    for id in Products:
        product = Products[id]
        if product.get_sub_category() == subCategory:
            if product.get_activated() == True:
                products.append(product)

    mainCategory = get_main_category(subCategory)
    bmainCat = mainCategory.replace(' ', '')
    products = sort_by(products, category, order)

    subCategory = get_name_with_space(subCategory)
    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        return redirect('/search/' + searchForm.search_input.data + '/view/descending')
    return render_template('subCategory.html', bmainCat=bmainCat, productList=products, subCategory=subCategory, productCount=len(products), mainCategory=mainCategory, searchForm=searchForm, current=current, Items=Items, show=show)

# Ribena(one of the products)
@app.route('/IndItem/<serialNo>', methods=['GET', 'POST'])
def IndItem(serialNo):
    checkfordiscounts()
    db = shelve.open('storage.db','w')
    try:
        products = db['Products']
    except:
        print("Error while retrieving products from storage.")
    try:
        current = db['Current User']
        Items = len(current.get_shopping_cart())
    except:
        current = False
        print("Unable to get the current dude!")
        Items = 0

    show = discount_box(current)

    IndItem = products[serialNo]
    IndItem.increase_views()
    class QuantityForm(Form):
        quantity = IntegerField("Quantity", [validators.NumberRange(min=1, max=IndItem.get_quantity(), message="Please select a valid quantity. There are only " + str(IndItem.get_quantity()) + " of this product currently.")])
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
    try:
        cart = current.get_shopping_cart()
        bought = False
        amount = 0
        for serial_no in cart:
            if serial_no == serialNo:
                bought = True
                amount = cart[serial_no]
                break
    except:
        bought = False
        amount = 0
    db['Products'] = products
    db.close()
    subCategory = IndItem.get_sub_category()
    mainCategory = get_main_category(subCategory).replace(' ','')
    relatedProducts = []
    for serial_no in products:
        if get_main_category(products[serial_no].get_sub_category()) == mainCategory:
            relatedProducts.append(products[serial_no])
    relatedProducts.remove(IndItem)
    related = []
    for i in range(4):
        max = len(relatedProducts)
        if max <= 1:
            break
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
    return render_template('IndItem.html', product=IndItem, mainCategory=mainCategory, searchForm=searchForm, current=current, taken=taken, related=related, Items=Items, QuantityForm = Quantity, Bought = bought, amount = amount,show=show)

# Shopping Cart
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    checkfordiscounts()
    deducted=0
    discount= ''
    new_total = 0
    Delivery = NoCollectForm(request.form)
    Discount = DiscountForm(request.form)
    db = shelve.open('storage.db','r')
    current_discount = ''
    try:
        current = db['Current User']
        products = db["Products"]
    except:
        print('Error reading Current User.')
        current = False
        products = {}
    show = discount_box(current)

    cart = current.get_shopping_cart()
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

    current_discount = current.get_current_discount()
    print(current_discount)

    empty = not bool(current_discount)

    if empty == False:
        print("vcgashjkl")
        deducted = current_discount["deducted"]
        discount = current_discount["discount"]
        new_total = float(current_discount["amt_after"])

    if request.method == "POST" and Delivery.validate():
        print("HIIIIIIIIII")
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

    new_total = totalCost
    return render_template('cart.html', cartList=cartList, totalCost=totalCost, searchForm=searchForm, current=current, NoCollectForm = Delivery, Discount=Discount, Items = Items, discount=discount, new_total= new_total, current_discount=current_discount, deducted = deducted, show=show)


@app.route('/useDiscount',  methods=['POST'])
def useDiscount():
    checkfordiscounts()
    searchForm = searchBar()
    Delivery = NoCollectForm(request.form)
    Discount = DiscountForm(request.form)
    discount= ''
    current = ""
    valid_discount = {}
    users_codes = []
    new_total =0
    deducted = 0
    error_msg=''
    current_discount = ''

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

        show = discount_box(current)
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
        users_codes = current.get_discount_codes()
        print(users_codes)

        cartList = []
        totalCost = 0
        for product in cart:
            item = products[product]
            totalCost += float(item.get_price()) * int(cart[product])
            cartList.append(item)
        totalCost = '%.2f' %float(totalCost)
        Items = len(cartList)

        #check use
        check_used = False
        empty = not bool(users_codes)

        if empty == True:
            print("check empty")
            check_used = False
        else:
            for object in users_codes:
                if object.get_code() == code:
                    print(object.get_code())
                    check_used = True
                    error_msg = "You have already used " + code+ "!"

                    db.close()
                    return render_template('cart.html', cartList=cartList, totalCost=totalCost, current=current, NoCollectForm = Delivery, Discount=Discount, Items=Items, error_msg=error_msg, discount=discount, new_total=new_total , searchForm=searchForm, current_discount = current_discount, deducted = deducted, show=show)
                    # return render_template('cart.html', cartList=cartList, totalCost=totalCost, searchForm=searchForm, current=current, NoCollectForm = Delivery, Discount=Discount, Items = Items)

        amount_discounts = {}
        percentage_discounts = {}
        amount_empty = not bool(valid_discount["Amount"])
        percentage_empty = not bool(valid_discount["Percentage"])
        valid = False

        if amount_empty is False:
            amount_discounts = valid_discount["Amount"]
            for key in amount_discounts:
                if key == code:
                    valid = True
                    type = "amount"
                    condition = float(amount_discounts[key].get_condition())
                    discount_in_storage = amount_discounts[key]
                    break


        if percentage_empty is False:
            percentage_discounts = valid_discount["Percentage"]
            for key in percentage_discounts:
                if key == code:
                    valid = True
                    type = "percentage"
                    condition = float(percentage_discounts[key].get_condition())
                    discount_in_storage = percentage_discounts[key]
                    break
            error_msg = "Invalid discount code."

        if valid == False:
            db.close()
            error_msg = "Invalid discount code."
            return render_template('cart.html', cartList=cartList, totalCost=totalCost, current=current, NoCollectForm = Delivery, Discount=Discount, Items=Items, error_msg=error_msg, discount=discount, new_total=new_total, searchForm=searchForm, current_discount=current_discount, deducted = deducted, show=show)

        if valid is True and check_used==False and float(totalCost) >= condition:
            print("TRUUUUU")
            discount = discount_in_storage
            print(discount)
            print(users_codes)
            current_discount = current.get_current_discount()
            current_discount["discount"] = discount
            totalCost = '%.2f' %float(totalCost)
            current_discount["amt_before"] = totalCost
            # totalCost = totalCost
            condition = discount.get_condition()
            if float(totalCost) >= (condition):
                totalCost = Decimal(format(float(totalCost), '.2f'))
                if isinstance(discount, AmountDiscount):
                    print("its here")
                    amount = discount.get_discount_amount()
                    deducted = amount
                    new_total = totalCost - Decimal(format(float(amount), '.2f'))
                    current_discount["amt_after"] = Decimal(format(new_total, '.2f'))
                    current_discount["deducted"] = amount
                else:
                    percentage = discount.get_discount_percentage()
                    new_total = totalCost - totalCost * (percentage /100)
                    current_discount["amt_after"] = Decimal(format(new_total, '.2f'))
                    current_discount["deducted"] = Decimal(format(totalCost * percentage/100 , '.2f'))
                    deducted = current_discount["deducted"]
                totalCost = '%.2f' %float(totalCost)
                new_total = Decimal(format(new_total, '.2f'))
                current.set_current_discount(current_discount)
                db["Current User"] = current
                db.close()

                return render_template('cart.html', cartList=cartList, totalCost=totalCost, current=current, NoCollectForm = Delivery, Discount=Discount, Items=Items, error_msg=error_msg, discount=discount,new_total=new_total, searchForm=searchForm, current_discount=current_discount, deducted = deducted, show=show)
        else:
            db.close()
            error_msg = code + " not applicable"
            print(error_msg)
            return render_template('cart.html', cartList=cartList, totalCost=totalCost, current=current, NoCollectForm = Delivery, Discount=Discount, Items=Items, error_msg=error_msg, discount=discount,new_total=new_total, searchForm=searchForm, current_discount=current_discount, deducted = deducted, show=show)

@app.route("/removeUseDiscount", methods=["POST"])
def removeUseDiscount():
    print("remocve")
    current = ''
    db = shelve.open('storage.db', 'c')
    try:
        current = db["Current User"]
    except:
        print('Error in retrieving current user from storage.db.')

    empty = {}
    current.set_current_discount(empty)
    db["Current User"] = current
    db.close()

    return redirect(url_for('cart'))

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
    deducted = 0
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

    current_discount = current.get_current_discount()

    cart = current.get_shopping_cart()
    prodlist = []
    subtotal = 0
    for key in cart:
        product = products[key]
        product.set_quantity(int(cart[key]))
        prodlist.append(product)
        subtotal += float(product.get_price()) * int(cart[key])
    number = len(prodlist)
    empty = not bool(current_discount)
    if empty == False:
        deducted = float(current_discount["deducted"])
        discount = current_discount["discount"]
        total = subtotal + 12 - deducted

    else:
        deducted = 0
        discount = ''
        total = subtotal + 12
    db.close()
    today = date.today()
    currentDate = today.strftime("%d %B %Y")
    if request.method == "POST" and deliveryForm.validate():
        db = shelve.open('storage.db','c')
        current = db["Current User"]
        print(deliveryForm.unit_no.data)
        deliveryInfo = Delivery(currentDate, deliveryForm.name.data, deliveryForm.phone.data,
                    current.get_email(),total, deducted, discount, prodlist, deliveryForm.payment_mode.data,
                     deliveryForm.credit_card_number.data, deliveryForm.credit_card_expiry.data, deliveryForm.credit_card_cvv.data,
                     deliveryForm.street_name.data,deliveryForm.postal_code.data,deliveryForm.unit_no.data)

        pickle_out = open('temp_transaction.pickle','wb')
        pickle.dump(deliveryInfo, pickle_out)
        pickle_out.close()
        db.close()
        return redirect(url_for("summary"))
    if request.method == "POST" and collectionForm.validate():
        db = shelve.open('storage.db','c')
        current = db["Current User"]
        collection = Collection(currentDate, collectionForm.name.data, collectionForm.phone.data, current.get_email(), total, deducted, discount, prodlist,
        collectionForm.payment_mode.data, collectionForm.credit_card_number.data, collectionForm.credit_card_expiry.data, collectionForm.credit_card_cvv.data,
        collectionForm.date.data, collectionForm.time.data)
        pickle_out = open('temp_transaction.pickle','wb')
        pickle.dump(collection, pickle_out)
        pickle_out.close()
        db.close()
        return redirect(url_for("summary"))
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

    return render_template('checkout.html', deliveryform=deliveryForm, current=current, collectionform =collectionForm, searchForm=searchForm, cart=prodlist, total=total, number=number, subtotal =subtotal, delivery = NoCollect, Items = 0, deducted=deducted, discount=discount)

# Summary page
@app.route('/summary', methods= ["GET", "POST"])
def summary():
    db = shelve.open('storage.db','r')
    pickle_in = open('temp_transaction.pickle','rb')
    transaction = pickle.load(pickle_in)
    pickle_in.close()
    print(transaction.get_name())
    try:
        current = db["Current User"]
    except:
        print("Error in retrieving current user from storage")
    db.close()
        # if request.method == "POST" and searchForm.validate():
        #     return redirect('/search/' + searchForm.search_input.data)
    creditNo = str(transaction.get_credit_card_number())
    lastThree = creditNo[-4:-1]
    print(creditNo)
    aterisk = len(creditNo) - 3
    ateriskNo = aterisk * '*'
    encryptNo = ateriskNo + lastThree
    transaction.set_credit_card_number(encryptNo)

    type = transaction.get_type()
    if type == "delivery":
        D = True
    else:
        D = False
    searchForm = searchBar()
    return render_template('summary.html', searchForm=searchForm, details=transaction, Items = 0, type = D, current = current)

@app.route('/confirm/<type>', methods = ["GET", "POST"])
def confirm(type):
    print("Velai seiyuthu")
    db = shelve.open('storage.db','c')
    pickle_in = open('temp_transaction.pickle', 'rb')
    transaction = pickle.load(pickle_in)
    pickle_in.close()
    try:
        current = db["Current User"]
        products = db["Products"]
        transactions = db["Transactions"]
        discount_master = db["Discount Master"]
    except:
        print("Nah man this can't be happenin")
    transactions[transaction.get_id()] = transaction
    db["Transactions"] = transactions
    print("Transactions updated on admin")
    current.set_transactions(transaction.get_id())
    print("Transaction history updated for user")
    test = transaction.get_discount()
    if test:
        discount = test
        users_codes = current.get_discount_codes()
        users_codes.append(discount)
        # current.set_current_discount(current_discount)
        current.set_discount_codes(users_codes)
        current_discount = current.get_current_discount()
        current_discount.clear()
        current.set_current_discount(current_discount)
        for thing in discount_master:
            if thing == discount:
                used = thing.get_used()
                used += 1
                thing.set_used(used)
    else:
        print("Oop no discount used")
    cart = current.get_shopping_cart()
    for key in cart:
        product = products[key]
        print(product.get_quantity())
        product.set_quantity(product.get_quantity() - int(cart[key]))
        product.increase_purchases(int(cart[key]))
        products[key] = product
        print(product.get_quantity(),"prods left")
    db["Products"] = products
    print("Prods successfully updated")
    current.set_shopping_cart({})
    db["Current User"] = current
    print("Resetted shopping cart")
    db.close()
    print("Database closed")
    if type == "feedback":
        return redirect(url_for('feedback'))
    else:
        return redirect(url_for('home'))
# feedback page
@app.route('/feedback', methods = ["GET", "POST"])
def feedback():
    feedbackForm = FeedbackForm(request.form)
    searchForm = searchBar()

    try:
        db = shelve.open('storage.db', 'r')
        current = db["Current User"]
    except:
        print("Error in retrieving current user for feedback")

    if request.method == "POST" and feedbackForm.validate():
        db = shelve.open('storage.db', 'c')
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

    return render_template('feedback.html', searchForm=searchForm, feedbackForm=feedbackForm, current=current, Items = 0)

@app.route('/displayFeedback')
def displayFeedback():
    feedbacks = {}
    db = shelve.open('storage.db', 'r')
    try:
        feedbacks = db["Feedback"]
        print(feedbacks)
    except:
        print("error")

    return render_template('adminFeedback.html', feedbackList = feedbacks, currentPage='Feedback')

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
        transactionsDict = db['Transactions']
        db.close()
    except:
        print('Error in retrieving Products from storage.db.')

    transactionList = []

    for id in transactionsDict:
        if transactionsDict[id].get_completion()==False:
            transactionList.append(transactionsDict[id])
    transactionList.reverse()

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
    , viewsGraph = viewsGraph, lowStockList=lowStockList, midStockList=midStockList, transactions=transactionList, stockPage=stockPage, stockList=stockList)

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
    searchString = searchString.lower()
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
    searchString = searchString.lower()
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
        return redirect('/addStock')

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

@app.route('/deleteStockChoice/<serialNo>')
def deleteStockChoice(serialNo):
    newStock = {}
    db = shelve.open('storage.db', 'r')
    try:
        newStock = db['New Stock']
    except:
        print('Error in retrieving New Stock from storage.db.')
    print(newStock)
    newStock.pop(serialNo)
    db['New Stock'] = newStock
    db.close()
    return redirect('/addStock')

@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    transactionsDict = {}
    deliveryCompleteList = []
    deliveryNotCompleteList = []
    collectionCompleteList = []
    collectionNotCompleteList = []

    db = shelve.open('storage.db', 'c')

    try:
        transactionsDict = db['Transactions']
    except:
        print('Error in retrieving Transactions from storage.db.')

    for key in transactionsDict:
        if transactionsDict[key].get_type()=='delivery':
            if transactionsDict[key].get_completion()==True:
                deliveryCompleteList.append(transactionsDict[key])
            else:
                deliveryNotCompleteList.append(transactionsDict[key])
        else:
            if transactionsDict[key].get_completion()==True:
                collectionCompleteList.append(transactionsDict[key])
            else:
                collectionNotCompleteList.append(transactionsDict[key])

    deliveryCompleteList.reverse()
    deliveryNotCompleteList.reverse()
    collectionCompleteList.reverse()
    collectionNotCompleteList.reverse()

    exportForm = ExportTransaction(request.form)

    if request.method=="POST":
        d_mark_complete_transactions = request.form.getlist("dMarkAsComplete")
        for sn in d_mark_complete_transactions:
            transactionsDict[int(sn)].set_completion(True)
            print(d_mark_complete_transactions)

        d_mark_incomplete_transactions = request.form.getlist("dMarkAsIncomplete")
        for sn in d_mark_incomplete_transactions:
            transactionsDict[int(sn)].set_completion(False)
            print(d_mark_incomplete_transactions)

        c_mark_complete_transactions = request.form.getlist("cMarkAsComplete")
        for sn in c_mark_complete_transactions:
            transactionsDict[int(sn)].set_completion(True)
            print(c_mark_complete_transactions)

        c_mark_incomplete_transactions = request.form.getlist("cMarkAsIncomplete")
        for sn in c_mark_incomplete_transactions:
            transactionsDict[int(sn)].set_completion(False)
            print(c_mark_incomplete_transactions)

        db['Transactions'] = transactionsDict
        db.close()

        return redirect('/transactions')

    return render_template('transactions.html', currentPage='Transactions'
    , deliveryCompleteList=deliveryCompleteList, deliveryNotCompleteList=deliveryNotCompleteList
    , collectionCompleteList=collectionCompleteList, collectionNotCompleteList=collectionNotCompleteList
    , exportForm=exportForm)

@app.route('/downloadProducts', methods=['GET'])
def downloadProducts():
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

@app.route('/downloadTransactions/<delivery>/<collection>/<uncompleted>/<completed>', methods=['GET'])
def downloadTransactions(delivery, collection, completed, uncompleted):
    print(delivery, collection, uncompleted, completed)
    transactionsDict = {}
    deliveryCompleteList = []
    deliveryNotCompleteList = []
    collectionCompleteList = []
    collectionNotCompleteList = []
    finalData = []

    db = shelve.open('storage.db', 'r')

    try:
        transactionsDict = db['Transactions']
    except:
        print('Error in retrieving Transactions from storage.db.')

    for key in transactionsDict:
        if transactionsDict[key].get_type()=='delivery':
            if transactionsDict[key].get_completion()==True:
                deliveryCompleteList.append(transactionsDict[key])
            else:
                deliveryNotCompleteList.append(transactionsDict[key])
        else:
            if transactionsDict[key].get_completion()==True:
                collectionCompleteList.append(transactionsDict[key])
            else:
                collectionNotCompleteList.append(transactionsDict[key])

    deliveryCompleteList.reverse()
    deliveryNotCompleteList.reverse()
    collectionCompleteList.reverse()
    collectionNotCompleteList.reverse()

    deliveryArray = ['Status'
                    , 'Delivery Type'
                    , 'Date of Order'
                    , 'Name'
                    , 'Contact No.'
                    , 'Email'
                    , 'Payment Mode'
                    , 'Credit Card No.'
                    , 'Expiry Date'
                    , 'CVV'
                    , 'Address'
                    , 'Items'
                    , 'Total']

    collectionArray = ['Status'
                        , 'Delivery Type'
                        , 'Date of Order'
                        , 'Name'
                        , 'Contact No.'
                        , 'Email'
                        , 'Payment Mode'
                        , 'Credit Card No.'
                        , 'Expiry Date'
                        , 'CVV'
                        , 'Collection Date/Time'
                        , 'Items'
                        , 'Total']

    if delivery=='true':
        finalData.append(deliveryArray)

        if completed=='true':
            for t in deliveryCompleteList:
                itemList = []
                count = 1
                for item in t.get_items():
                    itemData = ''
                    itemData += str(count) + '. ' + item.get_product_name() + '(' + item.get_serial_no() + '), Quantity: ' + str(item.get_quantity())
                    itemList.append(itemData)
                    count += 1

                address = t.get_street_name() + ', #' + str(t.get_unit_no()) + ' (S' + str(t.get_postal_code()) + ')'
                data = ['Delivered'
                        , 'Delivery'
                        , t.get_date_of_order()
                        , t.get_name()
                        , t.get_phone()
                        , t.get_email()
                        , t.get_payment_mode()
                        , str(t.get_credit_card_number())
                        , t.get_credit_card_expiry()
                        , t.get_credit_card_cvv()
                        , address
                        , itemList[0]
                        , '$' + t.get_total()]

                finalData.append(data)

                if len(itemList)>1:
                    for x in range(len(itemList)-1):
                        data = ['','','','','','','','','','','',itemList[x+1]]
                        finalData.append(data)

        if uncompleted=='true':
            for t in deliveryNotCompleteList:
                itemList = []
                count = 1
                for item in t.get_items():
                    itemData = ''
                    itemData += str(count) + '. ' + item.get_product_name() + '(' + item.get_serial_no() + '), Quantity: ' + str(item.get_quantity())
                    itemList.append(itemData)
                    count += 1

                address = t.get_street_name() + ', #' + str(t.get_unit_no()) + ' (S' + str(t.get_postal_code()) + ')'
                data = ['Not Delivered'
                        , 'Delivery'
                        , t.get_date_of_order()
                        , t.get_name()
                        , t.get_phone()
                        , t.get_email()
                        , t.get_payment_mode()
                        , str(t.get_credit_card_number())
                        , t.get_credit_card_expiry()
                        , t.get_credit_card_cvv()
                        , address
                        , itemList[0]
                        , '$' + t.get_total()]

                finalData.append(data)

                if len(itemList)>1:
                    for x in range(len(itemList)-1):
                        data = ['','','','','','','','','','','',itemList[x+1]]
                        finalData.append(data)

        if collection=='true':
            finalData.append([])
            finalData.append([])

    if collection=='true':
        finalData.append(collectionArray)

        if completed=='true':
            for t in collectionCompleteList:
                itemList = []
                count = 1
                for item in t.get_items():
                    itemData = ''
                    itemData += str(count) + '. ' + item.get_product_name() + '(' + item.get_serial_no() + '), Quantity: ' + str(item.get_quantity())
                    itemList.append(itemData)
                    count += 1

                data = ['Collected'
                        , 'Collection'
                        , t.get_date_of_order()
                        , t.get_name()
                        , t.get_phone()
                        , t.get_email()
                        , t.get_payment_mode()
                        , str(t.get_credit_card_number())
                        , t.get_credit_card_expiry()
                        , t.get_credit_card_cvv()
                        , str(t.get_date()) + ', ' + str(t.get_time())
                        , itemList[0]
                        , '$' + t.get_total()]

                finalData.append(data)

                if len(itemList)>1:
                    for x in range(len(itemList)-1):
                        data = ['','','','','','','','','','','',itemList[x+1]]
                        finalData.append(data)

        if uncompleted=='true':
            for t in collectionNotCompleteList:
                itemList = []
                count = 1
                for item in t.get_items():
                    itemData = ''
                    itemData += str(count) + '. ' + item.get_product_name() + '(' + item.get_serial_no() + '), Quantity: ' + str(item.get_quantity())
                    itemList.append(itemData)
                    count += 1

                data = ['Not Collected'
                        , 'Collection'
                        , t.get_date_of_order()
                        , t.get_name()
                        , t.get_phone()
                        , t.get_email()
                        , t.get_payment_mode()
                        , str(t.get_credit_card_number())
                        , t.get_credit_card_expiry()
                        , t.get_credit_card_cvv()
                        , str(t.get_date()) + ', ' + str(t.get_time())
                        , itemList[0]
                        , '$' + t.get_total()]

                finalData.append(data)

                if len(itemList)>1:
                    for x in range(len(itemList)-1):
                        data = ['','','','','','','','','','','',itemList[x+1]]
                        finalData.append(data)

    return excel.make_response_from_array(finalData, file_type='xls', file_name='Delorem Ipsum transaction records')

# Other stuff
@app.route('/discount/<category>/<order>/', methods=['GET', 'POST'])
def discount(category, order):
    AddDiscountAmount = AddDiscountAmountForm(request.form)
    AddDiscountPercentage = AddDiscountPercentageForm(request.form)
    db = shelve.open('storage.db', 'c')
    amount_discounts = {}
    percentage_discounts = {}
    valid_discount = {}
    discount_master = []
    show_master = []
    try:
        discount_master = db['Discount Master']
    except:
        print("Error in retrieving discount master from storage.")

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

    if bool(discount_master) is True:
        # print("discount maser is true")
        show_master = discount_master
        # for thing in discount_master:
        #     show_master.append(thing)
            # show_master = filter_discount(show_master, category, order)
    amt_show_master = []
    pct_show_master= []
    for thing in show_master:
        if type_key(thing) == "Amount":
            amt_show_master.append(thing)
            amt_show_master = filter_discount(amt_show_master, category, order)
        else:
            pct_show_master.append(thing)
            pct_show_master = filter_discount(pct_show_master, category, order)

    print("hellllllllooooooooooo", show_master)

    if request.method == "POST" and AddDiscountAmount.validate():
        start = AddDiscountAmount.discount_start.data
        expire = AddDiscountAmount.discount_expiry.data
        if start <= date.today() and expire >= date.today():
            status = "active"
        elif start > date.today() and expire > start:
            status = "inactive"
        elif start < date.today() and expire <date.today():
            status = "expired"
        used = 0
        code=AddDiscountAmount.discount_code.data
        discount = AmountDiscount(AddDiscountAmount.discount_code.data, AddDiscountAmount.discount_condition.data, AddDiscountAmount.discount_start.data, AddDiscountAmount.discount_expiry.data, status, used,AddDiscountAmount.discount_amount.data)
            # empty = bool(valid_discount['Amount'])
        discount_master.append(discount)
        db["Discount Master"] = discount_master
        test = valid_discount.get('Amount')
        if status == "active":
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

    if request.method == "POST" and AddDiscountPercentage.validate():
        start = AddDiscountPercentage.discount_start.data
        expire = AddDiscountPercentage.discount_expiry.data
        if start <= date.today() and expire >= date.today():
            status = "active"
        elif start > date.today() and expire > start:
            status = "inactive"
        elif start < date.today() and expire <date.today():
            status = "expired"
        used = 0
        code=AddDiscountPercentage.discount_code.data
        discount = PercentageDiscount(AddDiscountPercentage.discount_code.data, AddDiscountPercentage.discount_condition.data, AddDiscountPercentage.discount_start.data,AddDiscountPercentage.discount_expiry.data, status, used, AddDiscountPercentage.discount_percentage.data)
        discount_master.append(discount)
        db["Discount Master"] = discount_master
        test = valid_discount.get('Percentage')
        print(status)
        if status == "active":

            if test:
                percentage_discounts = valid_discount['Percentage']
                percentage_discounts[AddDiscountPercentage.discount_code.data] = discount
                valid_discount['Percentage'] = percentage_discounts
                db['Valid Discount'] = valid_discount
            else:
                print('elseeeee')
                valid_discount['Percentage'] = percentage_discounts
                percentage_discounts[AddDiscountPercentage.discount_code.data] = discount
                valid_discount['Percentage'] = percentage_discounts
                db['Valid Discount'] = valid_discount

        test = valid_discount.get('Amount')
        if test:
            amount_discounts = valid_discount['Amount']
        else:
            amount_discounts = amount_discounts

        # db.close()
        #
        # return render_template('discount.html', currentPage="Discount", AddDiscountAmount=AddDiscountAmount, AddDiscountPercentage=AddDiscountPercentage, valid_discount=valid_discount, amount_discounts=amount_discounts, percentage_discounts=percentage_discounts, code=code)
    print(percentage_discounts)
    print(amount_discounts)
    db.close()
    return render_template('discount.html', currentPage="Discount", AddDiscountAmount=AddDiscountAmount, AddDiscountPercentage=AddDiscountPercentage, valid_discount=valid_discount, amount_discounts=amount_discounts, percentage_discounts=percentage_discounts, show_master=show_master, pct_show_master=pct_show_master, amt_show_master=amt_show_master)


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
    db.close()

    return redirect('/discount/status/active')


@app.route('/categories')
def categories():
    return render_template('categories.html')

@app.route('/deliveryInvoice/<email>/')
def deliveryInvoice(email):
    print("hey!")
    current_user = ""
    products = {}
    transactions = {}
    db = shelve.open('storage.db', 'r')
    try:
        current_user = db["Current User"]
    except:
        print('Error in retrieving current user from storage.db.')
    try:
        products = db["Products"]
    except:
        print('Error in retrieving products from storage.db.')

    pickle_in = open('temp_transaction.pickle','rb')
    transaction = pickle.load(pickle_in)
    pickle_in.close()
    order_ID = transaction.get_id()

    cart = current_user.get_shopping_cart()
    productList = []

    images = []
    for object in transaction.get_items() :
        productList.append(object)
        images.append(object.get_thumbnail())

    total = transaction.get_total()
    total = Decimal(format(float(total), '.2f'))
    deducted = transaction.get_deducted()
    deducted = Decimal(format(float(deducted), '.2f'))
    print(total)
    print(deducted)

    try:
        msg = Message("Delorem Ipsum Pharmacy",
        sender="deloremipsumonlinestore@outlook.com",
        recipients=[email])

        for image in images:
            print("\n\n\nGoes into images")
            this_folder = os.path.dirname(os.path.abspath(__file__))
            print("This_folder")
            source = this_folder + "/static/images/" + image
            print(source)
            with app.open_resource(source) as fp:
                msg.attach(source, "image/jpg", fp.read())
                print("attached")

        msg.body = "This ur e reciept"
        msg.html = render_template('html_in_invoice.html',  productList=productList, current_user=current_user, transaction=transaction, cart=cart, products=products, order_ID=order_ID, total=total, deducted=deducted )
        print("testinggggggggggggggg")
        mail.send(msg)
        print("\n\n\nMAIL SENT\n\n\n")


    except Exception as e:

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
    checkfordiscounts()
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

    show = discount_box(current)

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
    return render_template('listOfBrands.html', searchForm=searchForm, brandsDict=brandsDict, current=current, Items=Items, show=show)

@app.route('/Brand/<brand>', methods=['GET', 'POST'])
def brand(brand):
    checkfordiscounts()
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

    show = discount_box(current)

    products = []
    for id in Products:
        product = Products[id]
        if brand.lower() == product.get_brand().lower():
            if product.get_activated() == True:
                products.append(product)

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        return redirect('/search/' + searchForm.search_input.data)
    return render_template('productByBrand.html', productList=products, productCount=len(products), searchForm=searchForm, brand=brand, current=current, Items = Items, show=show)

app.jinja_env.filters['get_name_with_space'] = get_name_with_space
if __name__=='__main__':
    excel.init_excel(app)
    app.run(debug=True)
