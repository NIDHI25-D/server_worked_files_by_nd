from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.addons.web.controllers.export import ExcelExport
import json
import base64


class ResDeviceLog(models.Model):
    _inherit = 'res.device.log'


    activity_log_ids = fields.One2many('activity.log', 'device_id', 'Activity Logs')
    timeout_date = fields.Datetime('Last Activity')

    def session_timeout_ah(self):
        config_parameter_obj = self.env['ir.config_parameter'].sudo()
        active_timeout = config_parameter_obj.get_param('advanced_session_management.session_timeout_active')

        if active_timeout == 'active':
            self.sudo().search([('is_current','=', True),('timeout_date','<',datetime.now())])._revoke()

        elif active_timeout == 'inactive':
            self.search([('timeout_date','<',datetime.now())])._revoke()

    def remove_old_log(self):
        config_parameter_obj = self.env['ir.config_parameter']
        value = config_parameter_obj.search([('key','=','advanced_session_management.remove_sesions')],limit=1)
        if value and value.value:
            value = int(value.value)
        else:
            value = 7
        records = self.env['activity.log'].search([('create_date', '<=', datetime.now() - timedelta(value))])
        excel = ExcelExport()
        data = {"import_compat": False, "domain": [],
                "fields": [
                           {'name': 'device_id/display_name', 'label': 'Name', 'store': True, 'type': 'char'},
                           {'name': 'device_id/user_id/name', 'label': 'User', 'store': True, 'type': 'many2one'},
                           # {'name': 'device_id/login_date', 'label': 'Login Date', 'store': True,
                           #  'type': 'datetime'},
                           {'name': 'device_id/device_type', 'label': 'Device', 'store': True, 'type': 'char'},
                           # {'name': 'device_id/os', 'label': 'OS', 'store': True, 'type': 'char'},
                           {'name': 'device_id/browser', 'label': 'Browser', 'store': True, 'type': 'char'},

                           #  Activity from the session.
                           {'name': 'name', 'label': 'Record Name', 'store': True, 'type': 'char'},
                           {'name': 'user_id/name', 'label': 'User', 'store': True, 'type': 'many2one'},
                           {'name': 'model', 'label': 'Model', 'store': True, 'type': 'char'},
                           {'name': 'action', 'label': 'Action', 'store': True, 'type': 'selection'},
                           {'name': 'value', 'label': 'Changes', 'store': True, 'type': 'html'},

                           # Edited value from the activity of the session.
                           {'name': 'edit_value_ids/name', 'label': 'Edit name', 'store': True, 'type': 'char'},
                           {'name': 'edit_value_ids/new', 'label': 'New Changes', 'store': True, 'type': 'char'},
                           {'name': 'edit_value_ids/old', 'label': 'Old Changes', 'store': True, 'type': 'char'}],
                "groupby": [], "ids": records.ids, "model": "activity.log"}
        response = excel.web_export_xlsx(json.dumps(data))

        attachment_value = {
            'name': f'activities.xlsx',
            'datas': base64.encodebytes(response.data),
            'res_model': "audit.log",
            'mimetype': 'application/vnd.ms-excel'
        }
        attachment = self.env['ir.attachment'].sudo().create(attachment_value)
        user_id = self.env['ir.config_parameter'].sudo().get_param('advanced_session_management.audit_user')
        body = _("Deleted Activity Log File")

        mail_values = {
            'email_from': self.env.company.email,
            'email_to': user_id,
            # 'email_to': user_email if user_email else False,
            # 'recipient_ids': [user_email.partner_id.id],
            'subject': "Marvelsa Activity Log",
            'body_html': body,
            'attachment_ids': [(6, 0, attachment.ids)],
            'auto_delete': True,
        }
        mail = self.env['mail.mail'].create(mail_values)
        mail.sudo().send()
        self.sudo().search([('is_current','=',False),('last_activity','<=',datetime.now() - timedelta(value))]).unlink()
        self.env['activity.log'].search([('create_date','<=',datetime.now() - timedelta(value))]).unlink()


    def _update_device(self, request):
        pass
        res = super(ResDeviceLog, self)._update_device(request)
        trace = request.session.update_trace(request)
        if trace:
            pass

    def dummy_btn(self):
        pass