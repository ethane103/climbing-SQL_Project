### What is this
I've wanted to learn SQL for a long time, so this repo contains my notes, and a demo project to show that process.

The demo project shows roughly how the MVP backend of a service that allows users to upload, rate and search rock climbing walls across various gyms and locations. The primary focus is on how that database could be structured, filled and accsessed. 
The project is still a WIP but so far the database filling is mostly done, and already showcases hosting a mySQL server on my local machine, a handle on how to acsess and interface with SQL, and linking SQL into python.

If you want to take a look at the project just dive right into the fillDB.ipynb file, which shows pretty clearly the process and state of the database as we create a number of tables.

If you want to follow along at home you'll need your own SQL server, and to create a database in it called climbing, as well as a user login with sufficient credentials to INSERT, UPDATE, DELETE, CREATE TABLEs, and set up cross table REFERENCES.
My reccomendation would be what I did which is set up a mySQL server running the (as of now) latest version, from where you can use mySQL workbench to handle the administration. You'll also need an up to date python installation, with ipynb, pandas, and pyodbc 
as well as some of the default packages. Finally you'll need to grab the mySQL odbc connecter.
