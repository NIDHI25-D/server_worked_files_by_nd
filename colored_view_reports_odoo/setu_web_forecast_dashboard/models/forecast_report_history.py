from odoo import models, fields, api, _


class ForecastReportHistory(models.Model):
    _name = "forecast.report.history"
    _description = "Forecast Report History"
    _order = "run_date desc"

    name = fields.Char(string="Report Name", required=True, default="Forecast History")
    run_date = fields.Datetime(string="History Date", default=fields.Datetime.now)
    line_ids = fields.One2many('forecast.report.line', 'history_id', string="Forecast Lines")

    # Add fields for wizard inputs
    history_forecast_type = fields.Selection([
        ('inbound', 'Inbound'),
        ('reordering', 'Reordering'),
        ('shipping', 'Shipping')
    ], string="Forecast Type")
    history_region = fields.Selection(
        selection=[('us', 'US'), ('uk', 'UK')],
        string='Region',
    )
    history_periods_ids = fields.Many2many(
        comodel_name='forecast.days.config',
        string='Periods',
    )
    history_is_exclude_oos_days = fields.Boolean(string='Include OOS Days')

    history_product_status_filter_ids = fields.Many2many(
        comodel_name='forecast.product.status.export',
        string='Product Status',
    )

    history_amazon_product_status_filter_ids = fields.Many2many(
        comodel_name='forecast.product.amz.status.export',
        string='Amazon Product Status',
    )
    history_filters_ids = fields.One2many(
        comodel_name='forecast.export.filter',
        inverse_name='history_id',
        string='Apply Filter by:',
    )

    history_use_constant_lead_time = fields.Boolean(string='Use constant Reorder up to DOI')
    history_delivery_lead_time = fields.Integer(string='Reorder up to')
    history_purchase_order_based_on_doi_id = fields.Many2one(
        comodel_name='forecast.days.config',
        string='Purchase Order Based On Doi',
        help='Select one period to use for the Purchase Order.',
    )

    def action_view_history_lines(self):
        """Open the forecast report lines related to this history in a new window"""
        self.ensure_one()
        triggered_lines = self.env['forecast.report.line'].search([
            ('history_id', '=', self.id),
            ('is_trigger_applied', '=', True)
        ])
        return {
            'name': _('Forecast Report Lines - %s' % self.name),
            'type': 'ir.actions.act_window',
            'res_model': 'forecast.report.line',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', triggered_lines.ids)],
            # 'domain': [('history_id', '=', self.id)],
            'target': 'current',
        }
