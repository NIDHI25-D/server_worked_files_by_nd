Setu Ecommerce Checkout Extended
----------------------------------------
##### USAGE

* This module are mainly use for Ecommerce based functionality and the portal side functionality.
* This module includes RAM registration related changes.
* Here are the scheduled action - **Check Contacts** which is used to inactive the contacts and corresponding to it's user if it's category are set as per the **Category** in **Settings** and this not any sale order are creating by those contact within seven working days.
* Here customise the Edit information action from the portal side and customise it step wise where **Account Information**, **The Company Information**, **Billing Information** and **Shipping Address** are included.
* Step 1 is **Account Information** In **Account Information** there are basic details are formed i.e - Name, Email Telephone.
* Step 2 is **Company Information** In **Company Information** first it asked to **Did You Required an invoice** option if checked it so filled out following details.
  * Fiscal Position:
  * Use Of CFDI: 
  * Payment Way:
  * Company type: 
  * RFC :
  * Company Name:
* Here if RFC are matches with other company so there are a message are displayed to **This RFC and related company already exists in our portal,  Click here for request connection.** and from this user can request with this connection and from these user Email are sent to the company which has registered with these RFC and if the company are approved those connection then user has rights of those company else reject then not.
* Step 3 is **Billing Information** In **Billing Information** there are a Billing Details are displayed as followed.
  * RFC :
  * Company Name:
  * Postal Code:
  * Street And Number:
  * Street #2:
  * City:
  * Colony:
  * Country:
  * State:
* Here from Postal Code: if it matches with the Country, Colony and City so it automatically takes from the Postal Code
* Step 4 is **Shipping Address** In **Shipping Address** there are a default address are displayed of the contact and here provides an add address option which allows to another address.
* Here at the top there are an **Add A Contact** and **Edit button** visible only if **Did You Required an invoice** value are checked at the **Company Information**
* From **Edit button** edit a Name and Permission of the user like,
  * Budgets
  * Sale Orders
  * Purchase Orders
  * Invoices
  * Claims
  * Consume the global points of the master company
  * Set As Admin User 
* From **Add A Contact** It allows to creates a new Contact and corresponding to it's user from Add A Contact button.
* After creating a Contact from Add A Contact it visible the created contact at Manage Contacts screen till then there are displayed **Currently there are not any contacts available.**
* And also created contact are displayed there as a table with the values contact name as a Member, given rights as a Permits, if login this user so it's Last Login and Edit and Delete option are available as Edit / Delete.
* If contacts are created from Add A Contact then at portal side there are a **Contacts** button are visible with counts of created contacts and on clicking of this, it shows a list of those contacts as a table. 
* At Portal there are a **Attach your Fiscal situation certificate.** option are available where add a Fiscal situation certificate and which displayed at the message of corresponding to these contact.



