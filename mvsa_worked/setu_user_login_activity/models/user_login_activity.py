from odoo import fields, models, api, _

class UserLoginActivity(models.Model):
    _name = 'user.login.activity'
    _description = 'User Login Activity'
    _order = 'login_time desc'

    user_id = fields.Many2one('res.users', string='Login User', default=lambda self: self.env.user)
    login_time = fields.Datetime('Login Time')
    user_ip_address = fields.Char('User IP Address')
    user_device = fields.Char('User Device')
