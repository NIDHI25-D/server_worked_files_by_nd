from odoo import models, fields, api, _

class ExportForecastFilter(models.TransientModel):
    _inherit = 'forecast.export.filter'

    history_id = fields.Many2one(
        comodel_name='forecast.report.history',
        string='Forecast History',
        ondelete='cascade',  # important: delete filters automatically when history is deleted
    )
