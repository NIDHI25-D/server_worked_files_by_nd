Setu Warehouse Transaction Authorization
-----------------------------

### USAGE

* This module is used to give restrictions to see the information and department wise applications, jobs and other
  functionality related to hr.

### Hr Applicant

* Added Some record rules to the model.
* create an applicant with conditions that contract_signed member matches the count of required
    employee then it will show respected Validation error while creation of applicant.
  
* write an applicant with conditions that if a contract_signed member matches the count
    of required employee, then it will show respected Validation error while creation of applicant.

### Hr Employee

* get departments from the menu.

### hr department

* Added Some record rules to the model.

### Hr Recruitment Stage

* Added Additional field department_ids to Hr Recruitment Stage.
* if adding the department into department_ids, then it does not have to contain
    any applications if it has then it will give earning.

### Hr Job

* Added Some record rules to the model.
* Added Additional fields Open Date and Close Date to jobs.
* Upon This it will handel the publication of jobs.
* for hr job, when all the employees are fulfilled as per the required
    candidates, then it will give validation error respectively if the user enables the toggle button.
  
* give close date with the conditions that when the last applicant assigned in the
    status: contract signed that date will be assigned in the field of close date and is_published toggle
    will be close and a message in chatter will be added.
