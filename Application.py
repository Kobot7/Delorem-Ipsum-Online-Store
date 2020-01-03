# import os.path
import shelve
from flask import Flask, render_template, request, redirect, url_for
from Forms import *
from StorageClass import *
# from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='/static')
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
# UPLOAD_FOLDER= '/static/images'
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Homepage
@app.route('/')
def home():
    return render_template("home.html")

# Login/Register
@app.route('/login', methods=['GET', 'POST'])
def login():
    loginForm = LoginForm(request.form)
    registrationForm = RegistrationForm(request.form)
    if request.method =="POST" and loginForm.validate():
        if loginForm.username.data == "admin" and loginForm.password.data == "admin":
            return render_template('dashboard.html')
    return render_template('login.html', form=loginForm, form2=registrationForm)

# Supplements(one of the subsections)
@app.route('/supplements')
def supplements():
    return render_template('supplements.html')

# Ribena(one of the products)
@app.route('/ribena')
def ribena():
    return render_template('ribena.html')

# Wishlist
@app.route('/wishlist')
def wishlist():
    return render_template('wishlist.html')

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

@app.route('/products')
def products():
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
        product.set_quantity(editProductForm.quantity.data)
        product.set_activated(editProductForm.activated.data)

        db['Products'] = productDict
        db.close()
        return redirect(url_for('products'))

    else:
        productDict = {}
        db = shelve.open('storage.db', 'r')
        productDict = db['Products']
        db.close()

        product = productDict.get(serialNo)
        editProductForm.productName.data = product.get_product_name()
        editProductForm.brand.data = product.get_brand()
        # editProductForm.thumbnail.data = product.get_thumbnail()
        editProductForm.subCategory.data = product.get_sub_category()
        editProductForm.price.data = float(product.get_price())
        editProductForm.quantity.data = int(product.get_quantity())
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
                          createProductForm.serialNo.data, createProductForm.price.data, createProductForm.activated.data, createProductForm.quantity.data)
        productDict[product.get_serial_no()] = product
        db['Products'] = productDict

        db.close()

        return redirect(url_for('products'))

    return render_template('addProduct.html', form=createProductForm)


@app.route('/deleteProduct/<int:id>', methods=['POST'])
def deleteProduct(id):
    db = shelve.open('storage.db', 'w')
    productDict = db['Products']
    productDict.pop(id)
    db['Products'] = productDict
    db.close()
    return redirect(url_for('products'))


@app.route('/categories')
def categories():
    return render_template('categories.html')

if __name__=='__main__':
    app.run()
