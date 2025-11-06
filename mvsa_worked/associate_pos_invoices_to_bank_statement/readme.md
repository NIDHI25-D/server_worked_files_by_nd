Associate Pos Invoice TO Bank Statements
----------------------------------------
##### USAGE

* This module initiates the feature of including POS invoices in respected Bank Reconciliation.
* This module also includes the calculation of the Total Signed Amount such as :
    *     When an invoice is added, the related balance subtraction operation is
          carried out, so that the person relating the invoices can verify that the total
          amount of the statement corresponds to the amount of the added invoices.
* The total signed amount of POS Invoice added in the statement line is shown in the line. As well as that amount is
  being subtracted from the total amount and that is reflected in the Difference.
* The statement line added in the Bank Reconciliation will be added to the **Tab : Related Statement** of respected POS
  invoice with the details:
  *     Statement, 
  *     Date, 
  *     Label, 
  *     Partner,
  *     Total Signed Amount 
  *     Amount


