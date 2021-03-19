import config as cfg
import source as src

def main():
	gap = 100
	gap_ignore = 50
	
	websocket = src.authentication()
	
	current_price = src.get_current_price(websocket,cfg.instrument)
	buy_price = current_price - gap / 2
	sell_price = current_price + gap

	print("Buy order")
	in_position = False

	while True:
		current_price = src.get_current_price(websocket,cfg.instrument)
		if not in_position:
			if current_price <= buy_price:
				print("Sell order")
				in_position = True
			
			if current_price > buy_price + gap + gap_ignore:
				print("Cancel buy order")
				buy_price = current_price - gap / 2
				print("Buy order")
			if current_price < sell_price - gap - gap_ignore:
				print("Cancel sell order")
				sell_price = current_price + gap
				print("Sell order")
		elif in_position:
			if current_price >= sell_price:
				print("Sell order")
				in_position = False
			
		
		

if __name__ == '__main__':
	main()
