Marvel Fields
-----------------------------

### USAGE

### Website

* There is configuration for the Billing General Public in contact.
* in contact, you can add a public address that while any order is from the website, if this option is selected, then the billing address will get changed as per the configuration.
* also there is added sorting product and some searching method changes for category and attribute.

### Sale Order

* There are some warehouse and client related changes.
* set a warehouse on a sale order as per set as customer.
* set dfactura_invoice as per the sale order.
* Set a mostrador as per the shipping method configuration.
* To set the mark is done in to sale order from sale order activities.


### Invoices

* dfactura invoice, mostrador added for a reference form the sale order to invoices.
* to trace the due date if it is changed by the odoo bot.
* for a vendor bill, it set the reference if the bill has no payment reference.
* Set x_studio_detener_factura fields in the stock_picking according to set dfactura fields in the sale order. 

### Delivery Method

* There is configration Is Mostrador Delivery Method then it will affect on the sale order.
* Remove a shipping method if partner is excluded from the shipping method.

### Warehouse

* Added one field to add Suggested Assortment to warehouses.

### Employee

*  Set an antiquity in years as per the income date.

### Products

* Set a length, width and high in products and products template.

### Purchase

* Added additional Fields to purchase order.
* set an email_cc as per the purchase order email_cc while creating mail.

### Mail

* While creating mail added, if mail is created by purchase order, then it's adding Email CC as per purchase order.

### Stock Transfers
    **Configuration**
    =================
    * Added Transfer Unlock Group To Give User Access limits.
    * Added Authorized Shipment Date Group To Give User Access limits.
* Added some additional fields.
* Button to set the current date while normal sale order but when if sale order from website then customer confirmation date will filled up automatically, this is for customer confirmation.

### Follow-Up Reminder From Partner

* Added Some modification to send mail to partner's child ids If chile partner Ticked For sending mail.

### Locations

* Added Volume Field In Locations.

### Classifications
    **Configuration**
    =================
    * Added Clasificaciones / Manager Group To Give User Access limits.
* Added Module.

### Configuration

* Added Two Fields.
* Fields To Track - To Track Fields Which is set.
* Send Mail To - Mail for Product Information.

### Account Credit Notes

* to implement the functionality of Marvelsa Wallet, which is at partner level configration to identify the type of wallet.
* If a Partner Wallet type is marvel wallet, then only this functionality will be visible.