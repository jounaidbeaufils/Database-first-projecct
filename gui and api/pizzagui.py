from tkinter import*
import pizzasql as ps
from decimal import Decimal

#keep track of logged in user
idCustomer = None

#menu window from which an order is placed
def menu_window(window=None):
    
    if window is not None:
        window.destroy()
    
    #tracking menu inputs
    pizza_input = []
    drink_input = []
    dessert_input = []
        
    window = Tk()
    
    #pizza frame
    pizza_frm = Frame(master= window)
    pizza_frm.grid(row=0, column=0,rowspan=2)

    pizza_list = ps.get_menu_listing("pizza")
    create_menu_list(pizza_frm, pizza_list, "pizza", pizza_input)
    
    #drink frame
    drink_frm = Frame(master= window)
    drink_frm.grid(row=0, column=1,)

    drink_list = ps.get_menu_listing("drink")
    create_menu_list(drink_frm, drink_list, "drinks", drink_input)

    #dessert frame
    dessert_frm = Frame(master= window)
    dessert_frm.grid(row=1, column=1,)

    dessert_list = ps.get_menu_listing("dessert")
    create_menu_list(dessert_frm, dessert_list,"dessert", dessert_input) 

    #discount frame
    discount_frm = Frame(master=window)
    discount_frm.grid(row=3, column=0)
    discount_lbl = Label(master=discount_frm, text="enter a discount code")
    discount_lbl.grid(row=0, column=0)
    discount_ent = Entry(master = discount_frm)
    discount_ent.grid(row=1,column=0)

    #checkout button
    checkout_btn = Button(text="Checkout", command=lambda: checkout())
    checkout_btn.grid(row=3, column=1)

    def checkout():
        #clean up user intput and match to menu items
        def data_get(x_input, x_list):
            x_data = []
            for x in x_input:
                x_data.append(x.get())
            
            
            name, price = zip(*x_list) #CHANGE HERE
            final_data = list(zip(name, price, x_data)) #CHANGE HERE
            return final_data
        
        piz = data_get(pizza_input, pizza_list)
        dri = data_get(drink_input, drink_list)
        des = data_get(dessert_input, dessert_list)
        
        #read coupon
        #print(len(discount_ent.get()) == 0)
        
        #count pizza in order
        _ , _, pizza_count = zip(*piz)#CHANGE HERE
        pizza_count = sum(map(int, pizza_count))
        print(pizza_count)
        
        #no order without a pizza
        if pizza_count > 0:
            reward_coupon = None
            use_coupon = discount_ent.get()
            #check coupon validity
            if ps.check_coupon(use_coupon) == False:
                use_coupon = None
            
            #check if the customer should be awarded a coupon
            past_pizza = ps.get_pizza_count(idCustomer)
            print(past_pizza)
            if (pizza_count + past_pizza) >= 10:
                reward_coupon =  ps.generate_coupon()
                ps.set_pizza_count(idCustomer, -10)
            
            #remove items that aren't ordered
            order_list = piz + dri + des
            order_list[:] = [tup for tup in order_list if tup[2] != '0']
            
            # execute order
            idOrder = ps.execute_order(order_list, idCustomer, use_coupon, reward_coupon)
            ps.set_pizza_count(idCustomer, pizza_count)
            
            # popup with coupon code(optional) and order summary
            popup = Toplevel()
            
            summary_text = []
            total = 0
            for item, price, quantity in order_list:
                total += Decimal(price) * int(quantity)
                summary_text.append(str(item) +  ", " + str(price) + ", x" + quantity)
                
            if use_coupon is not None:
                total = total * Decimal("0.9")
                total = round(total, 2)
            
            summary_lbl = Label(popup, text = ",\n".join(summary_text))
            summary_lbl.grid(row=0,column=0)
            
            total_lbl  = Label(popup, text= "total: {}".format(total))
            total_lbl.grid(row=1,column=0)
            
            est = ps.estimate_time(idOrder)
            print("est: {}".format(est))
            estimate_lbl = Label(popup, text="estimated time to delivery: {} mins".format(est))
            estimate_lbl.grid(row=2, column= 0)

            if reward_coupon is not None:
                coupon_lbl = Label(popup, text= "new coupon code: {}".format(reward_coupon))
                coupon_lbl.grid(row=3, column=0)
            
            ok_btn = Button(popup, text="OK", command= lambda: account_window(window))
            ok_btn.grid(row=4, column=0)
            
    
    window.mainloop()
##########################################



#this function creates a list of items from a menu category.
def create_menu_list(target_frm, source_list, menu_list_name, input_list):
    #title
    name_lbl = Label(master = target_frm, text = menu_list_name)
    name_lbl.grid(row = 0, column = 0, columnspan = 3)
    
    #heading
    pizza_lbl = Label(master = target_frm, text = "options")
    pizza_lbl.grid(row = 1, column = 0)
    
    price_lbl = Label(master = target_frm, text = "unit price")
    price_lbl.grid(row = 1, column = 1)
    
    quantity_lbl = Label(master = target_frm, text = "quantity")
    quantity_lbl.grid(row = 1, column = 2)
    
    for i, item in enumerate(source_list):
        
        name_btn = Button(master= target_frm, text= item[0], fg = "blue", relief=FLAT, 
            command= lambda i=i: pizza_popup(source_list[i][0])) # i=i to bypass python closure
        name_btn.grid(row = i+3, column = 0)
        
        price_lbl = Label(master= target_frm, text= item[1])
        price_lbl.grid(row = i+3, column = 1)
        
        quantity_spbx = Spinbox(master= target_frm, from_ = 0,  to = 20)
        quantity_spbx.grid(row = i+3, column = 2)
        input_list.append(quantity_spbx)

    
####popup to show ingredientsof pizza
def pizza_popup(pizza):
    
    #ingrident list
    ingredient_list = ps.pizza_ingredient(pizza)#returns None if the ingredient is not a pizza
    
    if ingredient_list is None:
        return
    #vegetarian check is the last item in the ingredient list
    is_veg = ingredient_list.pop()
    
    popup = Toplevel()
    
    ingredient_lbl = Label(popup, text = ",\n".join(ingredient_list))
    ingredient_lbl.grid(row=0, column=0)
    
    if is_veg:
        is_veg = "This pizza is vegetarian"
    else:
         is_veg = "This pizza is NOT vegetarian"
            
    veg_lbl = Label(popup, text=is_veg)
    veg_lbl.grid(row=1, column=0)
    
    ok_btn = Button(popup, text="OK", command= lambda: popup.destroy())
    ok_btn.grid(row=2,column=0)

def login_window(window=None):
    
    if window is not None:
        window.destroy()
    
    
    window = Tk()
    
    #user name input
    user_lbl = Label(text="Customer ID")
    user_lbl.grid(row=0, column=0)
    user_ent = Entry()
    user_ent.grid(row=0, column=1)
    
    def login():
        global idCustomer 
        idCustomer= int(user_ent.get())
        menu_window(window)
    
    # login button
    login_btn = Button(window, text='Login', command=lambda: login())
    login_btn.grid(row=2, column=1)
    
    def register():
        global idCustomer 
        idCustomer = ps.get_next_id()
        register_window(window)
    
    # Register button
    register_btn = Button(window, text='Register', command=lambda: register())
    register_btn.grid(row=2,column=0)
    
    window.mainloop()
########################################## 

def account_window(window=None):
    
    if window is not None:
        window.destroy()
    #track order selecttion input
    order_input = []
    
    window = Tk()

    ####Orders Frame####
    orders_frm = Frame(window)
    orders_frm.grid(row=0,column=0)
    orders_lbl = Label(orders_frm, text="orders")
    orders_lbl.grid(row=0,column=0)
    
    ###orders_display_frame###
    order_disp_frm = Frame(orders_frm)
    order_disp_frm.grid(row=1,column=0)
    
    order_list = ps.get_order_list(idCustomer)
    
    #headings
    order_lbl = Label(master = order_disp_frm, text = "order id")
    order_lbl.grid(row = 0, column = 0)
    
    time_lbl = Label(master = order_disp_frm, text = " date and time")
    time_lbl.grid(row = 0, column = 1)
    
    #order listbox
    order_lst = Listbox(order_disp_frm)
    order_lst.grid(row=1, column=0, columnspan=2)
    #add_orders
    for item in order_list:
        order_lst.insert(END, item)

    # Menu button
    menu_btn = Button(orders_frm,text='MENU',command=lambda: menu_window(window))
    menu_btn.grid(row=2,column=0)
    
    # Cancel button
    cancel_btn = Button(orders_frm, text='CANCEL ORDER', command=lambda: cancel_order())
    cancel_btn.grid(row=3,column=0)
    
    def cancel_order():
        idOrder = order_lst.get(ANCHOR)[0]
        cancel_check = ps.cancel(idOrder)
        
        #check if the order was canceled
        if cancel_check == 1:
            popup = Toplevel()
            
            confirm_lbl = Label(popup, text="order cancelled")
            confirm_lbl.grid(row=0, column=0)
            
            ok_btn = Button(popup, text="OK", command= lambda: account_window(window))#reloads window
            ok_btn.grid(row=1, column=0)
            
        else:
            popup = Toplevel()
            
            confirm_lbl = Label(popup, text="order can't be cancelled after 5 min")
            confirm_lbl.grid(row=0, column=0)
            
            ok_btn = Button(popup, text="OK", command= lambda: popup.destroy())#reloads window
            ok_btn.grid(row=1, column=0)
    
    window.mainloop()
##########################################

def register_window(window=None):
    
    if window is not None:
        window.destroy()
    
    #track user input
    info_input = []
    
    window = Tk()
    
    ###personal detail frame###
    pdetails_frm = Frame(window)
    pdetails_frm.grid(row=0,column=0)
    
    #first name
    fname_lbl = Label(pdetails_frm, text= "first name")
    fname_lbl.grid(row=0,column=0)
    fname_ent = Entry(pdetails_frm)
    fname_ent.grid(row=0, column=1)
    info_input.append(fname_ent)
    
    #last name
    lname_lbl = Label(pdetails_frm, text="last name")
    lname_lbl.grid(row=1,column=0)
    lname_ent = Entry(pdetails_frm)
    lname_ent.grid(row=1, column=1)
    info_input.append(lname_ent)
    
    #phone number
    phone_lbl = Label(pdetails_frm, text= "phone number")
    phone_lbl.grid(row=2, column=0)
    phone_ent = Entry(pdetails_frm)
    phone_ent.grid(row=2, column=1)
    info_input.append(phone_ent)

    ###address frame###
    address_frm = Frame(window)
    address_frm.grid(row=0, column=1)
      
    #make column 1 three time wider than 0
    address_frm.columnconfigure(0, weight=1)
    address_frm.columnconfigure(1, weight=3)

    #street number
    number_lbl = Label(address_frm, text="street number")
    number_lbl.grid(row=0,column=0)
    number_ent = Entry(address_frm)
    number_ent.grid(row=0,column=1)
    info_input.append(number_ent)

    #street addition
    addition_lbl = Label(address_frm, text="addition")
    addition_lbl.grid(row=1,column=0)
    addition_ent = Entry(address_frm)
    addition_ent.grid(row=1,column=1)
    info_input.append(addition_ent)

    #street name
    sname_lbl = Label(address_frm, text="street name")
    sname_lbl.grid(row=2,column=0)
    sname_ent = Entry(address_frm)
    sname_ent.grid(row=2,column=1)
    info_input.append(sname_ent)

    #post code
    code_lbl = Label(address_frm, text="post code")
    code_lbl.grid(row=3,column=0)
    code_ent = Entry(address_frm)
    code_ent.grid(row=3,column=1)
    info_input.append(code_ent)
    
    #customer id
    cstmr_lbl = Label(window, text="customer number: {}".format(idCustomer))
    cstmr_lbl.grid(row=2, column=0)
    
    #save button
    save_btn = Button(window, text="SAVE", command= lambda: save_cstmr())
    save_btn.grid(row=2, column=1)
    
    def save_cstmr():
        cstmr_data = []
        for ent in info_input:
            cstmr_data.append(ent.get())
        
        #create customer
        ps.make_customer(cstmr_data)
        menu_window(window)
    
    
    window.mainloop()