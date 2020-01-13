# import os.path
import shelve, string, random
import re
from flask import Flask, render_template, request, redirect, url_for
from Forms import *
from StorageClass import *
from Functions import *
from User import *

app = Flask(__name__, static_url_path='/static')

# Homepage
@app.route('/home')
def home():
    return render_template("home.html")

# Login/Register
@app.route('/login', methods=['GET', 'POST'])
def login():
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
        exist = namesDict.get(loginForm.username.data, "Nothing")
        if exist!= "Nothing":
            current_user = usersDict[exist]
            db["Current User"] = current_user
            db.close()
            password = current_user.get_password()
            if loginForm.password.data == password:
                return redirect(url_for('home'))

        if loginForm.username.data == "admin" and loginForm.password.data == "admin":
            return render_template('dashboard.html')

    return render_template('login.html', form=loginForm, form2=registrationForm)

# Supplements(one of the subsections)
@app.route('/subCategory/<subCategory>/')
def supplements(subCategory):
    db = shelve.open('storage.db', 'r')
    try:
        Products = db["Products"]
    except:
        print("Error in retrieving products from shelve")
    products = []
    for id in Products:
        product = Products[id]
        if product.get_sub_category() == subCategory:
            if product.get_activated() == True:
                products.append(product)

    mainCategory = get_main_category(subCategory)

    return render_template('supplements.html', productList=products, subCategory=subCategory, modalCount=len(products), mainCategory=mainCategory)

# Ribena(one of the products)
@app.route('/IndItem/<serialNo>')
def IndItem(serialNo):
    db = shelve.open('storage.db','r')
    try:
        products = db['Products']
    except:
        print("Error while retrieving products from storage.")
    IndItem = products[serialNo]
    subCategory = IndItem.get_sub_category()
    mainCategory = get_main_category(subCategory)
    return render_template('IndItem.html', product=IndItem, mainCategory=mainCategory)

# Wishlist
@app.route('/wishlist/<filter>/')
def wishlist(filter):
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

    return render_template('wishlist.html', filtered_list=filtered_list)

    @app.route('/deleteWishListItem/<serialNo>', methods=['POST'])
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

@app.route('/moveToCart/<serialNo>', methods=['POST'])
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

# Shopping Cart
@app.route('/cart')
def cart():
    return render_template('cart.html')

# Checkout
@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

# Admin Side
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/products/<category>/<order>/')
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

    return render_template('products.html', productList=productList)

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
        product.set_thumbnail(editProductForm.thumbnail.data)
        product.set_sub_category(editProductForm.subCategory.data)
        product.set_price(editProductForm.price.data)
        product.set_description(editProductForm.description.data)
        product.set_quantity(editProductForm.quantity.data)
        product.set_activated(editProductForm.activated.data)

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
        editProductForm.thumbnail.data = product.get_thumbnail()
        editProductForm.subCategory.data = product.get_sub_category()
        editProductForm.price.data = float(product.get_price())
        editProductForm.quantity.data = int(product.get_quantity())
        editProductForm.description.data = product.get_description()
        editProductForm.activated.data = product.get_activated()
        editProductForm.serialNo.data = product.get_serial_no()

    return render_template('productSettings.html', form=editProductForm)

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

        product = Product(createProductForm.productName.data, createProductForm.brand.data, createProductForm.thumbnail.data, createProductForm.subCategory.data,
                          createProductForm.price.data, createProductForm.description.data, createProductForm.activated.data, createProductForm.quantity.data)

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

    return render_template('addProduct.html', form=createProductForm)

@app.route('/categories')
def categories():
    return render_template('categories.html')

if __name__=='__main__':
    app.run(debug=True)
