import mysql.connector
from decimal import Decimal
from datetime import datetime, timedelta
import time

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ALKATRAZE17omega",
    database="mydb"
)

mycursor = mydb.cursor(buffered=True)

def pizza_ingredient(pizza):
    querry = """
    SELECT 
    ingredient_pizza.idIngredient, ingredient.vegetarian
    FROM 
    ingredient_pizza JOIN ingredient 
    ON ingredient_pizza.idIngredient = ingredient.idIngredient 
    WHERE idPizza = '{}'
    """.format(pizza)
    mycursor.execute(querry)
    
    my_result = mycursor.fetchall()
    if len(my_result) == 0: #if there are no igredients then the pizza was not found in the ingredient list
        return None
    
    ingredients, veg = zip(*my_result)
    
    #convert from tuple to list
    ingredients = list(ingredients)
    veg = list(veg)
    
    #append vegetarian boolean at the end of the ingredient list
    for i, x in enumerate(veg):
        if x == 0:
            ingredients.append(0)
            break
        elif i == len(veg) - 1:
            ingredients.append(1)
            
    return ingredients
#print(pizza_ingredient("forbigboys"))

#returns a list of (name, price) tuples for item_type 'pizza', 'drink' and 'dessert'
def get_menu_listing(item_type):
    
    #func to add vat and margin
    def mark_up(tuple_list):
        mark_up_list = []
        for name, price in tuple_list:
            price = price * Decimal('1.09')#prices in the database are stored as decimal rather than float
            price = price * Decimal('1.4')
            mark_up_list.append((name, round(price, 2)))

        return mark_up_list
    
    # gets menu items from drink or deserts with their price.
    def get_direct_list(item_type):
        primary_key = "id" + item_type.capitalize()#our naming convention for primary keys

        querry = " SELECT {}, price FROM {}".format(primary_key, item_type)
        mycursor.execute(querry)

        my_result = mycursor.fetchall()
        return mark_up(my_result)
    
    #get's the price of pizza through ingredient prices
    def get_pizza_list():
        querry = """
        SELECT idPizza, SUM(price) FROM 
        (SELECT 
        ingredient_pizza.idPizza, 
        ingredient.price
        FROM 
        ingredient_pizza INNER JOIN ingredient
        ON
        ingredient_pizza.idIngredient = ingredient.idIngredient) AS pizza_ingredient_price
        GROUP BY idPizza
        """

        mycursor.execute(querry)

        my_result = mycursor.fetchall()

        return mark_up(my_result)
    
    #decide whether to us the pizza lister or other lister
    primary_key = "id" + item_type.capitalize()#our naming convention for primary keys
    if item_type == 'pizza':
        return get_pizza_list()
    else:
        return get_direct_list(item_type)

def check_coupon(coupon):
    querry = "SELECT code FROM discount WHERE code = '{}'".format(coupon)
    mycursor.execute(querry)
    my_result = mycursor.fetchall()

    if len(my_result) == 0:
        return False
    else:
        return True

#calculate order total
def order_total(order_list, valid_coupon=False):

    total = 0
    for name, price, quantity in order_list:
        total += price * quantity
        
    if valid_coupon:
        total = total * 0.9

    return total

def execute_order(order_list, idCustomer, use_coupon=None, reward_coupon=None):
    def remove_coupon(coupon):
        order_querry = """
        DELETE FROM 
        discount WHERE code = '{}'
        """.format(coupon)
        mycursor.execute(order_querry)
        mydb.commit()
        
    #get next idOrder auto-increment
    id_querry = """
    SELECT `AUTO_INCREMENT`
    FROM  INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'mydb'
    AND   TABLE_NAME   = 'orders';"""

    mycursor.execute(id_querry)
    my_result = mycursor.fetchone()
    idOrder = my_result[0]

    #insert in order tabl
    #check coupon values
    if check_coupon(use_coupon) == False:
        use_coupon = 'NULL'
    else:
          remove_coupon(use_coupon)
            
    if reward_coupon is None:
        reward_coupon = 'NULL'

    #insert the order
    order_querry = """
    INSERT INTO 
    orders (order_date_time, use_coupon, reward_coupon, idCustomer, status)
    VALUES (NOW(), {}, {}, {}, 0)
    """.format(use_coupon,reward_coupon,idCustomer)

    mycursor.execute(order_querry)

    #add items to order
    for item, _, quantity in order_list: ###CHANGE HERE

        item_querry = """
        INSERT INTO menu_order (idMenu, idOrder, quantity) VALUES ('{}','{}','{}')
        """.format(item, idOrder, quantity)

        mycursor.execute(item_querry)
    #commit the order and all items in one transaction
    mydb.commit()

    return idOrder

def get_pizza_count(idCustomer):
    querry = """
    SELECT number_of_pizza FROM customer 
    WHERE idCustomer = '{}'
    """.format(idCustomer)
    mycursor.execute(querry)
    
    return mycursor.fetchone()[0]
#gets the next auto incremented idCustomer, primary key of customer
def get_next_id():
    id_querry = """
    SELECT `AUTO_INCREMENT`
    FROM  INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'mydb'
    AND   TABLE_NAME   = 'customer';""" 
    
    mycursor.execute(id_querry)
    my_result = mycursor.fetchone()
    idCustomer = my_result[0]
    return idCustomer

#retrieves all orders made by a customer    
def get_order_list(idCustomer):
    querry = """
    SELECT idOrder, order_date_time 
    FROM orders 
    WHERE idCustomer = {}
    """.format(idCustomer)
    
    mycursor.execute(querry)
    my_result = mycursor.fetchall()
    
    id_order, time = zip(*my_result)
    id_order = list(id_order)
    time = list(time)
    str_time = []
    for t in time:
        str_time.append(t.strftime("%m/%d/%Y, %H:%M"))
    
    final_result = list(zip(id_order, str_time))
    
    return final_result

#creates a new customer
def make_customer(cstmr_data):
    querry = """
    INSERT INTO 
    customer(firstname, lastname, phone, street_number, street_addition, street_name, zipcode, number_of_pizza) 
    VALUES ('{}','{}','{}','{}','{}','{}','{}',0)
    """.format(*cstmr_data)
    
    mycursor.execute(querry)
    mydb.commit()
    
    #['first name', 'last name', 'phone number', 'street number', 'addition', 'street name', 'post code']

#autoincrement a discount code
def generate_coupon():
    querry = """
    SELECT `AUTO_INCREMENT`
    FROM  INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'mydb'
    AND   TABLE_NAME   = 'discount';""" 
    
    mycursor.execute(querry)
    my_result = mycursor.fetchone()
    coupon = my_result[0]
    
    add_querry = """
    INSERT INTO discount (code) VALUES ({})
    """.format(coupon)
    
    mycursor.execute(add_querry)
    mydb.commit()
    
    return coupon

#cancels an order
def cancel(idOrder):
    mycursor.execute("SELECT order_date_time FROM orders WHERE idOrder ='{}'".format(idOrder))
    list_time = mycursor.fetchall()

    for x in list_time:
        if (x[0] + timedelta(minutes=5)) > datetime.today():
            mycursor.execute("DELETE FROM orders WHERE idOrder = '{}' ".format(idOrder))
            mydb.commit()
            return 1
        else:
            return 0

#adds or removes pizza counts from a customer
def set_pizza_count(idCustomer,count):
    querry = """
    UPDATE customer SET number_of_pizza = '{}'
    WHERE idCustomer = '{}'""".format(get_pizza_count(idCustomer)+count,idCustomer)
    mycursor.execute(querry)
    mydb.commit()

#estimates the time it would take to get you pizza in minutes
def estimate_time(idOrder):
    mycursor.execute("SELECT idCustomer FROM orders WHERE idOrder = '{}'".format(idOrder))
    my_result = mycursor.fetchall()
    mydb.commit()
    final_result = []
    for x in my_result:
        final_result.append(x[0])
    print(str(len(my_result)) + " : final result")

    mycursor.execute("SELECT zipcode FROM customer WHERE idCustomer = '{}'".format(final_result[0]))
    zipcode = mycursor.fetchall()
    final_zipcode = []
    for x in zipcode:
        final_zipcode.append(x[0])

    mycursor.execute("SELECT idOrder, zipcode FROM (SELECT orders.idOrder, orders.status, customer.zipcode FROM orders JOIN customer ON orders.idCustomer = customer.idCustomer) AS T WHERE T.status != 4 AND T.zipcode='{}'".format(final_zipcode[0]))
    number_of_zipcode = mycursor.fetchall()
    print(len(number_of_zipcode))

    mycursor.execute("SELECT idDriver FROM delivery_ops WHERE zipcode = '{}'".format(final_zipcode[0]))
    drivers = mycursor.fetchall()
    final_drivers = []
    for x in drivers:
        final_drivers.append(x[0])
    print(len(final_drivers))

    value = (((len(number_of_zipcode))/(len(final_drivers)))*30) + 10
    if value < 40:
        value = 40
    return value