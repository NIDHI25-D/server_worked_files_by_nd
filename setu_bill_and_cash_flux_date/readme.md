Setu Bill And Cash Flux Date
-----------------------------

### USAGE

* Implemented To Creating the Vendor Bill Dynamically Upon Bill Type, Payment term, Partner Category and purchase
  payments configuration.

### Purchase Order

* Creating the vendor bill upon purchase payments of payment term Upon the partner tags if the Enable for create bill is
  true then only it will create Bills.
* filtering the bill types that are going to create the vendor bills.
* creating the vendor bill for whose currency is same and create bill draft is set to true.
* after that vendor tax bill for whose tax type is set to true.
* it only creates a vendor tax bill if not created with the same bill type.
* Updating the Invoice Due Date Upon some Conditions.
* Conditions Have to match as follows.
* If the date updated in PO is mentioned in the payment term, and also a bill type is the same,and its invoice is in
  draft state.

### Bill

* added some additional fields.

### Partner Tags

* added some additional fields.

### Payment Term

* added some additional fields.
* You have to configure the purchase payment by adding a bill type, Date Type, Operation Type, Reference, Days to
  Operate into Bill that are created.

### Bill Type

* Creating Bill Type To Create Dynamic Bills.

### Purchase Payment

* Creating Purchase Payment To Create Dynamic Vendor Bills.
* Into Payment Term have to create the Purchase Payment with configuration for dates to add or subtract days while
  creating dynamic bills for vendor purchase order.