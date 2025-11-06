Setu Odoo Mirakl Connector
-------------------------

##### USAGE
* This module are mainly used to sync the sale order from **mirakl connector** to odoo.
* Here are the main menu **Mirakl** and under the menu there are various menus like - **Dashboard, Operations, Process History, Configuration**
* At the **Dashboard** There are Visible the records of Mirakl connector.
* Under the **Operations** there are a submenu **Mirakl Operations** from the **Mirakl Operations** opened the wizard - **Mirakl Operations** here filled the **Multi e-Commerce Connector** where displayed only fully integrated records and another one is **Operations** here if selects a value Import Specific Order-IDS here visible the new page **Sync Option** at there added a sale order id from connector and Perform Operation then creates a sale order in odoo as per the connector's order, if the API Key and Host are valid.  
* Here status of sale order are managed from connector's order status i.e - status are **Awaiting shipment** then confirmed the sale order else in other stages sale order are created in draft state.
* Here if order are created one time and tried to again sync same order from same connector then not allowed and raise validation like **This Sale order Already exist**
* Here if the product in connector are created in odoo then and only then creates a sale order for these particular products.
* But if the Partner are not in odoo so as per the e-commerce partner, partner are created in odoo.
* during creating an sale order there are also attachment are set from the order and attached it to the odoo's sale order here document are attached only if type are SHIPPING LABEL not takes other documents for it.
* Here also added Mirakl Payment Gateway, and it creates during creating a sale order and these Payment Gateway are set to those created sale order.

##### CONFIGURATION
* There are a category for accessing it, which is - Mirakl and there are a various group for it - **User**, **Manager** 
* If the user has manager's rights then and only then it has visible and accessing the features of **Operations, Process History, Configuration** in mirakl menu.
* Here only creates a sale order after the date which are set at the **Import Order After Date** in the **Mirakl Setup** page.

