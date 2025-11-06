# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.http import request


class Website(models.Model):
    _inherit = 'website'

    def get_not_elegible_customer_error(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 04/12/24
            Task: Migration to v18 from v16
            Purpose: This method will send error message to the website page.
        """
        error = request.session.get('not_elegible_customer_error', False)
        if error:
            request.session.pop('not_elegible_customer_error')
        return error

    def check_not_elegible_customer_error_session(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 04/12/24
            Task: Migration to v18 from v16
            Purpose: This method will check whether need to show the error message or not.
        """
        return True if request.session.get('not_elegible_customer_error', False) else False

    def elegible_customer(self, current_user_partner):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 04/12/24
            Task: Migration to v18 from v16
            Purpose: This method will filter out whether the partner selected category_id is is_customer_lock_reason or not
        """

        not_eligible_partner = current_user_partner and current_user_partner.mapped('category_id').filtered(
            lambda x: x.is_customer_lock_reason) or False
        if not not_eligible_partner and current_user_partner and current_user_partner.email:
            customer_email = current_user_partner.email.strip().lower()
            not_eligible_partner = self.env['res.partner'].sudo().search([('email', '=', customer_email)]).mapped(
                'category_id').filtered(
                lambda x: x.is_customer_lock_reason) or False
        return not_eligible_partner
