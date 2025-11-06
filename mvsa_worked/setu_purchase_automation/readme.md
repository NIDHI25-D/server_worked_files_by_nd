setu_purchase_automation
----------------------------------------
##### USAGE

* This module initiates the feature of automation of the purchase.
* This module are use for multiple usages, the functionality of this module are as follow.
* there are the button **Associate Purchase Order** in the account bank statement line to clicked on this button opened a wizard and from the wizard shown an option to added the PO for this statement line and if the amount of the PO or we can say total signed field value's sum in the purchase order tab are extended then the Amount then given an validation error else reduce this amount from the po.
* this statement line are also reflected to those respected PO which is set to the line in the tab **Related Statement** in purchase order with the details :
  * Statement, 
  * Date, 
  * Label, 
  * Partner,
  * Po Total Signed 
  * Amount
* there are the various fields are added to the purchase order under the tab **other information** and from those fields there are the automation of the state of the field **Purchase Status** 
* there are various values of the field Purchase Status i.e - In Production, Purchase Order Ready, In Transit, In Custom Clearance, Dispatched, Collected, In Yard, Counting, Received, Waiting For Expenses, Finalized purchase Order, On Hold, Canceled etc. and from the different condition those states are changed. 
* there are various menus are included under the configuration od the purchase order i.e - Custom Agency, Discharge ports, Loading ports, Forwarder, Carriers, and those records are reflected to the dropdown of the fields in purchase order. 

##### CONFIGURATION

* there are the following configuration in the **order** section in the **purchase** tab in the **settings**
* **Expected Arrival Date Automation**
  *  to auto set the Expected Arrival from ETD Date added the days of these.
* there are one cron/scheduled action are included **Henco Api Data**
* there are automatic set the values of fields in purchase order from the Henco url which are set to the Henco API in configuration, there are fields are set from henco are like:
  * Merchandise Ready Date,
  * Vessel,
  * ETD Date,
  * ATD Date,
  * ETA Date,
  * ATA Date,
  * Freight Cost,
  * Container Number,
  * Voyage
* there are Company, CustomerNum, LineType and Level are available in the configuration this values are use to the request data from the Henco API.
* there are the x-api-key field are available in the configuration this value are use to the header for the Henco API.
* there are Henco Username and Henco Password which are gives as an user name and password in the Henco API.
