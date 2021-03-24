import sys
import config as cfg
import source as src

def main(argv):
	config_filename = argv[1]
	
	cnf = src.read_config(config_filename)
	gap = cnf['robot']['gap']
	gap_ignore = cnf['robot']['gap_ignore']
	amount = cnf['robot']['amount']
	
	websocket = src.authentication(cnf['exchange'])
	
	current_price = src.get_current_price(websocket,cfg.instrument)
	buy_price = current_price - gap / 2
	sell_price = current_price + gap

	print("buy_price {}, sell_price {}".format(buy_price,sell_price))
	status = 'buy'
	order_id = src.set_order(websocket,status,buy_price,amount,cfg.instrument)

	while True:
		current_price = src.get_current_price(websocket,cfg.instrument)
		if status == 'buy' and current_price > 0:
			if src.check_order(websocket,order_id):
				status = 'sell'
				sell_price = current_price + gap
				print("buy_price {}, sell_price {}".format(buy_price,sell_price))
				order_id = src.set_order(websocket,status,sell_price,amount,cfg.instrument)
			
			elif current_price > buy_price + gap + gap_ignore:
				src.cancel_order(websocket,order_id)
				buy_price = current_price - gap/2
				print("buy_price {}, sell_price {}".format(buy_price,sell_price))
				order_id = src.set_order(websocket,status,buy_price,amount,cfg.instrument)
		
		elif status == 'sell' and current_price > 0:
			if src.check_order(websocket,order_id):
				status = 'buy'
				buy_price = current_price - gap/2
				print("buy_price {}, sell_price {}".format(buy_price,sell_price))
				order_id = src.set_order(websocket,status,buy_price,amount,cfg.instrument)

			elif current_price < sell_price - gap - gap_ignore:
				src.cancel_order(websocket,order_id)
				sell_price = current_price + gap
				print("buy_price {}, sell_price {}".format(buy_price,sell_price))
				order_id = src.set_order(websocket,status,sell_price,amount,cfg.instrument)

		else:
			print("Order status error")
			status = 'buy'	

if __name__ == '__main__':
	if len(sys.argv) > 1:
		main(sys.argv)
	else:
		print("Try to use: python georgebot.py <configuration_file.yaml>")
