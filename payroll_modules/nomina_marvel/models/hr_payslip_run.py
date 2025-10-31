# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    
    incidence_start = fields.Date(string=_('Inicio de incidencias'))
    incidence_end = fields.Date(string=_('Fin de incidencias'))
