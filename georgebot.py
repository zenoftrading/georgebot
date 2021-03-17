import asyncio
import websockets
import json

msg = \
{
  "id" : 1,
  "method" : "public/get_mark_price_history",
  "params" : {
    "instrument_name" : "BTC-25JUN21-50000-C",
    "start_timestamp" : 1609376800000,
    "end_timestamp" : 1609376810000
  },
  "jsonrpc" : "2.0"
}

async def call_api(msg):
   async with websockets.connect('wss://test.deribit.com/ws/api/v2') as websocket:
       await websocket.send(msg)
       while websocket.open:
           response = await websocket.recv()
           # do something with the response...
           print(response)

asyncio.get_event_loop().run_until_complete(call_api(json.dumps(msg)))
