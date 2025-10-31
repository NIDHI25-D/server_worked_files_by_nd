MercadoPago Payment Acquirer
----------------------------------------
##### USAGE
* This module facilitates Mercado Pago payment processing within Odoo. 
* It provides an inline form view for adding payment details in Odoo.
* The system will register a customer if they are not already in Mercado Pago. 
* If the customer is already registered, it will use their existing information to create a payment in mercado pago. 
* Additionally, it offers payment installments through Mercado Pago. 
* The minimum payment amount is 5 MXN, while the maximum is 200,000 MXN.
* If the card issuer is 'American Express,' then Mercado Pago will apply additional charges.
* This module, includes a cron(scheduled action) named : **MercadoPago Payment transaction status check and update**.


##### CONFIGURATION
*       Sales -> Configuration -> Payment Providers -> Mercado Pago
* add these fields values :
  * MercadoPago Public key
  * MercadoPago Access token
* Enable Monthly Installments if you want to activate it. 
* Configure the price list and months as needed.
