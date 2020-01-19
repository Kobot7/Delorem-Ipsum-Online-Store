from wtforms import Form, StringField, SelectField, validators, BooleanField, PasswordField, FileField, DecimalField, IntegerField, TextAreaField, DateField, TimeField
import re

choicesList = [('', 'Select')
                , ('BabyAccessories', 'Baby - Accessories')
                , ('BabyVitamins', 'Baby - Baby Vitamins')
                , ('Diapers', 'Baby - Diapers')
                , ('MilkPowder&Food', 'Baby - Milk Powder & Food')
                , ('Toiletries', 'Baby - Toiletries')

                , ('CosmeticsAccessories', 'Cosmetics - Accessories')
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

                , ('SkinCareAccessories', 'Skin Care - Accessories')
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

    thumbnail = FileField('Image')

    productName = StringField('Product Name', [validators.DataRequired(message='This is a required field.')
                                            , validators.Length(min=1, max=100, message='Product name has to be less than 100 characters.')])

    brand = StringField('Brand', [validators.DataRequired(message='This is a required field.')
                               , validators.Length(min=1, max=50, message='Brand name is too long.')])

    subCategory = SelectField('Sub-Category', [validators.DataRequired(message='This is a required field.')], choices=choicesList, default='')

    price = DecimalField('Price', [validators.DataRequired(message='This is a required field.')
                                , validators.NumberRange(min=0, message='Value has to be more than 0')], places=2)

    description = TextAreaField('Description', [validators.DataRequired(message='This is a required field.')])

    quantity = IntegerField('Quantity', [validators.DataRequired(message='This is a required field.')
                                      , validators.NumberRange(min=0, message='Value has to be more than 0')])

    serialNo = StringField('Serial No.')

class CreateProductForm(Form):
    productName = StringField('Product Name', [validators.DataRequired(message='This is a required field.')
                                            , validators.Length(min=1, max=100, message='Product name has to be less than 100 characters.')])

    brand = StringField('Brand', [validators.DataRequired(message='This is a required field.')
                               , validators.Length(min=1, max=50, message='Brand name is too long.')])

    thumbnail = FileField('Image', [validators.DataRequired(message='This is a required field.')
                                 , validators.regexp('([^\s]+(\.(gif|jpg|tiff|png))$)', message='Please ensure file is in one of the following formats: jpg, png, gif, tiff')])

    subCategory = SelectField('Sub-Category', [validators.DataRequired(message='This is a required field.')], choices=choicesList, default='')

    price = DecimalField('Price', [validators.DataRequired(message='This is a required field.')
                                , validators.NumberRange(min=0, message='Value has to be more than 0')], places=2)

    description = TextAreaField('Description', [validators.DataRequired(message='This is a required field.')])

    quantity = IntegerField('Quantity', [validators.DataRequired(message='This is a required field.')])

    activated = BooleanField('')

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

class EditProfileForm(Form):
    image = FileField('Image')
    username = StringField('Username')
    address = TextAreaField('Address')
    phone = StringField('Contact Number')
    email = StringField('Contact Email')

class DeliveryForm(Form):
    Street_Name = StringField('Street Name',[validators.DataRequired()])
    Postal_Code = DecimalField('Postal Code', [validators.NumberRange(min=10000, max=830000, message="Postal code is 6 digits")])
    Unit_No = StringField('Unit No',[validators.Length(min=5,max=7),validators.DataRequired()])
    Date = DateField('Date', [validators.DataRequired()])
    Time = TimeField('Time',[validators.DataRequired()])
