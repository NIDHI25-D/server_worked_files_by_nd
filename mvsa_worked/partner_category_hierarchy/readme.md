Partner Category Hierarchy
-----------------------------

### USAGE

* Use of THis module is to create a hierarchy upon the customers/partners.
* we can manage a different price list according to the Partners.

### Product Prise List

* Added a default Price List.
* you cannot delete a default Price List.
* You cannot change a default price list sequence.
* Add domain in a price list id when quotation is created from sale. Order and CRM.

### Partners

* used in module website sale price list Visibility of Price lists is managed on Parent Category Used in module.
* set an allowed price list as per the hcateegory of partner.
* set an allowed price list as per the allowed price lists of partner.
* set an allowed price list as per the Extra Price list of partner.

### Partner HCategory

* This is a model that creates the partner and category regarding customer to manage the different types of price lists.
* Whenever the category will be having the same in parent_id, it will give error.
* Also set a Parent Category to inherit that's all prise lists.

### Sale Order

* Add a domain on a price list id as per the selected partner Whenever Partner will change it will pass domain.

### Website

* Added Domains to filter the price list according to the category and extra price list are set into the partners.
* Added monthly proposal price list id in allowed a price list for website.