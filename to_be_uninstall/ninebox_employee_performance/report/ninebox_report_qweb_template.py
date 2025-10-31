from odoo import api, fields, models

class ReportNinebox(models.AbstractModel):
    _name = 'report.ninebox_employee_performance.report_ninebox'
    _description = 'Ninebox Report as PDF.'

    @api.model
    def _get_report_values(self, docids, data=None):
        """
            Author: udit@setuconsulting
            Date: 01/02/23
            Task: Agrobolder migration
            Purpose: Prepare value for ninebox qweb template
        """
        data = dict(data or {})
        count_1x1 = 0
        count_1x2 = 0
        count_1x3 = 0

        count_2x1 = 0
        count_2x2 = 0
        count_2x3 = 0

        count_3x1 = 0
        count_3x2 = 0
        count_3x3 = 0
        docids = ''.join(docids)
        # review_period_id = self.env['review.period.timeline'].sudo().browse([
        #     ('assessment_period', '=', docids[0])])
        period = self._context.get('period')
        
        # docs = self.env['employee.performance.report'].sudo().search([('assessment_period', 'in', review_period_id.id)])
        docs = self.env['employee.performance.report'].sudo().search([('assessment_period', 'in',(self._context.get('period')))])
                                                                    
        for employee in docs:
            # 1x1 - 1x5
            if employee.pot_per_rate == '1_1':
                count_1x1 += 1
            
            if employee.pot_per_rate == '1_2':
                count_1x2 += 1
            
            if employee.pot_per_rate == '1_3':
                count_1x3 += 1
        
            # 2x1 - 2x5
            if employee.pot_per_rate == '2_1':
                count_2x1 += 1
            
            if employee.pot_per_rate == '2_2':
                count_2x2 += 1
                
            if employee.pot_per_rate == '2_3':
                count_2x3 += 1
            
            # 3x1 - 3x5
            if employee.pot_per_rate == '3_1':
                count_3x1 += 1

            if employee.pot_per_rate == '3_2':
                count_3x2 += 1

            if employee.pot_per_rate == '3_3':
                count_3x3 += 1
            
        data.update({
            'review_period' : period,
            
            'count_1x1' : count_1x1,
            'count_1x2' : count_1x2,
            'count_1x3' : count_1x3,

            'count_2x1' : count_2x1,
            'count_2x2' : count_2x2,
            'count_2x3' : count_2x3,

            'count_3x1' : count_3x1,
            'count_3x2' : count_3x2,
            'count_3x3' : count_3x3,
        })
        
        return {
            'doc_ids': docs.ids,
            'doc_model': 'employee.performance',
            'docs': docs,
            'data' : data,
        }