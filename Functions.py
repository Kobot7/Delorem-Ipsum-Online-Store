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
    #if order == "recent":
    #elif order =="expiring":
    #elif order =="discount":
    filtered_list=[]
    if filter =="hightolow":
        filtered_list = sorted(list, key=keyDict['price'], reverse=True)
    elif filter =="lowtohigh":
        filtered_list = sorted(list, key=keyDict['price'], reverse=False)
    elif filter =="a-z":
        filtered_list = sorted(list, key=keyDict['name'], reverse=False)
    elif filter =="z-a":
        filtered_list = sorted(list, key=keyDict['name'], reverse=True)
    #elif order =="stock":
    return filtered_list
