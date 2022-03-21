STARTING_URL = 'https://scrapeme.live/shop/'
def pars(doc):
    page_ = doc.find_all(class_='page-numbers')
    no_of_page = int(page_[18].text.strip())
#no_of_page = 2
    return ({'url' : [{'url':f'https://scrapeme.live/shop/page/{page_no}/', 'call_back' : 'pars_products'} for page_no in range(1, no_of_page + 1)]})

def pars_products(doc):

    div = doc.find(class_='products columns-4').contents
    return({'url' : [{'url':item.find_all('a', href=True)[0].get('href'), 'call_back' : 'pars_product'} for item in div[1::2]]})

def pars_product(doc):
    title = doc.find(class_='product_title entry-title').text.strip()
    amount = doc.find(class_='price')
    amount = amount.find(class_='woocommerce-Price-amount amount').contents[1].text.strip()
    product_details = doc.find(class_='woocommerce-product-details__short-description').contents[1].text.strip()
    additional_information = doc.find(class_='shop_attributes')
    try:
        weight = additional_information.find(class_='product_weight').text.strip()
    except:
        weight = 'weight not available'
    try:
        dimensions = additional_information.find(class_='product_dimensions').text.strip()
    except:
        dimensions = 'dimensions not available'
    stock = doc.find(class_='stock in-stock').text.strip()
    return ({'data':[{'title' : title, 'amount' : amount, 'stock' : stock, 'product_details' : product_details, 'weight' : weight, 'dimensions' : dimensions}]})
