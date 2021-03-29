import peewee
import config as cfg

DATABASE_NAME = 'deals.db'

database = peewee.SqliteDatabase(DATABASE_NAME)

class BaseModel(peewee.Model):
    """Base model with meta information of database classes
    """
	class Meta:
		database = database

class Order(BaseModel):
    """Class with table Order structure
    """
    date = peewee.DateTimeField()
    order_id = peewee.IntegerField()
    status = peewee.CharField()
    amount = peewee.DoubleField()
    price = peewee.DoubleField()
    executed = peewee.BooleanField(default=False)

def create_tables():
    """Helper function to create database
    """
    with database:
        database.create_tables([Order])

def add_order_to_db(date,order_id,status,amount,price):
    """Adding order details to database

    Args:
        date (datetime): order adding date
        order_id (int): order id
        status (string): 'buy' or 'sell'
        amount (double): amount
        price (double): price

    Returns:
        boolian: True if add order details and False in opposit case
    """
    try:
        Order.create(
            date = date,
            order_id = order_id,
            status = status,
            amount = amount,
            price = price
        )
        print("Add order {}".format(order_id))
        return True
    except Exception as e:
        print("add_order_to_db error: {}".format(e))
        return False

def update_order(order_id):
    """Set True if order executed

    Args:
        order_id (int): order id
    """
    try:
        order = Order.get(Order.order_id == order_id)
        order.executed = True
        order.save()
        print("Update order {}".format(order_id))
    except Exception as e:
        print("update_order error: {}".format(e))