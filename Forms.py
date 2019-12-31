from wtforms import Form, StringField, SelectField, validators, BooleanField, PasswordField, FileField, DecimalField, IntegerField

choicesList = [('', 'Select'), ('Bodycare', 'Bodycare'), ('Lotion', 'Lotion'), ('Over the Counter', 'Over the Counter'), ('Supplements', 'Supplements'), ('Toner', 'Toner'), ('Vitamins', 'Vitamins')]

class EditProductForm(Form):
    activated = BooleanField('')
    thumbnail = FileField('Thumbnail')
    productName = StringField('Product Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    brand = StringField('Brand', [validators.Length(min=1, max=150), validators.DataRequired()])
    subCategory = SelectField('Sub-Category', [validators.DataRequired()], choices=choicesList, default='')
    serialNo = StringField('Serial No.', [validators.Length(min=1, max=10), validators.DataRequired()])
    price = DecimalField('Price', places=2)
    quantity = IntegerField('Quantity')

class CreateProductForm(Form):
    productName = StringField('Product Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    brand = StringField('Brand', [validators.Length(min=1, max=150), validators.DataRequired()])
    thumbnail = FileField('Image', [validators.DataRequired()])
    subCategory = SelectField('Sub-Category', [validators.DataRequired()], choices=choicesList, default='')
    price = StringField('Price', [validators.Length(min=1, max=6), validators.DataRequired()])
    activated = BooleanField('')
    quantity = IntegerField('Quantity')

class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=1, max=25), validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

class RegistrationForm(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
