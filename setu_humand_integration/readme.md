Setu API Humand Integration
----------------------------------------
##### USAGE
* This module is used to connect with Humand Integration and creates user when employee are creates in odoo. 
* The values of created users in Humand Integration are getting from the employee created in odoo, i.e - email, firstName, lastName, hiringDate, birthdate etc.
* There are the fields **Access Token** and **Humand Default Password** in companies, it is used to connect with specific Humand Integration.
* There are the scheduled action(cron) name is - **Time-Off Requests From Humand**

##### CONFIGURATION
*       Settings -> Humand Integration -> Time-Off Requests Days
* There are the field Time-Off Requests Days at configuration where the filled numbers are consider as a days from the current date, and approved the time off under those manager in odoo between the current date and before from the current date which are set in the Time-Off Requests Days.