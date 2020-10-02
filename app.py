
# ./app.py

from flask import Flask, render_template, request, jsonify
import json
import amazon2shopify
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
  print(data)
  amazon2shopify.create_product(data)
  #pusher.trigger('todo', 'item-added', data) # trigger `item-added` event on `todo` channel
  return {}

@app.route('/items', methods = ['GET'])
def get_items():
  #pusher.trigger('todo', 'item-added', data) # trigger `item-added` event on `todo` channel
  return jsonify(amazon2shopify.get_products())

# endpoint for deleting todo item
@app.route('/remove-todo/<item_id>')
def removeTodo(item_id):
  data = {'id': item_id }
  #pusher.trigger('todo', 'item-removed', data)
  return jsonify(data)

# endpoint for updating todo item
@app.route('/update-todo/<item_id>', methods = ['POST'])
def updateTodo(item_id):
  data = {
    'id': item_id,
    'completed': json.loads(request.data).get('completed', 0)
  }
  #pusher.trigger('todo', 'item-updated', data)
  return jsonify(data)

# run Flask app in debug mode
app.run(use_reloader=False, host='0.0.0.0', port=3000)
