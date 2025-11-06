Setu Prioritization Of Pickings
-------------------------

##### USAGE
* This module is used to prioritize the pickings in a single line for each warehouse based on priority levels.
* Line complexity and importance levels. This module form a consecutive for assigning pickings to the assortment teams automatically.
* **Problems** - the order in which pickings are assigned to the assortment teams depends on one person, which means that sometimes pickings of lesser importance, or that are very extensive or complex, are assigned to the assortment teams, causing delays in shipments of high importance.
* **Solution** - Create an algorithm to prioritize the pickings in a single line for each warehouse based on priority levels, line complexity and importance levels. This algorithm should form a consecutive for assigning pickings to the assortment teams automatically.
* There are a menu called **Prioritization of Pickings** and under this menu there are various options and configurations are available which are helps to pickings prioritization.
* Other options for use in pickings prioritization are :
* **Complexity Levels** - it is use to creates a levels for complexity of the pickings between range of **Initial range of lines** and **End range of lines**
* Here are the **Assortment team** and **Assortment team types** are define under and the menu **Assortment** there are a form a consecutive for assigning pickings to the assortment teams via executing a cron which is **Prioritization Of picking**
* Here are the **Priority Rules** where creates/set a records of Transfer Domain which matches a respective pickings and in this pickings there are a Prioritization Priority are set as per the priority of the rule, if there are a no rule are apply then No rule are set to the respective picking.
* Here from the **Complexity Assortment Team Types** of the Assortment Team Types if there are a **Pending Transfers** of there respective Complexity Level so in a queue single picking are set the values of **Assortment Team**,**Prioritization Priority**, **Complexity Assigned**,**Responsible Person** and remove these transfer from the Pending Transfers.
* There are a separate menu are available for the **Prioritization Priorities** under the **Inventory** where only Prioritization pickings are shown as a grouping of Prioritization Priority.  
