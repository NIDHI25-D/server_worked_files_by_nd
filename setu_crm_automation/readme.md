Setu Crm Automation
-------------------
##### USAGE

* This module is mainly related to the CRM records.
* This module is used to not directly allow, users to change the state of CRM orders.
* This module also includes a cron named : **Change State Of Opportunity**
* This cron, archives the Pipeline records with Lost state, which are in new state with the Lost reason : **Final del Periodo**
* When Order of CRM are confirmed then stage is changed to **Proposition**.
* This module, changes the stage to **Shipped** and **Won** stage as per the fulfillments of the dates : **Shipping Date** and **X Studio Fecha De Entrega** in respected Transfers.

##### CONFIGURATION
* To allow user to manually change the states of CRM, need to give rigths to particular users.
  *     Settings  >  Users > Enable to change CRM Lead stage manually
* If user, doesn't want to allow user to change the state manually than disable the right for user and add the message in Settings.
  *     Settings > CRM > Message
* This message will be appeared as an Alert when the user tries to change the state without the rights.

