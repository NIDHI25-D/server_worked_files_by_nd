from odoo import models,fields


class JobQueues(models.Model):
    _inherit = "queue.job"

    delete_mail_at_once = fields.Boolean(default=False)