import asyncio, websockets, json, random, yaml, datetime
import config as cfg
import database as db

def authentication(exchange):
	"""Websocket authentication from API to send private responses

	https://docs.deribit.com/#public-auth

	Returns:
		websockets object: authenticated websocket
	"""
	cfg.msg_id += 1
	msg = \
		{
			"jsonrpc": "2.0",
			"id": cfg.msg_id,
			"method": "public/auth",
			"params": {
				"grant_type": "client_credentials",
				# "client_id": cfg.client_id,
				# "client_secret": cfg.client_secret
				"client_id": exchange['client_id'],
				"client_secret": exchange['client_secret']
			}
		}

	async def auth(msg):
		# websocket = await websockets.connect(cfg.uri)
		websocket = await websockets.connect(exchange['uri'])
		await websocket.send(msg)
		await websocket.recv()
		return websocket

	ws = asyncio.get_event_loop().run_until_complete(auth(json.dumps(msg)))

	return ws

def get_current_price(websocket,instrument):
	"""Get current (mark price) for an instrument

	https://docs.deribit.com/?python#public-ticker

	Args:
		websocket (websockets object): authenticated websocket
		instrumet (string): instrument name

	Returns:
		number: the mark price for the instrument
	"""
	cfg.msg_id += 1
	msg = \
		{
			"jsonrpc": "2.0",
			"id": cfg.msg_id,
			"method": "public/ticker",
			"params": {
				"instrument_name": instrument
			}
		}

	async def ticker(websocket, msg):
		await websocket.send(msg)
		response = await websocket.recv()
		try:
			print("ticker mark_price: {}".format(json.loads(response)['result']['mark_price']))
			return json.loads(response)['result']['mark_price']
		except Exception as e:
			print("ticker mark_price error: {}".format(e))
			return 0

	return asyncio.get_event_loop().run_until_complete(ticker(websocket, json.dumps(msg)))

def set_order(websocket,status,price,amount,instrument):
	"""Places a buy or sell limit order for an instrument

	https://docs.deribit.com/#private-buy
	https://docs.deribit.com/#private-sell

	Args:
		websocket (websockets object): authenticated websocket
		status (string): 'buy' or 'sell' order
		price (number): price for limit order
		amount (number): for perpetual amount is in USD units 
		instrument (string): instrument 

	Returns:
		number: order id
	"""
	cfg.msg_id += 1
	msg = \
		{
			"jsonrpc": "2.0",
			"id": cfg.msg_id,
			"method": "private/" + status,
			"params": {
				"instrument_name": instrument,
				"amount": amount,
				"type": "limit",
				"price": price
			}
		}

	print("{} {} {} on {}".format(status,amount,instrument,price))
	# order_id = 0

	async def order(websocket, msg):
		await websocket.send(msg)
		response = await websocket.recv()
		try:
			return json.loads(response)['result']['order']['order_id']
		except Exception as e:
			print("set_order error: {}".format(e))
			return 0

	order_id = asyncio.get_event_loop().run_until_complete(order(websocket, json.dumps(msg)))

	return order_id

def check_order(websocket,order_id):
	"""Retrieve the current state of an order specified by order id

	https://docs.deribit.com/#private-get_order_state

	Args:
		websocket (websockets object): authenticated websocket
		order_id (number): order id

	Returns:
		boolian: True if order was closed and False if not
	"""
	cfg.msg_id += 1
	msg = \
		{
			"jsonrpc": "2.0",
			"id": cfg.msg_id,
			"method": "private/get_order_state",
			"params": {
				"order_id": order_id
			}
		}

	async def check(websocket, msg):
		await websocket.send(msg)
		response = await websocket.recv()
		try:
			return json.loads(response)['result']['order_state'] != 'open'
		except Exception as e:
			print("check_order error: {}".format(e))
			return False

	order_status = asyncio.get_event_loop().run_until_complete(check(websocket, json.dumps(msg)))    
	
	print("Checking order {}".format(order_id))
	# order_status = random.choice([True, False])
	print("Order status {}".format(order_status))
	
	return order_status

def cancel_order(websocket,order_id):
	"""Cancel an order specified by order id

	https://docs.deribit.com/#private-cancel

	Args:
		websocket (websockets object): authenticated websocket
		order_id (number): order id
	"""

	cfg.msg_id += 1
	msg = \
		{
			"jsonrpc": "2.0",
			"id": cfg.msg_id,
			"method": "private/cancel",
			"params": {
				"order_id": order_id
			}
		}

	print("Cancelling order {}".format(order_id))

	async def cancel(websocket, msg):
		await websocket.send(msg)
		await websocket.recv()
		return

	asyncio.get_event_loop().run_until_complete(cancel(websocket, json.dumps(msg)))
	
	

def read_config(filename):
	"""Read .yaml config file

	robot:
		gap: 0
		gap_ignore: 0
		amount: 0
	exchange:
  		client_id: ''
  		client_secret: ''
  		uri: ''
  		instrument: ''	
	
	Args:
		filename (string): configuration file name

	Returns:
		dict: dict with parameters
	"""
	with open(filename) as file:
		try:
			confs = yaml.safe_load(file)
			return confs
		except yaml.YAMLError as e:
			print("Read config file error: {}".format(e))

def run(websocket,config):
	"""Main algo function

	Args:
		websocket (websockets object): authenticated websocket
		config (dict): configuration data from yaml file
	"""
	gap = config['robot']['gap']
	gap_ignore = config['robot']['gap_ignore']
	amount = config['robot']['amount']
	
	instrument = config['exchange']['instrument']
	
	current_price = get_current_price(websocket,instrument)
	buy_price = current_price - gap / 2
	sell_price = current_price + gap

	print("buy_price {}, sell_price {}".format(buy_price,sell_price))
	status = 'buy'
	order_id = set_order(websocket,status,buy_price,amount,instrument)
	db.add_order_to_db(datetime.datetime.utcnow(),order_id,status,amount,buy_price)

	while True:
		current_price = get_current_price(websocket,instrument)
		if status == 'buy' and current_price > 0:
			if check_order(websocket,order_id):
				db.update_order(order_id)
				status = 'sell'
				sell_price = current_price + gap
				print("buy_price {}, sell_price {}".format(buy_price,sell_price))
				order_id = set_order(websocket,status,sell_price,amount,instrument)
				db.add_order_to_db(datetime.datetime.utcnow(),order_id,status,amount,sell_price)
			
			elif current_price > buy_price + gap + gap_ignore:
				cancel_order(websocket,order_id)
				buy_price = current_price - gap/2
				print("buy_price {}, sell_price {}".format(buy_price,sell_price))
				order_id = set_order(websocket,status,buy_price,amount,instrument)
				db.add_order_to_db(datetime.datetime.utcnow(),order_id,status,amount,buy_price)
		
		elif status == 'sell' and current_price > 0:
			if check_order(websocket,order_id):
				db.update_order(order_id)
				status = 'buy'
				buy_price = current_price - gap/2
				print("buy_price {}, sell_price {}".format(buy_price,sell_price))
				order_id = set_order(websocket,status,buy_price,amount,instrument)
				db.add_order_to_db(datetime.datetime.utcnow(),order_id,status,amount,buy_price)

			elif current_price < sell_price - gap - gap_ignore:
				cancel_order(websocket,order_id)
				sell_price = current_price + gap
				print("buy_price {}, sell_price {}".format(buy_price,sell_price))
				order_id = set_order(websocket,status,sell_price,amount,instrument)
				db.add_order_to_db(datetime.datetime.utcnow(),order_id,status,amount,sell_price)

		else:
			print("Order status error")
			status = 'buy'	

def cancel_all_orders(websocket):
	"""Cancel all order

	Args:
		websocket (websockets object): authenticated websocket
	"""
	cfg.msg_id += 1
	msg = \
		{
			"jsonrpc": "2.0",
			"id": cfg.msg_id,
			"method": "private/cancel_all",
			"params": {}
		}

	async def cancel_all(websocket, msg):
		await websocket.send(msg)
		await websocket.recv()
		return

	asyncio.get_event_loop().run_until_complete(cancel_all(websocket, json.dumps(msg)))	

def terminate(websocket):
	"""Termiante bot: close all orders and websocket

	Args:
		websocket (websockets object): authenticated websocket
	"""
	async def close(websocket):
		await websocket.close()
		return

	cancel_all_orders(websocket)
	asyncio.get_event_loop().run_until_complete(close(websocket))
