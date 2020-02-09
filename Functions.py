import re
from Discount import *

def sort_by(list, category, order):
    if order=='ascending':
        order = False
    else:
        order = True

    list = sorted(list, key=keyDict[category], reverse=order)
    return list

def name_key(item):
    return item.get_product_name()

def brand_key(item):
    return item.get_brand()

def sub_category_key(item):
    return item.get_sub_category()

def serial_no_key(item):
    return item.get_serial_no()

def price_key(item):
    return float(item.get_price())

def activated_key(item):
    return item.get_activated()

def quantity_key(item):
    return item.get_quantity()

def view_key(item):
    return item.get_views()

def purchase_key(item):
    return item.get_purchases()

def threshold_key(item):
    return item.get_stock_threshold()

keyDict = {}
keyDict['name'] = name_key
keyDict['brand'] = brand_key
keyDict['sub-category'] = sub_category_key
keyDict['serial-no'] = serial_no_key
keyDict['price'] = price_key
keyDict['activated'] = activated_key
keyDict['quantity'] = quantity_key
keyDict['view'] = view_key
keyDict['purchase'] = purchase_key
keyDict['threshold'] = threshold_key

def get_main_category(subCategory):
    if subCategory in ['Pain&Fever','FamilyPlanning','FirstAid&Surgical','Eye&EarCare','Supplements']:
        mainCategory = 'Health'

    elif subCategory in ['Shampoo','Conditioner','Treatment','HairDye','HairStyling']:
        mainCategory = 'Hair Care'

    elif subCategory in ['Bath&HandCleansing','OralCare','SanitaryCare','Tissues&Wipes']:
        mainCategory = 'Toiletries'

    elif subCategory in ['SkinCareAccessories','Anti-acne','Facial','Hand&Body','LipCare', 'SunCare']:
        mainCategory = 'Skin Care'

    elif subCategory in ['Toiletries','Diapers','MilkPowder&Food','BabyVitamins','Accessories']:
        mainCategory = 'Baby'

    else:
        mainCategory = 'Cosmetics'

    return mainCategory


# For wish list
def filter_function(list, filter):
    filtered_list=[]
    if filter =="hightolow":
        filtered_list = sorted(list, key=keyDict['price'], reverse=True)
    elif filter =="lowtohigh":
        filtered_list = sorted(list, key=keyDict['price'], reverse=False)
    elif filter =="a-z":
        filtered_list = sorted(list, key=keyDict['name'], reverse=False)
    elif filter =="z-a":
        filtered_list = sorted(list, key=keyDict['name'], reverse=True)
    return filtered_list

def get_name_with_space(name):
    name = name.replace('&', ' & ')
    return re.sub(r"(\w)([A-Z])", r"\1 \2", name)

#for discounts
def filter_discount(list, category, order):
    if  order == "ascending" or order =="descending":
        if order=='ascending':
            order = False
        elif order=="descending":
            order = True
        list = sorted(list, key=keyDict[category], reverse=order)
        return list
    else:
        filtered_list=[]
        if category == "type" and order == "amount":
            for disount in list:
                if type_key(discount) =="Amount":
                    filtered_list.append(discount)
        elif category == "type" and order =="percentage":
            for discount in list:
                if type_key(discount) == "Percentage":
                    filtered_list.append(discount)
        elif category == "status" and  order == "active":
            for discount in list:
                if status_key(discount) == "active":
                    filtered_list.append(discount)
        elif category == "status" and  order == "inactive":
            for discount in list:
                if status_key(discount) == "inactive":
                    filtered_list.append(discount)
        elif category == "status" and  order == "expired":
            for discount in list:
                if status_key(discount) == "expired":
                    filtered_list.append(discount)
        elif category == "status" and  order == "deleted":
            for discount in list:
                if status_key(discount) == "deleted":
                    filtered_list.append(discount)
        return filtered_list


def code_key(discount):
    return discount.get_code()

def type_key(discount):
    if isinstance(discount, AmountDiscount):
        return "Amount"
    else:
        return "Percentage"

def condition_key(discount):
    return discount.get_condition()

def start_key(disount):
    return discount.get_start_date()

def end_key(disount):
    return discount.get_expiry_date()

def discount_key(discount):
    if isinstance(discount, AmountDiscount):
        return discount.get_discount_amount()
    else:
        return discount.get_discount_percentage()

def used_key(discount):
    return discount.get_used()

def status_key(discount):
    return discount.get_status()

discountKey = {}
discountKey['code'] = code_key
discountKey['type'] = type_key
discountKey['condition'] = condition_key
discountKey['start'] = start_key
discountKey['end'] = end_key
discountKey['discount'] = discount_key
discountKey['used'] = used_key
discountKey['status'] = status_key
