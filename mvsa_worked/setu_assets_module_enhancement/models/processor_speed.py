from odoo import fields, models


class ProcessorSpeed(models.Model):
    _name = 'processor.speed'
    _description = 'Processor Speed'

    name = fields.Char()
