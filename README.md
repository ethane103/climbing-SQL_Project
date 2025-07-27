### What is this
I've wanted to learn SQL for a long time, so this repo contains my notes, and a demo project to show that process.

The demo project shows roughly how the MVP backend, and an extremely basic frontend of a service that allows users to upload, rate and search rock climbing walls across various gyms and locations. The primary focus is on how that database could be structured, filled and accsessed. 

### How to explore the projct
If you want to take a look at the project just dive right into the fillDB.ipynb file, which shows pretty clearly the process and state of the database as we create a number of tables. After that you can look at the QueryRunThroughSQL.png file to see how the query construction looks in practice, and then explore the \[userview <- app_views <- db_funcs\] pipeline, primarily the db_funcs file, to see how it goes from GUI to SQL database interaction.

### How to follow along if you want
If you want to follow along at home you'll need your own SQL server, and to create a database in it called climbing, as well as a user login with sufficient credentials to INSERT, UPDATE, DELETE, CREATE TABLEs, and set up cross table REFERENCES.

My reccomendation would be what I did which is set up a mySQL server running the (as of now) latest version, from where you can use mySQL workbench to handle the administration. You'll also need an up to date python installation, with ipynb, pandas, and pyodbc as well as some of the default packages. Finally you'll need to grab the mySQL odbc connecter.
