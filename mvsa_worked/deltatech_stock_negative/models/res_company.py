# ©  2008-2021 Deltatech
# See README.rst file on addons root folder for license details
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    no_negative_stock = fields.Boolean(
        string="No negative stock", default=True, help="Allows you to prohibit negative stock quantities."
    )
