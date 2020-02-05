from wtforms import Form, StringField, SelectField, validators, BooleanField, PasswordField, FileField, DecimalField, IntegerField, TextAreaField, RadioField
from wtforms.fields.html5 import DateField
from wtforms_components import TimeField, DateRange
from datetime import datetime,date
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

    productName = StringField('Product Name', [validators.DataRequired(message='This is a required field.')
                                            , validators.Length(min=1, max=100, message='Product name has to be less than 100 characters.')])

    brand = StringField('Brand', [validators.DataRequired(message='This is a required field.')
                               , validators.Length(min=1, max=50, message='Brand name is too long.')])

    subCategory = SelectField('Sub-Category', [validators.DataRequired(message='This is a required field.')], choices=choicesList, default='')

    price = DecimalField('Price', [validators.DataRequired(message='This is a required field.')
                                , validators.NumberRange(min=0, message='Value has to be more than 0')], places=2)

    description = TextAreaField('Description', [validators.DataRequired(message='This is a required field.')])

    quantity = IntegerField('In-Stock', [validators.DataRequired(message='This is a required field.')
                                      , validators.NumberRange(min=0, message='Value has to be more than 0')])

    stockThreshold = IntegerField('Alert if stock falls below', [validators.DataRequired(message='This is a required field.')
                                      , validators.NumberRange(min=0, message='Value has to be more than 0')])

    serialNo = StringField('Serial No.')

class CreateProductForm(Form):
    productName = StringField('Product Name', [validators.DataRequired(message='This is a required field.')
                                            , validators.Length(min=1, max=100, message='Product name has to be less than 100 characters.')])

    brand = StringField('Brand', [validators.DataRequired(message='This is a required field.')
                               , validators.Length(min=1, max=50, message='Brand name is too long.')])

    subCategory = SelectField('Sub-Category', [validators.DataRequired(message='This is a required field.')], choices=choicesList, default='')

    price = DecimalField('Price', [validators.DataRequired(message='This is a required field.')
                                , validators.NumberRange(min=0, message='Value has to be more than 0')], places=2)

    description = TextAreaField('Description', [validators.DataRequired(message='This is a required field.')])

    quantity = IntegerField('In-Stock', [validators.DataRequired(message='This is a required field.')])

    stockThreshold = IntegerField('Alert if stock falls below', [validators.DataRequired(message='This is a required field.')
                                      , validators.NumberRange(min=0, message='Value has to be more than 0')])

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
    username = StringField('Username', [validators.Length(min=1, max=25), validators.DataRequired()])
    address = TextAreaField('Address')
    phone = IntegerField('Contact Number',[validators.NumberRange(min=80000000, max=99999999, message="Please enter a valid phone number")])
    email = StringField('Contact Email', [validators.Length(min=6, max=35)])
    password = StringField("Password")
    newpassword = StringField('New Password')

class NoCollectForm(Form):
    home_delivery = BooleanField("Home Delivery")


cardlist = [('visa','Visa'),
            ('mastercard', 'MasterCard')]

class DeliveryForm(Form):
    name = StringField('Cardholder Name',[validators.DataRequired()])
    phone = IntegerField('Phone Number',[validators.NumberRange(min=30000000, max=99999999, message="Please enter a valid phone number")])
    payment_mode = RadioField('Payment Mode',choices=cardlist, default='')
    credit_card_number = IntegerField('Credit Card Number', [validators.NumberRange(min=3000000000000, max=9999999999999999,message="Please enter a valid Credit Card Number")])
    credit_card_expiry = DateField('Credit Card Expiry Date', validators=[DateRange(min=date.today(), format='%Y-%m-%d', message="Please choose a valid date")])
    credit_card_cvv = IntegerField('CVV', [validators.NumberRange(min=100, max = 999, message="Please enter a valid CVV")])
    street_name = StringField('Street Name',[validators.DataRequired()])
    postal_code = DecimalField('Postal Code', [validators.NumberRange(min=10000, max=830000, message="Postal code is 6 digits")])
    unit_no = StringField('Unit No',[validators.Length(min=5,max=7,message="Please enter a valid unit number"),validators.DataRequired()])

class CollectionForm(Form):
    name = StringField('Cardholder Name',[validators.DataRequired()])
    phone = IntegerField('Phone Number',[validators.DataRequired(), validators.NumberRange(min=30000000, max=99999999, message="Please enter a valid phone number")])
    payment_mode = RadioField('Payment Mode',choices=cardlist, default='')
    credit_card_number = IntegerField('Credit Card Number', [validators.DataRequired(), validators.NumberRange(min=3000000000000, max=9999999999999999,message="Please enter a valid Credit Card Number")])
    credit_card_expiry = DateField('Credit Card Expiry Date', format = "%Y-%m-%d")
    credit_card_cvv = IntegerField('CVV', [validators.DataRequired(), validators.NumberRange(min=100, max = 999)])
    date = DateField('Date',[validators.DataRequired()])
    time = IntegerField('Postal Code', [validators.NumberRange(min=10000, max=830000, message="Postal code is 6 digits")])


class SearchBar(Form):
    search_input = StringField('')


admin_searchList = [('name-brand', 'Name/Brand')
                , ('sub-category', 'Sub-Category')
                , ('serial-no', 'Serial No.')]

class AdminSearch(Form):
    search_cat = SelectField('', choices=admin_searchList, default='name')
    search_input = StringField('', [validators.DataRequired()])

class DiscountForm(Form):
    discount_code = StringField('Discount code')

class AddDiscountForm(Form):
    discount_code = StringField('Discount code')
    discount_condition =  DecimalField('Price at which disount is applicable', [validators.DataRequired(message='This is a required field.')
                                , validators.NumberRange(min=0, message='Value has to be more than 0')], places=2)
    # discount_expiry = DateField('Expiry Date', format = "%Y-%m-%d")
    discount_start  = DateField('Date start', format = "%Y-%m-%d")
    discount_expiry  = DateField('Date expiry', format = "%Y-%m-%d")
    discount_amount = DecimalField('Discount Amount', [validators.DataRequired(message='This is a required field.')
                                , validators.NumberRange(min=0, message='Value has to be more than 0')], places=2)
    discount_percentage = DecimalField('Discount percentage', [validators.DataRequired(message='This is a required field.')
                                , validators.NumberRange(min=0, message='Value has to be more than 0')], places=2)
