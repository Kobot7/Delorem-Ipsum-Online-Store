from wtforms import Form, StringField, SelectField, validators, BooleanField, PasswordField, FileField, DecimalField, IntegerField, TextAreaField

choicesList = [('', 'Select')
                , ('Accessories', 'Baby - Accessories')
                , ('BabyVitamins', 'Baby - Baby Vitamins')
                , ('Diapers', 'Baby - Diapers')
                , ('MilkPowder&Food', 'Baby - Milk Powder & Food')
                , ('Toiletries', 'Baby - Toiletries')

                , ('Accessories', 'Cosmetics - Accessories')
                , ('Eyes', 'Cosmetics - Eyes')
                , ('Face', 'Cosmetics - Face')
                , ('Lips', 'Cosmetics - Lips')
                , ('MakeupRemover', 'Cosmetics - Makeup Remover')
                , ('Nails', 'Cosmetics - Nails')

                , ('Conditioner', 'Hair Care - Conditioner')
                , ('HairDye', 'Hair Care - Hair Dye')
                , ('HairStyling', 'Hair Care - Hair Styling')
                , ('Shampoo', 'Hair Care - Shampoo')
                , ('Treatment', 'Hair Care - Treatment')

                , ('Eye&EarCare', 'Health - Eye & Ear Care')
                , ('FamilyPlanning', 'Health - Family Planning')
                , ('FirstAid&Surgical', 'Health - First Aid & Surgical')
                , ('Pain&Fever', 'Health - Pain & Fever')
                , ('Supplements', 'Health - Supplements')

                , ('Accessories', 'Skin Care - Accessories')
                , ('Anti-acne', 'Skin Care - Anti-acne')
                , ('Facial', 'Skin Care - Facial')
                , ('Hand&Body', 'Skin Care - Hand & Body')
                , ('LipCare', 'Skin Care - Lip Care')
                , ('SunCare', 'Skin Care - Sun Care')

                , ('Bath&HandCleansing', 'Toiletries - Bath & Hand Cleansing')
                , ('OralCare', 'Toiletries - Oral Care')
                , ('SanitaryCare', 'Toiletries - Sanitary Care')
                , ('Tissues&Wipes', 'Toiletries - Tissues & Wipes')]

class EditProductForm(Form):
    activated = BooleanField('')
    # thumbnail = FileField('Image', [validators.DataRequired()])
    thumbnail = FileField('Image', [validators.DataRequired(), validators.regexp('([^\s]+(\.(gif|jpg|tiff|png))$)', message='Please ensure file is in one of the following formats: jpg, png, gif, tiff')])
    productName = StringField('Product Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    brand = StringField('Brand', [validators.Length(min=1, max=150), validators.DataRequired()])
    subCategory = SelectField('Sub-Category', [validators.DataRequired()], choices=choicesList, default='')
    price = DecimalField('Price', [validators.DataRequired()], places=2)
    description = TextAreaField('Description', [validators.DataRequired()])
    serialNo = StringField('Serial No.', [validators.Length(min=1, max=10), validators.DataRequired()])
    quantity = IntegerField('Quantity', [validators.DataRequired()])

class CreateProductForm(Form):
    productName = StringField('Product Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    brand = StringField('Brand', [validators.Length(min=1, max=150), validators.DataRequired()])
    thumbnail = FileField('Image', [validators.DataRequired(), validators.regexp('([^\s]+(\.(gif|jpg|tiff|png))$)', message='Please ensure file is in one of the following formats: jpg, png, gif, tiff')])
    subCategory = SelectField('Sub-Category', [validators.DataRequired()], choices=choicesList, default='')
    price = DecimalField('Price', [validators.DataRequired()], places=2)
    description = TextAreaField('Description', [validators.DataRequired()])
    activated = BooleanField('')
    quantity = IntegerField('Quantity', [validators.DataRequired()])

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
