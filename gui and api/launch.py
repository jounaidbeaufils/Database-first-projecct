import pizzagui as pg
import pizzadelivery as pd
from multiprocessing import Process

if __name__ == '__main__':
    Process(target=pd.delivery_loop).start()
    Process(target=pg.login_window).start()