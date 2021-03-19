import asyncio
import websockets
import json
import config as cfg

def get_msg_id(msg_id):
	msg_id += 1
	return msg_id

def authentication():
	cfg.msg_id = get_msg_id(cfg.msg_id)
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
		websocket = await websockets.client.connect(cfg.uri)
		await websocket.send(msg)
		response = await websocket.recv()
		# print(json.dumps(json.loads(response), indent=4))
		return websocket

	ws = asyncio.get_event_loop().run_until_complete(auth(json.dumps(msg)))

	return ws

def get_current_price(websocket,instrumet):
	cfg.msg_id = get_msg_id(cfg.msg_id)
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
		return json.loads(response)['result']['mark_price']

	return asyncio.get_event_loop().run_until_complete(ticker(websocket, json.dumps(msg)))

def place_order(websocket, state, price, amount, instrument):
    cfg.msg_id = get_msg_id(cfg.msg_id)
    msg = \
        {
            "jsonrpc": "2.0",
            "id": cfg.msg_id(),
            "method": "private/" + state,
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
        print(json.dumps(json.loads(response), indent=4))
        return json.loads(response)['result']['order']['order_id']

    order_id = asyncio.get_event_loop().run_until_complete(order(websocket, json.dumps(msg)))

    return order_id