from odoo import fields, models


class ProcessorModel(models.Model):
    _name = 'processor.model'
    _description = 'Processor Model'

    name = fields.Char()
