import asyncio, websockets, json, random
import config as cfg

def authentication():
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
				"client_id": cfg.client_id,
				"client_secret": cfg.client_secret
			}
		}

	async def auth(msg):
		websocket = await websockets.connect(cfg.uri)
		await websocket.send(msg)
		# response = await websocket.recv()
		# print("websocket: {}".format(response))
		return websocket

	ws = asyncio.get_event_loop().run_until_complete(auth(json.dumps(msg)))

	return ws

def get_current_price(websocket,instrumet):
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
				"instrument_name": instrumet
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

	async def order(websocket, msg):
		await websocket.send(msg)
		response = await websocket.recv()
		try:
			return json.loads(response)['result']['order']['order_id']
		except Exception as e:
			print("set_order error: {}".format(e))
			return False

	order_id = asyncio.get_event_loop().run_until_complete(order(websocket, json.dumps(msg)))
	
	print("{} {} {} on {}".format(status,amount,instrument,price))
	# order_id = 0

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
		return json.loads(response)['result']['order_state'] != 'open'

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

	async def cancel(websocket, msg):
		await websocket.send(msg)
		# response = await websocket.recv()
		# print(json.dumps(json.loads(response), indent=4))

	asyncio.get_event_loop().run_until_complete(cancel(websocket, json.dumps(msg)))
	
	print("Cancelling order {}".format(order_id))
