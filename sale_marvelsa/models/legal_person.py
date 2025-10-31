from odoo import fields, models


class LegalPerson(models.Model):
    _name = 'legal.person'
    _description = 'Legal Person in Contacts'

    name = fields.Char(string='Name', help='Enter the name of legal Person')
