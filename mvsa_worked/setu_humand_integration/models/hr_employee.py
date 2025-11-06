# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import requests
import json
import logging

_logger = logging.getLogger("Setu_Humand_Integration")


class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"

    is_need_to_create_humand_employee = fields.Boolean(string= 'Is Need To Create Humand Employee', help='need to create humand employee if value is False', copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 19/02/25
            Task: Migration to v18 from v16
            Purpose: To create employee account into humand when creates an employee in odoo.
        """
        employees = super(HrEmployeePrivate, self).create(vals_list)
        for employee in employees:
            employee.create_employee_to_humand()
        return employees

    def archive_employee_to_humand(self, humand_access_token, employeeInternalId):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 19/02/25
            Task: Migration to v18 from v16
            Purpose: To archive employee account into humand.
        """
        url = "https://api-prod.humand.co/public/api/v1/users/"
        headers = {
            'accept': 'application/json',
            'Authorization': humand_access_token
        }
        response_employeeInternalId = requests.request("GET",
                                                       url + employeeInternalId,
                                                       headers=headers, data={})
        if not response_employeeInternalId:
            if response_employeeInternalId.status_code == 400:
                _logger.info('The provided data is invalid')
            elif response_employeeInternalId.status_code == 401:
                _logger.info(f'Invalid Access Token')
            elif response_employeeInternalId.status_code == 404:
                _logger.info(f'Users not found for given usernames {self.name}')
            else:
                _logger.info(f"Can't Update Humand Employee Account Because {response_employeeInternalId.status_code}.")
        if response_employeeInternalId.status_code in [200, 201]:
            url = f"https://api-prod.humand.co/public/api/v1/users/{employeeInternalId}/deactivate"
            try:
                response = requests.request("POST", url, headers=headers, data={})
            except:
                if response.status_code == 401:
                    _logger.info('Invalid Access Token')
                elif response.status_code == 500:
                    _logger.info('An unexpected error has occurred')
                else:
                    _logger.info(f"Can't Update Humand Employee Account Because {response.status_code}.")
            if response.status_code in [200, 201, 204]:
                _logger.info(f"The User {self.name} Is Deactivated into Humand.")
                self.message_post(body=_(f"The User {self.name} Is Deactivated into Humand."))

    def action_archive(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 19/02/25
            Task: Migration to v18 from v16
            Purpose: To archive employee account into humand.
        """
        res = super(HrEmployeePrivate, self).action_archive()
        for employee_id in self:
            employeeInternalId = employee_id.work_email
            humand_access_token = self.env.company.humand_access_token
            if employeeInternalId and humand_access_token:
                employee_id.archive_employee_to_humand(humand_access_token,employeeInternalId)
        return res

    def create_employee_to_humand(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 19/02/25
            Task: Migration to v18 from v16
            Purpose: To create employee account into humand.
            add_modification: is_need_to_create_humand_employee write value true if employee created in humand
        """
        humand_access_token = self.env.company.humand_access_token or ""
        password = self.env.company.humand_default_password or ""
        relationships_employeeInternalId = self.parent_id.work_email or ""
        email = employeeInternalId = self.work_email or ""
        firstName = self.empleado_nombre or ""
        lastName = (self.empleado_paterno or "") + " " + (self.empleado_materno or "")
        hiringDate = self.incom_date or False
        birthdate = self.birthday or False
        response = {}
        response_employeeInternalId = {}
        response_relationships_employeeInternalId = {}
        if employeeInternalId or relationships_employeeInternalId:
            url = "https://api-prod.humand.co/public/api/v1/users/"
            headers = {
                'accept': 'application/json',
                'Authorization': humand_access_token
            }
            if employeeInternalId:
                response_employeeInternalId = requests.request("GET", url + employeeInternalId, headers=headers,
                                                               data={})
                if response_employeeInternalId.status_code in [200, 201]:
                    humand_employee = response_employeeInternalId.json()
                    self.is_need_to_create_humand_employee = True
                    _logger.info(f"User Exists with ID. {humand_employee.get('id', 0)}")
            if relationships_employeeInternalId:
                response_relationships_employeeInternalId = requests.request("GET",
                                                                             url + relationships_employeeInternalId,
                                                                             headers=headers, data={})
                if not response_relationships_employeeInternalId:
                    if response_employeeInternalId.status_code == 400:
                        _logger.info('The provided data is invalid')
                    elif response_employeeInternalId.status_code == 401:
                        _logger.info(f'Invalid Access Token')
                    elif response_employeeInternalId.status_code == 404:
                        _logger.info(f'Users not found for given usernames {self.parent_id.name}')

        if all([humand_access_token, password, relationships_employeeInternalId, email, employeeInternalId, firstName,
                lastName]) and not response_employeeInternalId and response_relationships_employeeInternalId:
            _logger.info(f"Creating Humand Employee Account.")
            url = "https://api-prod.humand.co/public/api/v1/users"
            payload = json.dumps({
                "password": password,
                "relationships": [
                    {
                        "name": "BOSS",
                        "employeeInternalId": relationships_employeeInternalId
                    }
                ],
                "employeeInternalId": employeeInternalId,
                "email": email,
                "firstName": firstName,
                "lastName": lastName,
                "hiringDate": str(hiringDate),
                "birthdate": str(birthdate)
            })
            headers = {
                'accept': 'application/json',
                'Authorization': humand_access_token,
                'Content-Type': 'application/json'
            }
            try:
                response = requests.request("POST", url, headers=headers, data=payload)
            except:
                if response.status_code == 400:
                    _logger.info('The provided data is invalid')
                    self.message_post(body=_(f"Can't Create Humand Employee Account."))
                elif response.status_code == 401:
                    _logger.info(f'Invalid Access Token')
                    self.message_post(body=_(f"Can't Create Humand Employee Account."))
                else:
                    _logger.info(f"Can't Create Humand Employee Account Because {response.status_code}.")
                    self.message_post(body=_(f"Can't Create Humand Employee Account."))
            if response.status_code in [200, 201]:
                humand_employee = response.json()
                self.is_need_to_create_humand_employee = True
                _logger.info(f"Created Humand Employee Account With ID {humand_employee.get('id', 0)}.")
                self.message_post(body=_(f"Created Humand Employee Account With ID {humand_employee.get('id', 0)}."))
        else:
            if not relationships_employeeInternalId:
                _logger.info(
                    f"Can't Create Humand Employee Account Because There Is Work Email missing In {self.parent_id.name}.")
            if not humand_access_token:
                _logger.info(
                    "Can't Create Humand Employee Account Because There Is No Access Token.")
            if not password:
                _logger.info(
                    "Can't Create Humand Employee Account Because There Is No Default Password.")
            if not all([email, employeeInternalId, firstName, lastName]):
                _logger.info(
                    "Can't Create Humand Employee Account Because There Is Something missing In Employee Information.")
