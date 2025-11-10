from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    forecast_line_id = fields.Many2one(
        'forecast.report.line',
        string="Forecast Line",
        ondelete='set null',
    )

    is_forecast_po = fields.Boolean(
        string="Created from On Screen Forecast Report",
        help="Indicates that this Purchase Order was generated from the Forecast Wizard.",
        default=False,
        copy=False
    )
