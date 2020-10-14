
# ./app.py

from flask import Flask, render_template, request, jsonify
import json
import amazon2shopify
import amazon
import searchresults
from flask import request
from flask_apscheduler import APScheduler
# create flask app
app = Flask(__name__)


# index route, shows index.html view
@app.route('/')
def index():
  return render_template('index.html')

# endpoint for storing todo item
@app.route('/add-todo', methods = ['POST'])
def addTodo():

  data = json.loads(request.data.decode()) # load JSON data from request
  data['description'] = amazon.scrape("https://www.amazon.com/"+ searchresults.scrape("https://www.amazon.com/s?k="+data['item-name'])['products'][0]['url'])
  print(data)
  amazon2shopify.create_product(data)
  #pusher.trigger('todo', 'item-added', data) # trigger `item-added` event on `todo` channel
  return {}

@app.route('/items', methods = ['GET'])
def get_items():
  region = request.args.get('country')
  pageNum = int(request.args.get('pageNum'))
  prodName = (request.args.get('prodname'))
  #pusher.trigger('todo', 'item-added', data) # trigger `item-added` event on `todo` channel
  result = []
  mapping = get_mapping()
  f = open("mappings.json", "r")
  mapping = {}
  for line in f.readlines():
    mapping[ line.split()[1]] = (line.split()[2], line.split()[3])
  for i in amazon2shopify.get_products(region, mapping[region][1], pageNum, prodName):
    result += [i]
  return jsonify(result)

# endpoint for deleting todo item
@app.route('/remove-todo/<item_id>')
def removeTodo(item_id):
  data = {'id': item_id }
  #pusher.trigger('todo', 'item-removed', data)
  return jsonify(data)

@app.route('/get_mapping')
def get_mapping():
  data = { }
  f = open("mappings.json", "r")
  mapping = {}
  for line in f.readlines():
    mapping[ line.split()[1]] = (line.split()[2], line.split()[3])
  #pusher.trigger('todo', 'item-removed', data)
  return jsonify(mapping)

# endpoint for updating todo item
@app.route('/update-todo/<item_id>', methods = ['POST'])
def updateTodo(item_id):
  data = {
    'id': item_id,
    'completed': json.loads(request.data).get('completed', 0)
  }
  #pusher.trigger('todo', 'item-updated', data)
  return jsonify(data)

if __name__ == "__main__":
  scheduler = APScheduler()
  scheduler.add_job(func=amazon2shopify.fetch_report, args=[], trigger='interval', id='job', minutes=15)
  #amazon2shopify.fetch_report()
  scheduler.start()
  app.run(use_reloader=True, host='0.0.0.0', port=3000)
