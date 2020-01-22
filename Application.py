import shelve, string, random
from flask import Flask, render_template, request, redirect, url_for
from Forms import *
from StorageClass import *
from Functions import *
from User import *
from werkzeug.utils import secure_filename
import os
from pathlib import Path

app = Flask(__name__, static_url_path='/static')

def searchBar():
    return SearchBar(request.form)

def testing():
    productDict = {}
    db = shelve.open('storage.db', 'w')
    productDict = db['Products']
    del productDict['952571Z']

    # test = productDict['709283M']
    # test.increase_purchases(0)
    # for x in range(10):
    #     test.increase_views()
    db['Products'] = productDict
    db.close()

# Homepage
@app.route('/home', methods=['GET', 'POST'])
def home():
    db = shelve.open('storage.db', 'c')
    try:
        current = db["Current User"].get_username()
    except:
        print("Error while retrieving current user")
        current = False
    db.close()

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        print(searchForm.search_input.data)

    return render_template("home.html", current=current, searchForm=searchForm)

# Profile/Username
@app.route('/my-account/<current>', methods=['GET', 'POST'])
def view_profile(current):
    db = shelve.open("storage.db", "c")
    try:
        usersDict = db["Users"]
        current = db["Current User"]
    except:
        usersDict = {}
        db["Users"] = usersDict
        print("Error while retrieving usersDict")
    editProfileForm = EditProfileForm(request.form)
    if request.method == "POST":
        current_id = current.get_user_id()
        # current.set_profile_pic(editProfileForm.image.data)
        current.set_username(editProfileForm.username.data)
        current.set_address(editProfileForm.address.data)
        current.set_phone(editProfileForm.phone.data)
        current.set_email(editProfileForm.email.data)
        usersDict[current_id] = current
        db["Users"] = usersDict
        db["Current User"] = current
        db.close()
        # return render_template('my-account.html', pic=current.get_profile_pic(), name=current.get_username(), address=current.get_address(), phone=current.get_phone(), email=current.get_email())
        return render_template('my-account.html', name=current.get_username(), address=current.get_address(), phone=current.get_phone(), email=current.get_email())
    else:
        db.close()
        return render_template('my-account.html', name=current.get_username(), address=current.get_address(), phone=current.get_phone(), email=current.get_email())
        # return render_template("my-account.html", pic=current.get_profile_pic(), name=current.get_username(), address=current.get_address(), phone=current.get_phone(), email=current.get_email())


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
            return redirect('/dashboard')

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        print(searchForm.search_input.data)
    return render_template('login.html', form=loginForm, form2=registrationForm, searchForm=searchForm)

@app.route('/logout')
# @login_required
def logout():
    db = shelve.open("storage.db", "c")
    db["Current User"] = ""
    print("User logged out successfully")
    return redirect(url_for('home'))
    # return render_template("home.html", current="", logged_out=True)

# Supplements(one of the subsections)
@app.route('/subCategory/<subCategory>/', methods=['GET', 'POST'])
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

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        print(searchForm.search_input.data)
    return render_template('supplements.html', productList=products, subCategory=subCategory, modalCount=len(products), mainCategory=mainCategory, searchForm=searchForm)


# Ribena(one of the products)
@app.route('/IndItem/<serialNo>', methods=['GET', 'POST'])
def IndItem(serialNo):
    db = shelve.open('storage.db','w')
    try:
        products = db['Products']
    except:
        print("Error while retrieving products from storage.")
    IndItem = products[serialNo]
    IndItem.increase_views()
    db['Products'] = products
    db.close()
    subCategory = IndItem.get_sub_category()
    mainCategory = get_main_category(subCategory)

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        print(searchForm.search_input.data)
    return render_template('IndItem.html', product=IndItem, mainCategory=mainCategory, searchForm=searchForm)


# Shopping Cart
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    db = shelve.open('storage.db','r')
    try:
        user = db['Current User']
    except:
        print('Error reading Current User.')

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
        print(searchForm.search_input.data)
    return render_template('cart.html', cartList=cartList, totalCost=totalCost, searchForm=searchForm)

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
    cartList = []
    totalCost = 0
    for product in cart:
        totalCost += float(cart[product].get_price())
        cartList.append(cart[product])
    totalCost ='%.2f' %float(totalCost)

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        print(searchForm.search_input.data)
    return render_template('cart.html', cartList=cartList, totalCost=totalCost, searchForm=searchForm)

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
        print(searchForm.search_input.data)
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
        print(searchForm.search_input.data)
    return render_template('wishlist.html', filtered_list=filtered_list, searchForm=searchForm)

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
    deliveryForm = DeliveryForm(request.form)
    db = shelve.open('storage.db', 'r')
    try:
        current_user = db["Current User"]
    except:
        print("Error in retrieving current user for checkout")

    searchForm = searchBar()
    if request.method == "POST" and searchForm.validate():
        print(searchForm.search_input.data)
    return render_template('checkout.html', form=deliveryForm, searchForm=searchForm)


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
    for key in productDict:
        product = productDict.get(key)
        productList.append(product)
        viewList = sort_by(productList, 'view', 'descending')[:5]
        purchaseList = sort_by(productList, 'purchase', 'descending')[:5]

    return render_template('dashboard.html', viewList = viewList, purchaseList = purchaseList)

@app.route('/dashboard/productStats/<category>/<order>/')
def viewAll(category, order):
    productDict = {}
    db = shelve.open('storage.db', 'w')

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

    return render_template('productStats.html', productList=productList)

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

    AdminSearch(request.form)
    adminSearchForm = AdminSearch(request.form)

    return render_template('products.html', adminSearchForm = adminSearchForm, productList=productList)

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
        editProductForm.description.data = product.get_description()
        editProductForm.activated.data = product.get_activated()
        editProductForm.serialNo.data = product.get_serial_no()

    return render_template('productSettings.html', form=editProductForm, label=product.get_thumbnail())

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

        product = Product(createProductForm.productName.data, createProductForm.brand.data, image.filename, createProductForm.subCategory.data,
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

@app.route('/details')
def details():
    deliveryForm = DeliveryForm(request.form)

    return render_template('details.html', form=deliveryForm)


if __name__=='__main__':
    app.run(debug=True)
