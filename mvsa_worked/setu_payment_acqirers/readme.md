Payment Acquirer Extended
----------------------------------------
##### USAGE
* This module enables Installment for Stripe Payments
* If the Current Order Pricelist matches the Installment Plans Pricelist, then Installment Plans will be added for that order.
* After confirmation of sale order, latest charge of stripe added in sale order.

##### CONFIGURATION
*       Payment Providers -> Stripe -> Enable Monthly Installment
* Configure these fields:
  * Pricelist
  * Months
  * Minimum Amount
