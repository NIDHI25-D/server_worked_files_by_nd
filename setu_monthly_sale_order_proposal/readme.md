Setu Create Monthly Sale Order Proposal
----------------------------------------
##### USAGE
* This module facilitates Automatically create sale order based on customer past month and year sale orders.
* After creation of monthly or interval proposal sale order, it will send email to customer and configured users from settings
* This module, includes two cron(scheduled actions) named : 
  * **Create Monthly Sale Order Proposal**.
  * **Create Interval Monthly Sale Order Proposal**.
* Interval proposal Only include customers who were created at least 3 months ago, but no more than 1 year and 1 day ago



##### CONFIGURATION
*       Contacts -> Sales & Purchase
* add this field value:
  * Monthly Proposal Pricelist 

*       Settings -> Website -> Monthly Proposal
* add these fields values:
  * Message 
  * Select user to send mail about monthly proposal
