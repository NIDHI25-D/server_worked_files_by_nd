from odoo import models, fields, api, _


class vendor_charge_status(models.Model):
    """ Model for claim stages. This models the main stages of a claim
        management flow. Main CRM objects (leads, opportunities, project
        issues, ...) will now use only stages, instead of state and stages.
        Stages are for example used to display the kanban view of records.
    """
    _name = "vendor.charge.status"
    _description = "Vendor charge status"

    name = fields.Char('Status Name', required=True, translate=True)
