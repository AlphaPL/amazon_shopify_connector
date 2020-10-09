import mws, os
import os
import requests
import base64
import requests
from flask_apscheduler import APScheduler
from flask import jsonify
import pickle
import datetime
import amazon
import searchresults
# access key AKIAJWDGQRGP3ETCKTVA
# client secret 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
# seller id A3TUGG788NOEF7
cached_records = []
def get_products(region, marketplace):
  global cached_records
  print(region, marketplace)
  #fetch_report()
  try:
    orders_api = mws.Reports(
         access_key='AKIAI5SXHL3KQ5TMYPQQ',
         secret_key='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',
         account_id='A3TUGG788NOEF7',
         region='UK'
    )
    products_api = mws.Products(
         access_key='AKIAI5SXHL3KQ5TMYPQQ',
         secret_key='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',
         account_id='A3TUGG788NOEF7',
         region=region
    )
    for i in (orders_api.get_report_request_list(types=['_GET_MERCHANT_LISTINGS_ALL_DATA_']).parsed['ReportRequestInfo']):
      if(i['ReportType']['value'] == '_GET_MERCHANT_LISTINGS_ALL_DATA_'):
        report_id = i['GeneratedReportId']['value']
    report_lines = ((orders_api.get_report(report_id).parsed).decode().split('\n'))
    columns = {}
    for idx, column in enumerate(report_lines[0].strip().split('\t')):
      columns[idx] = column.strip().replace('\ufeff','')
    records = []
    for i in report_lines[1:]:
      record = {}
      if i:
        for idx, j in enumerate(i.split('\t')):
          record[columns[idx]] = j.strip().replace('\ufeff','')
        record['SmallImage'] = products_api.get_matching_product(marketplace, [record['asin1']]).parsed['Product']['AttributeSets']['ItemAttributes']['SmallImage']['URL']['value']
        record['handle'] =  ''.join(([c for c in record['item-name'].lower() if c.isalnum()])) 
        record['in-shopify'] = bool(get_prod_id(record))
        data = get_prod(record)
        if data and '|' in data['title']:
          record['restock-date'] = data['title'][data['title'].rfind(' ') + 1:]
        records += [record]
    cached_records = records
    afile = open('records', 'wb')
    pickle.dump(records, afile)
    afile.close()
    return records
  except mws.mws.MWSError as e:
    import traceback
    file2 = open('records', 'rb')
    new_d = pickle.load(file2)
    traceback.print_exc()
    return new_d

def get_mapping():
          #test code
    data = { }
    f = open("mappings.json", "r")
    mapping = {}
    for line in f.readlines():
      mapping[ line.split()[1]] = (line.split()[2], line.split()[3])
    return mapping

def fetch_report(): 
    print('Triggering report ', datetime.datetime.now())
    mapping = get_mapping()
    for r in mapping:
      try:
        print(r)
        print('Importing records from', r, mapping[r][1])
        for product in get_products(r, mapping[r][1]):
          product['description'] = amazon.scrape("https://www.amazon.com/"+ searchresults.scrape("https://www.amazon.com/s?k="+product['item-name'])['products'][0]['url'])
          print('Inserting product', product)
          create_product(product)
          orders_api = mws.Reports(
               access_key='AKIAI5SXHL3KQ5TMYPQQ',
               secret_key='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',
               account_id='A3TUGG788NOEF7',
               region='UK')
          orders_api.request_report('_GET_MERCHANT_LISTINGS_ALL_DATA_')
      except:
        pass




def get_prod_id(data):
      r = requests.get("https://11141a688940e4c4c90d53906ec7ec3a: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@clear-clavio-store.myshopify.com/admin/api/2020-07/products.json?handle="+data['handle'])
      for pro in r.json()['products']:
        return pro['id']
      return False



def get_prod(data):
      r = requests.get("https://11141a688940e4c4c90d53906ec7ec3a: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@clear-clavio-store.myshopify.com/admin/api/2020-07/products.json?handle="+data['handle'])
      for pro in r.json()['products']:
        return pro
      return False


def create_product(data):
      print("Importing product", data['item-name'])
      url = data['SmallImage']
      url = url[:url.rfind('.')]
      url = url[:url.rfind('.')]
      url = url+".jpg"
      payload =   {"product": {
        "title": data['item-name'] +" | Available " + data['restock-date'] if 'restock-date' in data and data['quantity'] == '' else data['item-name'],
        "handle": data['handle'],
        "body_html": data['description']['short_description'],
        "tags":data['restock-date']  if 'restock-date' in data else '',
        "variants": [
        {
          "price": data['price'],
          "sku": data['seller-sku'],
          "inventory_quantity": data['quantity'],
          "shop" : {
          "country":"GB"
          }
        }],
        "images": [
          {
            "attachment":  str(base64.b64encode(requests.get(url).content))[2:-1]
          }
        ]
      }}
      headers = {"Accept": "application/json", "Content-Type": "application/json"}
      if get_prod_id(data):
        print(data['item-name'], 'Exists! Updateing')
        r = requests.put("https://11141a688940e4c4c90d53906ec7ec3a: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@clear-clavio-store.myshopify.com/admin/api/2020-07/products/"+str(get_prod_id(data))+".json", json=payload, headers=headers)
      else:
        print(data['item-name'], 'Not Exists! Sending new')
        r = requests.post("https://11141a688940e4c4c90d53906ec7ec3a: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@clear-clavio-store.myshopify.com/admin/api/2020-07/products.json", json=payload, headers=headers)
        for i in range(5):
          r = requests.put("https://11141a688940e4c4c90d53906ec7ec3a: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@clear-clavio-store.myshopify.com/admin/api/2020-07/products/"+str(get_prod_id(data))+".json", json=payload, headers=headers)

#create_product()
