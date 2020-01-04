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
    return item.get_price()

def activated_key(item):
    return item.get_activated()

def quantity_key(item):
    return item.get_quantity()

keyDict = {}
keyDict['name'] = name_key
keyDict['brand'] = brand_key
keyDict['sub-category'] = sub_category_key
keyDict['serial-no'] = serial_no_key
keyDict['price'] = price_key
keyDict['activated'] = activated_key
keyDict['quantity'] = quantity_key
