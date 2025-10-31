import odoo
from odoo import models, fields, api, http, _
import re
import os
from datetime import datetime, timedelta
from odoo.tools.misc import _format_time_ago
from odoo.http import request
from odoo.exceptions import UserError
import werkzeug
from odoo.addons.web.controllers.export import ExcelExport
import json
import base64

class login_log(models.Model):
    _name = 'login.log'
    _description = 'Login Log'
    _order = 'id desc'

    name = fields.Char('Name')
    user_id = fields.Many2one('res.users', 'User')
    user_agent = fields.Char('User Agent')
    browser = fields.Char('Browser')
    device = fields.Char('Device')
    os = fields.Char('OS')
    ip = fields.Char('IP')
    session_id = fields.Char('Session ID')
    login_date = fields.Datetime('Login Date')
    logout_date = fields.Datetime('Logged out Date')
    state = fields.Selection([('active','Active'),('close','Clossed')], string='Status')
    activity_log_ids = fields.One2many('activity.log', 'login_log_id', 'Activity Logs')
    # read_activity_log_ids = fields.One2many('activity.log', 'login_log_read_id', 'Read Activity Logs')
    country = fields.Char('Country')
    loc_state = fields.Char('State')
    city = fields.Char('City')
    url = fields.Char('URL', compute='_get_url')
    is_active = fields.Boolean('Is Active', compute='_get_is_active')
    timeout_date = fields.Datetime('Last Activity')

    def session_timeout_ah(self):
        config_parameter_obj = self.env['ir.config_parameter'].sudo()
        active_timeout = config_parameter_obj.get_param('advanced_session_management.session_timeout_active')

        if active_timeout == 'active':
            self.search([('state','=','active'),('timeout_date','<',datetime.now())]).logout_button()

        elif active_timeout == 'inactive':
            self.search([('timeout_date','<',datetime.now())]).logout_button()

    def dummy_btn(self):
        pass

    def _get_is_active(self):
        activity_log_obj = self.env['activity.log']
        for record in self:
            activity_time = activity_log_obj.search([('login_log_id','=',record.id)], order='id desc', limit=1).create_date
            if activity_time and record.state == 'active':
                record.is_active = (datetime.now() - activity_time) < timedelta(minutes=5)
            else:
                record.is_active = False

    def _get_url(self):
        self.url = '/web#id='+ str(self.id) +'&model=login.log&view_type=form'

    def location_lookup_ao(self):
        self.ensure_one()
        if self.ip:
            return {
                'type': 'ir.actions.act_url',
                'name': "Location",
                'target': 'new',
                'url': 'https://www.ip2location.com/demo/' + self.ip,
            }

    def logout_button(self):
        not_found = True
        db_name = ''
        config_parameter_obj = self.env['ir.config_parameter'].sudo()
        active_timeout = config_parameter_obj.get_param('advanced_session_management.session_timeout_active')
        for record in self:
            if record.state == 'active':
                # request.session.logout(keep_db=True)
                session_store = http.root.session_store
                get_session = session_store.get(record.session_id)
             
                if get_session.db and get_session.uid == record.user_id.id and get_session.sid == record.session_id:
                    # get_session.logout(keep_db=True)
                    session_store.delete(get_session)
                record.sudo().write({'state':'close','logout_date':datetime.now()})
            #     for fname in os.listdir(odoo.tools.config.session_dir):
            #         path = os.path.join(odoo.tools.config.session_dir, fname)
            #         name = re.split('_|\\.', fname)
            #         session_store = http.root.session_store
            #         get_session = session_store.get(name[0])
            #         get_session.logout(keep_db=True)
            #         os.unlink(path)
            #         if get_session.db and get_session.uid == record.user_id.id and get_session.sid == record.session_id:
            #             record.sudo().write({'state':'close','logout_date':datetime.now()})
            #             os.unlink(path)
            #             get_session.logout(keep_db=True)
            #             not_found = False
            #             if get_session.sid == request.session.sid:
            #                 db_name = get_session.db
            # if not_found:
            #     record.sudo().write({'state':'close','logout_date':datetime.now()})
        if db_name:
            return {
                    'type': 'ir.actions.act_url',
                    'target': 'self',
                    'url': '/web?db=' + db_name,
                }
        
    # def logout_button(self):
    #     not_found = True
    #     db_name = ''
        
    #     for record in self:
    #         if record.state == 'active':
    #             # request.session.logout(keep_db=True)
    #             session_store = http.root.session_store
    #             get_session = session_store.get(record.session_id)
    #             if get_session.db and get_session.uid == record.user_id.id and get_session.sid == record.session_id:
    #                 # get_session.logout(keep_db=True)
    #                 session_store.delete(get_session)
    #             record.sudo().write({'state':'close','logout_date':datetime.now()})
    #         #     for fname in os.listdir(odoo.tools.config.session_dir):
    #         #         path = os.path.join(odoo.tools.config.session_dir, fname)
    #         #         name = re.split('_|\\.', fname)
    #         #         session_store = http.root.session_store
    #         #         get_session = session_store.get(name[0])
    #         #         get_session.logout(keep_db=True)
    #         #         os.unlink(path)
    #         #         if get_session.db and get_session.uid == record.user_id.id and get_session.sid == record.session_id:
    #         #             record.sudo().write({'state':'close','logout_date':datetime.now()})
    #         #             os.unlink(path)
    #         #             get_session.logout(keep_db=True)
    #         #             not_found = False
    #         #             if get_session.sid == request.session.sid:
    #         #                 db_name = get_session.db
    #         # if not_found:
    #         #     record.sudo().write({'state':'close','logout_date':datetime.now()})
    #     if db_name:
    #         return {
    #                 'type': 'ir.actions.act_url',
    #                 'target': 'self',
    #                 'url': '/web?db=' + db_name,
    #             }

#    @api.model
    @api.model_create_multi
    def create(self, vals):
        # vals['name'] = str(self.env['res.users'].browse(vals['user_id']).name) + '/'  + str(vals['login_date'])[:10] + '/' + vals['browser'] + '/' + vals['device'] + '/' + '00' + str(self.env['ir.sequence'].sudo().next_by_code('login.log')) or _('New')
        res = super(login_log, self).create(vals)
        res.name = 'S00' + str(self.env['ir.sequence'].sudo().next_by_code('login.log')) or _('New')
        config_parameter_obj = self.env['ir.config_parameter']
        send_mail = config_parameter_obj.search([('key','=','advanced_session_management.send_mail')],limit=1)
        if send_mail.value == 'True' and res.user_id.has_group('advanced_session_management.group_login_log_user_ah'):
            template = self.env.ref('advanced_session_management.new_session_start_mail_template_ah', raise_if_not_found=False)
            if res and res.id and template:
                template.sudo().send_mail(res.id, force_send=True)
        return res 

    def unlink(self):
        for record in self:
            try:
                model = request.params['model']
            except:
                model = ''
            if record.user_id.id == self.env.user.id and model != 'base.module.uninstall':
                raise UserError(_("For the security purpose, you can't delete your own sessions and activities."))
            record.activity_log_ids.unlink()
            record.logout_button()
            
        return super(login_log, self).unlink()
    
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
                "fields": [{'name': 'login_log_id/name', 'label': 'Name', 'store': True, 'type': 'char'},
                           {'name': 'login_log_id/user_id/name', 'label': 'User', 'store': True, 'type': 'many2one'},
                           {'name': 'login_log_id/login_date', 'label': 'Login Date', 'store': True,
                            'type': 'datetime'},
                           {'name': 'login_log_id/device', 'label': 'Device', 'store': True, 'type': 'char'},
                           {'name': 'login_log_id/os', 'label': 'OS', 'store': True, 'type': 'char'},
                           {'name': 'login_log_id/browser', 'label': 'Browser', 'store': True, 'type': 'char'},

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
        response = excel.index(json.dumps(data))
        attachment_value = {
            'name': "activities",
            'datas': base64.encodebytes(response.data),
            'res_model': "audit.log",
            'mimetype': 'application/vnd.ms-excel'
        }
        attachment = request.env['ir.attachment'].sudo().create(attachment_value)
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
        self.search([('state','=','close'),('logout_date','<=',datetime.now() - timedelta(value))]).unlink()
        self.env['activity.log'].search([('create_date','<=',datetime.now() - timedelta(value))]).unlink()
        # for record in self.search([('state','=','close'),('logout_date','<=',datetime.now() - timedelta(value))]):
        #     record.unlink()
        # for record in self.env['activity.log'].search([('create_date','<=',datetime.now() - timedelta(value))]):
        #     record.unlink()
