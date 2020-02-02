import shelve, string, random
from flask import Flask, render_template, request, redirect, url_for
from Forms import *
from StorageClass import *
from Functions import *
from User import *
from deliveryDetails import *

# Image download
from werkzeug.utils import secure_filename
import os
from pathlib import Path

# Graphing
import json
import plotly

import pandas as pd
import numpy as np
import plotly.graph_objs as go

# Flask mail
from flask_mail import Mail, Message
import sys
import asyncio
from threading import Thread

app = Flask(__name__, static_url_path='/static')
app.config.update(
    MAIL_SERVER= 'smtp.office365.com',
    MAIL_PORT= 587,
    MAIL_USE_TLS= True,
    MAIL_USE_SSL= False,
	MAIL_USERNAME = '191993Y@mymail.nyp.edu.sg',
	MAIL_PASSWORD = '4mhzlkwjhfrA',
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

@app.route('/search/<searchString>', methods=['GET', 'POST'])
def search(searchString):
    db = shelve.open('storage.db', 'r')
    try:
        Products = db["Products"]
    except:
        print("Error in retrieving products from shelve")

    products = []
    for id in Products:
        product = Products[id]
        if searchString in product.get_product_name().lower() or searchString in product.get_brand().lower():
            if product.get_activated() == True:
                products.append(product)

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        return redirect('/search/' + searchForm.search_input.data)
    return render_template('search.html', productList=products, searchString=searchString, productCount=len(products), searchForm=searchForm)

# Homepage
@app.route('/home', methods=['GET', 'POST'])
def home():
    productDict = {}

    db = shelve.open('storage.db', 'c')
    try:
        current = db["Current User"]
    except:
        print("Error while retrieving current user: user not logged in")
        current = False

    try:
        productDict = db['Products']
        db.close()
    except:
        print('Error in retrieving Products from storage.db.')

    productList = []
    healthList = []
    for key in productDict:
        product = productDict[key]
        productList.append(product)

        if product.get_sub_category() in ['Eye&EarCare', 'Pain&Fever', 'Supplements']:
            if product.get_activated() == True:
                healthList.append(product)

    purchasesList = sort_by(productList, 'purchase', 'descending')[:6]
    viewsList = sort_by(productList,'view','descending')[:6]

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        return redirect('/search/' + searchForm.search_input.data)

    return render_template("home.html", current=current, searchForm=searchForm, purchasesList=purchasesList, healthList=healthList, viewsList=viewsList)

# Profile/Username
@app.route('/my-account/<username>', methods=['GET', 'POST'])
def view_profile(username):
    db = shelve.open("storage.db", "c")
    try:
        usersDict = db["Users"]
        namesDict = db["Usernames"]
        current = db["Current User"]
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
                print("New password set for user " + current.get_username() + ", " + current.get_password())
            else:
                print("Current user password was incorrect.")
        else:
            print("No new password u baka")

        usersDict[current_id] = current
        namesDict[current.get_username()] = current_id
        db["Users"] = usersDict
        db["Usernames"] = namesDict
        db["Current User"] = current

        searchForm = searchBar()
        if request.method == "POST" and searchForm.validate():
            print(searchForm.search_input.data)
        db.close()
        return render_template('my-account.html', current=current, name=current.get_username(), address=current.get_address(), phone=current.get_phone(), email=current.get_email(), searchForm=searchForm)
    else:
        searchForm = searchBar()
        if request.method == "POST" and searchForm.validate():
            print(searchForm.search_input.data)
        db.close()
        return render_template('my-account.html', current=current, name=current.get_username(), address=current.get_address(), phone=current.get_phone(), email=current.get_email(), searchForm=searchForm)

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
            U = User(registrationForm.username.data, registrationForm.password.data, registrationForm.email.data)
            usersDict[U.get_user_id()] = U
            namesDict[U.get_username()] = U.get_user_id()
            db['Users'] = usersDict
            db['Usernames'] = namesDict
            db.close()
            print("User created with name", U.get_username(), "id", U.get_user_id(),
             "Password", U.get_password(), "and Email", U.get_email())

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

            # current_user = usersDict[exist]
            # db["Current User"] = current_user
            # db.close()
            # password = current_user.get_password()
            # username = current_user.get_username()

            if loginForm.username.data == "admin" and loginForm.password.data == "admin":
                return redirect('/dashboard')

            username_exist = False
            login_correct = False

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
                    return redirect(url_for("home"))
                else:
                    searchForm = searchBar()
                    if request.method == "POST" and searchForm.validate():
                        print(searchForm.search_input.data)
                    print("Credentials are incorrect.")
                    return render_template('login.html', username_correct=False, form=loginForm, form2=registrationForm, searchForm=searchForm)
            else:
                searchForm = searchBar()
                if request.method == "POST" and searchForm.validate():
                    print(searchForm.search_input.data)
                print("User does not exist.")
                return render_template('login.html', username_correct=False, form=loginForm, form2=registrationForm, searchForm=searchForm)

        else:
            searchForm = searchBar()
            if request.method == "POST" and searchForm.validate():
                print(searchForm.search_input.data)
            return render_template('login.html', username_correct=True, form=loginForm, form2=registrationForm, searchForm=searchForm)
            print("Exception Error: navigating home.html to login.html")

        searchForm = searchBar()
        if request.method == "POST" and searchForm.validate():
            return redirect('/search/' + searchForm.search_input.data)
        return render_template('login.html', username_correct=True, form=loginForm, form2=registrationForm, searchForm=searchForm)
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
    db.close()
    #METHOD GET - history of order transaction
    return render_template('orderHistory.html')

# Supplements(one of the subsections)
@app.route('/subCategory/<subCategory>/', methods=['GET', 'POST'])
def supplements(subCategory):
    db = shelve.open('storage.db', 'r')
    try:
        Products = db["Products"]
    except:
        print("Error in retrieving products from shelve")
    try:
        current = db["Current User"]
    except:
        print("Error in retrieving current user, subcat")
    products = []
    for id in Products:
        product = Products[id]
        if product.get_sub_category() == subCategory:
            if product.get_activated() == True:
                products.append(product)

    mainCategory = get_main_category(subCategory)

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        return redirect('/search/' + searchForm.search_input.data)
    return render_template('supplements.html', productList=products, subCategory=subCategory, productCount=len(products), mainCategory=mainCategory, searchForm=searchForm)

# Ribena(one of the products)
@app.route('/IndItem/<serialNo>', methods=['GET', 'POST'])
def IndItem(serialNo):
    db = shelve.open('storage.db','w')
    current=""
    try:
        products = db['Products']
    except:
        print("Error while retrieving products from storage.")
    try:
        current = db['Current User']
    except:
        print("Unable to get the current dude!")
    IndItem = products[serialNo]
    IndItem.increase_views()
    wishlist = current.get_wishlist()
    taken = False
    for serial_no in wishlist:
        if serial_no == serialNo:
            taken = True
            break
    db['Products'] = products
    db.close()
    subCategory = IndItem.get_sub_category()
    mainCategory = get_main_category(subCategory)

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        return redirect('/search/' + searchForm.search_input.data)
    return render_template('IndItem.html', product=IndItem, mainCategory=mainCategory, searchForm=searchForm, current=current, taken=taken)

# Shopping Cart
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    db = shelve.open('storage.db','r')
    try:
        user = db['Current User']
        current = db['Current User']
    except:
        print('Error reading Current User.')
        current = False

    cart = user.get_shopping_cart()
    db.close()
    cartList = []
    totalCost = 0
    for product in cart:
        totalCost += float(cart[product].get_price())
        cartList.append(cart[product])
    totalCost = '%.2f' %float(totalCost)

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        return redirect('/search/' + searchForm.search_input.data)
    return render_template('cart.html', cartList=cartList, totalCost=totalCost, searchForm=searchForm, current=current)

@app.route("/addToCart/<name>", methods=['GET', 'POST'])
def addToCart(name):
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
            current_user.add_to_cart(product)
            break

    db['Current User'] = current_user
    cart = current_user.get_shopping_cart()
    db.close()

    # searchForm = searchBar()
    # if request.method == "POST" and searchForm.validate():
    #     return redirect('/search/' + searchForm.search_input.data)
    return redirect("/cart")

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
    cart = current_user.get_shopping_cart()
    db.close()
    cartList = []
    totalCost = 0
    for product in cart:
        totalCost += float(cart[product].get_price())
        cartList.append(cart[product])
    totalCost ='%.2f' %float(totalCost)

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        return redirect('/search/' + searchForm.search_input.data)
    return render_template('cart.html', cartList=cartList, totalCost=totalCost, searchForm=searchForm)

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
    current_user = ""
    db = shelve.open('storage.db', 'r')
    try:
        current_user = db["Current User"]
    except:
        print('Error in retrieving current user from storage.db.')

    wishlist = current_user.get_wishlist()

    db.close()

    filtered_list = []
    for key in wishlist:
        product = wishlist[key]
        filtered_list.append(product)
        filtered_list = filter_function(filtered_list, filter)

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        return redirect('/search/' + searchForm.search_input.data)
    return render_template('wishlist.html', filtered_list=filtered_list, searchForm=searchForm, filter_breadcrumb=filter_breadcrumb)

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
    #     return redirect('/search/' + searchForm.search_input.data)
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
    cart[serialNo] = product
    current_user.set_shopping_cart(cart)
    current_user.remove_from_wishlist(product)
    db["Current User"] = current_user
    db.close()
    return redirect('/wishlist/a-z')

# Checkout
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    current = "" #define current pls yuxde
    searchForm = searchBar()
    deliveryForm = DeliveryForm(request.form)
    collectionForm = CollectionForm(request.form)
    db = shelve.open('storage.db', 'c')
    transactions = {}
    try:
        current = db["Current User"]
    except:
        print("Error in retrieving current user for checkout")
    try:
        transactions = db["Transactions"]
    except:
        print("error in retrieving transaction information")

    cart = current.get_shopping_cart()
    prodlist = []
    total = 0
    for key in cart:
        prodlist.append(cart[key])
        total += float(cart[key].get_price())
    number = len(prodlist)
    if request.method == "POST" and deliveryForm.validate():
        deliveryInfo = Transaction(deliveryForm.name.data, deliveryForm.phone.data, current.get_email(), total, prodlist, deliveryForm.payment_mode.data, deliveryForm.credit_card_number.data, deliveryForm.credit_card_expiry.data, deliveryForm.credit_card_cvv.data)
    # current.set_transactions(deliveryInfo.get_id())
    # transactions[deliveryInfo.get_id()] = deliveryInfo
    # db["Transactions"] = transactions
    #     current.set_orders(deliveryInfo.get_id())
    #     db["Current User"] = current
    #     db.close()
    #     return render_template('checkout.html', current=current, completedForm=deliveryInfo, searchForm=searchForm, cart=prodlist, total=total, number=number)
        print(deliveryInfo.get_name())
    total = "%.2f" %float(total)
    # if request.method == "POST" and searchForm.validate():
    #     return redirect('/search/' + searchForm.search_input.data)

    return render_template('checkout.html', deliveryform=deliveryForm, current=current, collectionform =collectionForm, searchForm=searchForm, cart=prodlist, total=total, number=number)

# Summary page
@app.route('/summary', methods= ["GET", "POST"])
def summary(order):
    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        return redirect('/search/' + searchForm.search_input.data)

    details.get_street_name()
    details.get_postal_code()
    details.get_unit_no()
    details.get_name()
    details.get_phone()
    details.get_payment_mode()
    details.get_credit_card_number()
    details.get_credit_card_expiry()
    details.get_credit_card_cvv()

    if request.method == "POST":
        db = open.shelve('storage.db', 'c')
        details = db[Transactions]
    return render_template('summary.html', searchForm=searchForm, details=order)


# Admin Side
@app.route('/dashboard')
def dashboard():
    productDict = {}
    db = shelve.open('storage.db', 'c')

    try:
        productDict = db['Products']
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

    viewsList = sort_by(productList, 'view', 'descending')[:5]
    purchasesList = sort_by(productList, 'purchase', 'descending')[:5]

    purchasesName = []
    purchasesSerial = []
    purchasesAmount = []
    for product in purchasesList:
        purchasesName.append(product.get_product_name())
        purchasesSerial.append(product.get_serial_no())
        purchasesAmount.append(product.get_purchases())

    purchasesData = {
            'data':  [go.Bar(name='Purchases', x=purchasesAmount, y=purchasesSerial, text=purchasesName, textposition='auto', orientation='h', marker_color='#8FAFA2')],

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
            'data':  [go.Bar(name='Views', x=viewsAmount, y=purchasesSerial, text=viewsName, textposition='auto', orientation='h', marker_color='#E9BA6C')],

            'layout': {}
            }

    viewsGraph = json.dumps(viewsData, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('dashboard.html', currentPage='Dashboard', viewsList = viewsList, purchasesGraph = purchasesGraph, viewsGraph = viewsGraph, lowStockList=lowStockList, midStockList=midStockList)

@app.route('/productStats/<category>/<order>/')
def viewAll(category, order):
    productDict = {}
    db = shelve.open('storage.db', 'r')

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

    nameList = []
    purchasesList = []
    viewsList = []
    for product in productList:
        nameList.append(product.get_product_name())
        purchasesList.append(product.get_purchases())
        viewsList.append(product.get_views())


    graph = {}
    graph= {
            'data':  [go.Bar(name='Purchases', x=purchasesList, y=nameList, orientation='h', marker_color='#8FAFA2'),
                      go.Bar(name='Views', x=viewsList, y=nameList, orientation='h', marker_color='#E9BA6C')],

            'layout': {}
            }

    graphJSON = json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('productStats.html', productList=productList, graphJSON=graphJSON, currentPage='Statistics')

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
def adminSearch(searchCat, searchString):
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
            if searchString in product.get_sub_category().lower():
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

@app.route('/stock')
def stock():
    db = shelve.open('storage.db', 'c')

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

    return render_template('stock.html', currentPage='Stock', lowStockList=lowStockList, midStockList=midStockList, highStockList=highStockList)

@app.route('/transactions')
def transactions():
    transactionsDict = {}

    db = shelve.open('storage.db', 'c')

    try:
        productDict = db['Transactions']
        db.close()
    except:
        print('Error in retrieving Transactions from storage.db.')

    return render_template('transactions.html', currentPage='Transactions')


# Other stuff
@app.route('/categories')
def categories():
    return render_template('categories.html')

@app.route('/deliveryInvoice/<email>/',  methods=['POST'])
def deliveryInvoice(email):
    print("hey!")
    current_user = ""
    db = shelve.open('storage.db', 'r')
    try:
        current_user = db["Current User"]
    except:
        print('Error in retrieving current user from storage.db.')

    cart = current_user.get_shopping_cart()
    order_ID = current_user.get_orders()
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
        sender="191993Y@mymail.nyp.edu.sg",
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
        msg.html = render_template('html_in_invoice.html',  cartList=cartList, current_user=current_user ,order_ID= order_ID)
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

if __name__=='__main__':
    app.run(debug=True)
