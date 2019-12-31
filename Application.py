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

@app.route('/productSettings', methods=['GET', 'POST'])
def productSettings():
    editProductForm = EditProductForm(request.form)
    return render_template('productSettings.html', form=editProductForm)

@app.route('/addProduct', methods=['GET', 'POST'])
def addProduct():
    createProductForm = CreateProductForm(request.form)
    if request.method == 'POST' and createProductForm.validate():
        productDict = {}
        db = shelve.open('storage.db', 'c')
        try:
            productDict = db['Products']
        except:
            print('Error in retrieving Products from storage.db.')

        # file = request.form['image']
        # # if user does not select file, browser also
        # # submit an empty part without filename
        # if file.filename == '':
        #     print("WHAT?")
        # filename = createProductForm.thumbnail.data
        # print("got data")
        # filename = secure_filename(filename)
        # print("made secure file name")
        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # print("saved into path")
        product = Product(createProductForm.productName.data, createProductForm.brand.data, createProductForm.thumbnail.data, createProductForm.subCategory.data,
                          createProductForm.price.data, createProductForm.activated.data, createProductForm.quantity.data)
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
