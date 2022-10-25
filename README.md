# Database-first-projecct
First Dtabase project for KEN2110 (Jounaid Beaufils &amp; Laurent Bijman)

Aknowledging SQL injection vulnerability
Not all functions are defined where they should be
We ~probably~ should have used OOP and SQLAlchemy, as well as a few views to hide complexity

Databases
- contains SQL files to build and populate the database
- this was done with MySQL

gui and api
- contains python file to launch project
- launch.py -> run this file after installing the database to run the delivery app
- pizzagui.py -> contains the UI of the app
- pizzasql.py -> contains the method used to querry the database
- deliverysql.py -> a loop used to deliver pizzas and simulate drivers
