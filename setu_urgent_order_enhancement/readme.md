Setu Urgent Order Enhancement
-----------------------------

### USAGE

* Use to Identify the sale order is urgent or not.

### Configuration

* Added urgent orders sales team ids into setting to set the sales team Urgent order. 
* Whichever the sales team is selected in configuration it will consider as urgent order.

### Partner
* Add Urgent order Field.

### Sale Order

* Add Urgent Order field.
* if sale order's customer or selected sales team store in the
  system parameter (Which are set from the settings-> sales -> Urgent Orders),
  then is_urgent_order field set to True automatically.
* After creating the sale order if a partner or sales team was changed,
  then is_urgent_order fields set automatically according to the setting.

### Sale Report

* Add Urgent order Field.
* To filter and group sale orders.

### Stock Pickings

* Add Urgent order Field.
* If sale orders is an urgent order, then it will be True.
