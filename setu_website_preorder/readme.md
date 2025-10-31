Website Pre-Order
-------------------------

##### USAGE
* This module are mainly used for the Pre-order and Pre-sale, means if the product are not in stock still user are able to made it's sale or purchase.
* There are user feasible to creates,
  * National Pre-order
  * International Pre-order
  * Pre-sale
* There are separate menus are given to the all of these.
  - purchase --> pre-Order Request --> National Pre-Order Requests 
  - purchase --> pre-Order Request --> International Pre-Order Requests
  - purchase --> Pre-Sale Requests

* Condition to made product as a Pre-order is, the order are creating from the menu **National Pre-Order Requests if need to creates National Pre-Order else creating from International Pre-Order** and set quantity as needed and takes these order as a **Draft order** there are **Expected Arrival** are also takes in a consideration.
* Same procedure follow for International Pre-order.
* For Pre-sale order, creating a order from Pre-Sale Requests and confirm the order for those products and it's quantity, here **Expected Arrival** are also takes in a consideration, 
* For Pre-sale products it also needs to set the presale price, for the calculation of presale price there are two ways, 
  * it could done from particular order where **Presale Price Calculation** button are available to calculate price for only those products which are available in these order.
  * another way to calculate the presale price is there are a Scheduled action(Cron) name is - **Presale Price Update**
* If the order are created from given way then it was reflects as a preorder/presale at the website.
* There are a separate groups given for the products in website to filtered the products as **Instock Product**, **Presale Products**, **National Preorder Products**, **International Preorder Products**
* Here one more feature are available for the products at website side which is - **Next Day Shipping**, which is enable if **Next Day Shipping** are checked at product template side and it is visible only if product are not creating as any preorder or presale previously, so if **Next Day Shipping** are checked at product so it is available as **Next Day Shipping** at website, there are also Next Day Shipping group/filter available at website.
* Then in the product page at website there are user feasible to choose a product to Buy It as, as per the product's availability(From Stock - Standard delivery, As preorder, As presale, As International Preorder, As Next Day Shipping)
* There are a table which conditionality shows a total available quantity of stock, preorder, presale as per the product.
* There are **SKU** are also displayed of the product at the table and the stock are shows warehouse wise.
* There are text(description) are shown conditionality as filled up in the Pre-Sale Message for pre-sale and in International Pre-order Message for international preorder under the settings for national pre-order this text are fixed.
* After cart the product there are extend the product's description i.e - Stock Type(as per the chosen), it's Available, Price per product.
* After creating an order if confirm the sale order so it mean these quantity are reserved for those order so linked these order with it's corresponding order means if order are preorder type then linked with the those preorder in **Pre-order Details** and set Pre-ordered column as per the quantity buy, same fulfilled the Order Fulfilled as shown how many percent order are fulfilled.
* same flow are works for the pre-sale, if the order are creating as presale so, sale order are linked with these particular presale order at the **Pre-sale Details** and Pre-Sale column are set as per the buy quantity and Order Fulfilled are filled as per the order fulfillment.
  

##### CONFIGURATION
* There are an **Enable PreOrder** if it set then only allows to creates a preorder order for the products at website.
* There are an **Enable PreSale** if it set then only allows to creates a presale order for the products at website.
* There are an option - **Stock Warehouse** to choose at which warehouse stock needs to be considered, here an option to choose are - All, Specific, Several
* If here select All then by default all warehouses are consider, if select the Specific then specific one warehouse are allows to choose, if select Several then able to select more then one warehouses.
* Here are the Pre-sale Pricelist which is set to the sale order.
* Here are the Excluded Pricelist,which is excluded to allow to choose that pricelist and if both are same(sale order pricelist and Excluded Pricelist) then not allows and raise warning.
* Here are the **Cash Payment** which value are used to calculate the presale price.
* Here are the **Available Quantity Multiplier** and **Minimum Amount Quantity** which are used to calculate the **Calulated Quantity**
* Here are the **Configure Days for Calculation** here how much figure are set these consider as a days between these days Calulated Quantity are calculated.
* Here are the **International Preorder Pricelist** the uses of it is if order are international preorder type then these pricelist are set to these sale order.
* Here are two configurations for the Next Day Shipping - **Cash Next Day Specific Pricelist** and **Credit Next Day Specific Pricelist**, if the order are next day shipping and pricelist are not from them(Cash Next Day Specific Pricelist and Credit Next Day Specific Pricelist) so it gives an waring and not cart those quantities for these product.
* Here are the **Config Quantity** and **Activity User** which are use for national preorder notifications means if both of are set and quantity are exceed above the config quantity for any national preorder it sends a mail activity to the User which are set to the Activity User.
* Here are the **Enable Website sale orders cancellation** if it is checked then another one are visible which is **Time limit to cancel the orders (Hrs)** and between those hours which are set in Time limit to cancel the orders (Hrs) it is able to cancel the order from website feature.
* Here at the product level there are a Various things as configuration, i.e if the Minimum Quantity, Minimum Exclusivity Quantity and Delivery Estimated Time are set at the product then it reflects as a new table if product are international preorder type also not allows to lesser quantity if Minimum Quantity	is set and if **I want the Exclusivity of this product** is checked then not allows to lesser quantity then Minimum Exclusivity Quantity. 