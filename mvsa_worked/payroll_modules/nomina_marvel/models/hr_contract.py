# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class Contract(models.Model):
    _inherit = "hr.contract"

    sueldo_diario_real = fields.Float('Sueldo diario real')
    seguro_gmm = fields.Float('Seguro GMM')
    seguro_gmm_monto = fields.Float('Seguro GMM monto')
