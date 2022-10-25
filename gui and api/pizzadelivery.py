import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ALKATRAZE17omega",
    database="mydb",
    autocommit = True
)

mycursor = mydb.cursor(buffered=True)

from datetime import datetime, timedelta
import time

def delivery_loop():
    def check_for_State_Zero():
        mycursor.execute("SELECT * FROM orders WHERE status=0")
        size = mycursor.fetchall()
        print(size)
        print("salut")

        for i in size:
            mycursor.execute("SELECT idOrder FROM orders WHERE status = 0 LIMIT 1")
            index = mycursor.fetchall()

            final_index = []
            for x in index:
                final_index.append(x[0])

            mycursor.execute("SELECT idCustomer FROM orders WHERE status = 0 LIMIT 1")
            person = mycursor.fetchall()
            final_person = []
            for x in person:
                final_person.append(x[0])


            mycursor.execute("SELECT zipcode FROM customer WHERE idCustomer = '{}'".format(final_person[0]))
            zipcode = mycursor.fetchall()

            check_For_State_One(final_index[0])
            time.sleep(2)

    def check_For_State_One(index):
        now = datetime.today()
        print(now)
        mycursor.execute("UPDATE orders SET order_date_time = '{}' WHERE idOrder = '{}' ".format(now,index))
        mycursor.execute("UPDATE orders SET status = '{}' WHERE idOrder = '{}' ".format(1,index))
        mydb.commit()

    def check_For_State_Two():
        mycursor.execute("SELECT order_date_time FROM orders WHERE status=1")
        list_time = mycursor.fetchall()


        for x in list_time:
            if (x[0] + timedelta(minutes=10)) < datetime.today():
                print("send order number to waiting")
                mycursor.execute("UPDATE orders SET status = '{}' WHERE order_date_time = '{}' ".format(2,x[0]))
                mydb.commit()

    def check_For_Deliverying():
        mycursor.execute("SELECT * FROM orders ORDER BY order_date_time")
        mycursor.execute("SELECT idCustomer FROM orders WHERE status=2")
        list_time = mycursor.fetchall()
        if len(list_time) == 0:
            return
        get_person = []
        for x in list_time:
            get_person.append(x[0])


        mycursor.execute("SELECT zipcode FROM customer WHERE idCustomer='{}'".format(get_person[0]))
        zipcode = mycursor.fetchall()
        final_zipcode = []
        for x in zipcode:
            final_zipcode.append(x[0])


        mycursor.execute("SELECT idOrder FROM orders WHERE idCustomer='{}'".format(get_person[0]))
        idOrder = mycursor.fetchall()
        final_idOrder = []
        for x in idOrder:
            final_idOrder.append(x[0])


        mycursor.execute("SELECT idOrder FROM delivery_ops WHERE zipcode='{}'".format(final_zipcode[0]))
        result = mycursor.fetchall()
        final_result = []
        for x in result:
            final_result.append(x[0])
        if final_result[0] == None:

            mycursor.execute("UPDATE delivery_ops SET idOrder = '{}' WHERE zipcode='{}' ".format(final_idOrder[0],final_zipcode[0]))
            mycursor.execute("UPDATE orders SET status = '{}' WHERE idOrder='{}' ".format(3,final_idOrder[0]))
            mydb.commit()

    def check_if_delivered():
        mycursor.execute("SELECT order_date_time FROM orders WHERE status=3")
        list_time = mycursor.fetchall()
        if len(list_time) == 0:
            return 0

        #print(list_time)
        for x in list_time:
            if (x[0] + timedelta(minutes=30)) < datetime.today():
                print("your order is delivered")
                mycursor.execute("UPDATE orders SET status = '{}' WHERE order_date_time = '{}' ".format(4,x[0]))
                mydb.commit()
            else:
                print("the order is on the way")


    #Check every 10 secondes to see if we can update the status of different commands
    while True:
        #Set the current orders from status 0 to status 1, to prepare the pizzas
        check_for_State_Zero()
        #check if the pizza is done preparing and see if the pizza can be send to be picked up by a delivery driver
        check_For_State_Two()
        #Check if the pizza can be taken by the driver that has the same zipcode 
        check_For_Deliverying()
        #Check if the pizza that the driver had taken is delivered
        check_if_delivered()
        print(datetime.today())
        time.sleep(10)  

#statement select order number, zipcode & status (make status)
#ordertime + 10 mins 
#nothing, preparing, waiting, deliverying, delivered

#wait time is the status is at 0 that means you need at least to wait 10 mins + 30 mins (+30 if another pizza is sent)
#wait time is the status is at 1 that means you need at least to wait +-10 mins + 30 mins (+30 if another pizza is sent)
#wait time is the status is at 2 that means you need at least to wait 30 mins (+30 if another pizza is sent)
#wait time is the status is at 3 that means you need at least to wait +-30 mins 
#wait time is the status is at 4 that means you need at least to wait 0 min (pizza is delivered)