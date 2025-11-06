from odoo import fields, models


class ProcessorGeneration(models.Model):
    _name = 'processor.generation'
    _description = 'Processor Generation'

    name = fields.Char()
