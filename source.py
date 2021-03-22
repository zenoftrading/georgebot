import asyncio, websockets, json, random
import config as cfg

def get_msg_id(msg_id):
	msg_id += 1
	return msg_id

def authentication():
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
		return websocket

	ws = asyncio.get_event_loop().run_until_complete(auth(json.dumps(msg)))

	return ws

def get_current_price(websocket,instrumet):
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
		# print(json.dumps(json.loads(response), indent=4))
		try:
			return json.loads(response)['result']['mark_price']
		except:
			return 0

	return asyncio.get_event_loop().run_until_complete(ticker(websocket, json.dumps(msg)))

def set_order(websocket,status,price,amount,instrument):
	# cfg.msg_id += 1
	# msg = \
	#     {
	#         "jsonrpc": "2.0",
	#         "id": cfg.msg_id,
	#         "method": "private/" + status,
	#         "params": {
	#             "instrument_name": instrument,
	#             "amount": amount,
	#             "type": "limit",
	#             "price": price
	#         }
	#     }

	# async def order(websocket, msg):
	#     await websocket.send(msg)
	#     response = await websocket.recv()
	#     print(json.dumps(json.loads(response), indent=4))
	#     return json.loads(response)['result']['order']['order_id']

	# order_id = asyncio.get_event_loop().run_until_complete(order(websocket, json.dumps(msg)))
	
	print("{} {} {} on {}".format(status,amount,instrument,price))
	order_id = 0

	return order_id

def check_order(websocket,order_id):
	# cfg.msg_id += 1
	# msg = \
	#     {
	#         "jsonrpc": "2.0",
	#         "id": cfg.msg_id,
	#         "method": "private/get_order_state",
	#         "params": {
	#             "order_id": order_id
	#         }
	#     }

	# async def check(websocket, msg):
	#     await websocket.send(msg)
	#     response = await websocket.recv()
	#     print(json.dumps(json.loads(response), indent=4))
	#     # return True if order was closed and False another
	#     return json.loads(response)['result']['order_state'] != 'open'

	# order_status = asyncio.get_event_loop().run_until_complete(check(websocket, json.dumps(msg)))    
	
	print("Checking order {}".format(order_id))
	order_status = random.choice([True, False])
	print("Order status {}".format(order_status))
	
	return order_status

def cancel_order(websocket,order_id):
	# cfg.msg_id += 1
	# msg = \
	#     {
	#         "jsonrpc": "2.0",
	#         "id": cfg.msg_id,
	#         "method": "private/cancel",
	#         "params": {
	#             "order_id": order_id
	#         }
	#     }

	# async def cancel(websocket, msg):
	#     await websocket.send(msg)
	#     response = await websocket.recv()
	#     print(json.dumps(json.loads(response), indent=4))
	#     return

	# asyncio.get_event_loop().run_until_complete(cancel(websocket, json.dumps(msg)))
	
	print("Cancelling order {}".format(order_id))
