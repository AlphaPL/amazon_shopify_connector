import mws, os
import os
import requests
# access key AKIAJWDGQRGP3ETCKTVA
# client secret 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
# seller id A3TUGG788NOEF7
cached_records = []
def get_products():
  global cached_records
  try:
    orders_api = mws.Reports(
         access_key='AKIAJWDGQRGP3ETCKTVA',
         secret_key='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',
         account_id='A3TUGG788NOEF7',
         region='UK'
    )
    region2market = {}
    region2market['UK'] = 'A1F83G8C2ARO7P'
    products_api = mws.Products(
         access_key='AKIAJWDGQRGP3ETCKTVA',
         secret_key='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',
         account_id='A3TUGG788NOEF7',
         region='UK'
    )
    print(orders_api.get_service_status().original)
    for i in (orders_api.get_report_request_list().parsed['ReportRequestInfo']):
      if(i['ReportType']['value'] == '_GET_MERCHANT_LISTINGS_DATA_BACK_COMPAT_'):
        report_id = i['GeneratedReportId']['value']
    print(report_id)
    report_lines = ((orders_api.get_report(report_id).parsed).decode().split('\n'))
    columns = {}
    for idx, column in enumerate(report_lines[0].strip().split('\t')):
      columns[idx] = column
    records = []
    for i in report_lines[1:]:
      record = {}
      if i:
        for idx, j in enumerate(i.split('\t')):
          record[columns[idx]] = j
        record['SmallImage'] = products_api.get_matching_product(region2market['UK'], [record['asin1']]).parsed['Product']['AttributeSets']['ItemAttributes']['SmallImage']['URL']['value']
        records += [record]
    cached_records = records
    return records
  except Exception as e:
    print(e)
    import traceback
    traceback.print_exc()
    return cached_records




def create_product(data):
      print('Adding product', data)
      payload =   {"product": {
        "title": data['item-name'],
        "variants": [
        {
          "price": data['price'],
          "sku": data['seller-sku']
        }],
        "images": [
          {
            "id": 850703190,
            "product_id": 632910392,
            "position": 1,
            "created_at": "2018-01-08T12:34:47-05:00",
            "updated_at": "2018-01-08T12:34:47-05:00",
            "width": 110,
            "height": 140,
            "src": data['SmallImage'],
            "variant_ids": [
              {}
            ]
          }
        ]
      }}
      print('Sending payload', payload)
      headers = {"Accept": "application/json", "Content-Type": "application/json"}

      r = requests.post("https://11141a688940e4c4c90d53906ec7ec3a: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@clear-clavio-store.myshopify.com/admin/api/2020-07/products.json", json=payload, headers=headers)

      print(r)

#create_product()
