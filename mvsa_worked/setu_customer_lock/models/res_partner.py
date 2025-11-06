from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_customer_locked = fields.Boolean("Locked Customers", compute="get_customer_locking_info", store=True)

    @api.constrains("category_id")
    def onchange_customer_tag(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 04/12/24
            Task: Migration to v18 from v16
            Purpose: If the category_id change in the contacts then it will set the lock value to the partner's is_customer_locked
        """
        for record in self:
            if record.category_id and record.category_id.filtered(lambda x: x.is_customer_lock_reason):
                if not self.env.user.has_group('setu_customer_lock.allow_customer_lock'):
                    raise UserError(_("No access right for set customer lock. \nPlease contact to your Administrator"))
            #     record.is_customer_locked = True
            # else:
            #     record.is_customer_locked = False

    @api.depends('category_id', 'category_id.is_customer_lock_reason')
    def get_customer_locking_info(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 04/12/24
            Task: Migration to v18 from v16
            Purpose: This computes method will check whether the customer is locked or not.
        """
        _logger.debug("Compute get_customer_locking_info method start")
        for record in self:
            if record.category_id and record.category_id.filtered(lambda x: x.is_customer_lock_reason):
                record.is_customer_locked = True
            else:
                record.is_customer_locked = False
        _logger.debug("Compute get_customer_locking_info method end")

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ['is_customer_locked']
        return params