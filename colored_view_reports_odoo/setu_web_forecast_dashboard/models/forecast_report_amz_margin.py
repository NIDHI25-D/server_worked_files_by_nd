from odoo import models, fields,api

class ForecastReportAmzMargin(models.Model):
    _name = "forecast.report.amz.margin"
    _description="Forecast Report Amz Margin"
    _order = "forecast_report_date_amz_margin desc"


    forecast_report_date_amz_margin = fields.Date(string="AMZ Margin Date", default=fields.Date.today)
    amz_margin = fields.Float(string="AMZ Margin (%)")
    amz_margin_product_id = fields.Many2one('product.product', string="Product")
