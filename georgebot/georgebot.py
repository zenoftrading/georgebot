import sys, peewee
import source as src
import config
import database as db

def main(argv):
	config_filename = argv[1]
	config = src.read_config(config_filename)
	websocket = src.authentication(config['exchange'])

	try:
		src.run(websocket,config)
	except Exception as e:
		print("Bot error: {}".format(e))
	finally:
		src.terminate(websocket)

if __name__ == '__main__':
	if len(sys.argv) > 1:
		db.create_tables()
		main(sys.argv)
	else:
		print("Try to use: python georgebot.py <configuration_file.yaml>")
