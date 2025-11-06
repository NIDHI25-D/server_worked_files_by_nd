from odoo import models
import base64


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        """
        Author: jay.garach@setuconsulting.com
        Date: 10/02/25
        Task: Migration from V16 to V18 (https://app.clickup.com/t/865cy10mq?comment=90080049179749)
        Purpose: To Post message for The Responsive Letter in chatter.
        """
        res = super()._render_qweb_pdf(report_ref, res_ids, data)
        if self._get_report(report_ref).report_name == 'asset_extended.responsive_letter':
            model = self.env['hr.employee'].browse(res_ids)
            body = f'The Responsive Letter Downloaded by {self.env.user.name}'
            attachment = self.env['ir.attachment'].create({
                'name': 'ResponsiveLetter.pdf',
                'type': 'binary',
                'datas': base64.b64encode(res[0]),
                'mimetype': 'application/pdf',
                'res_model': 'hr.employee',
            })
            model.message_post(body=body, attachment_ids=[attachment.id])
        return res
