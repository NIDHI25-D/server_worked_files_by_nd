# -*- coding: utf-8 -*-
import logging
import werkzeug.urls
from werkzeug.exceptions import BadRequest
from odoo import http
from odoo.http import request

from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.home import ensure_db

_logger = logging.getLogger(__name__)


class PasswordSecurityHome(AuthSignupHome):
    def do_signup(self, qcontext):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 31/01/2025
        Task: Password Security
        Purpose: This method will used to check some regular expression for password based on configuration
        :param qcontext:
        :return:
        """
        password = qcontext.get("password")
        # TASK : Error in resetting a previously used password https://app.clickup.com/t/86dxhp2mr
        # user = request.env.user -- This part is comment as it used to take public user res.user(4)
        user = request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))], limit=1)
        if not user:
            user = request.env.user
        user._check_password(password)
        return super(PasswordSecurityHome, self).do_signup(qcontext)

    @http.route()
    def web_login(self, *args, **kw):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 30/01/2025
        Task: Password Security
        Purpose: This method will used to check password expire or not if password expire then session logout 
        :param args:
        :param kw:
        :return: signup url
        """
        ensure_db()
        response = super(PasswordSecurityHome, self).web_login(*args, **kw)
        if not request.params.get("login_success"):
            return response
        if not request.env.user:
            return response
        # Now, I'm an authenticated user
        if not request.env.user._password_has_expired():
            return response
        # My password is expired, kick me out
        request.env.user.action_expire_password()
        request.session.logout(keep_db=True)
        partner = request.env.user.partner_id
        signup_url = partner._get_signup_url()
        request.params["login_success"] = False
        redirect = signup_url
        return request.redirect(redirect)

    @http.route()
    def web_auth_signup(self, *args, **kw):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 31/01/2025
        Task: Password Security
        Purpose: Try to catch all the possible exceptions not already handled in the parent method
        :return:
        """
        try:
            qcontext = self.get_auth_signup_qcontext()
        except Exception:
            raise BadRequest from None  # HTTPError: 400 Client Error: BAD REQUEST

        try:
            return super(PasswordSecurityHome, self).web_auth_signup(*args, **kw)
        except Exception as e:
            # Here we catch any generic exception since UserError is already
            # handled in parent method web_auth_signup()
            qcontext["error"] = str(e)
            response = request.render("auth_signup.signup", qcontext)
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
            response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
            return response

    @http.route('/password/company_policy', type='json', auth='public', website=True)
    def company_policy(self):
        company = request.env.user.company_id if request.env.user else request.env['res.company'].sudo().search([],
                                                                                                                limit=1)
        return {
            "password_lower": company.password_lower or 0,
            "password_upper": company.password_upper or 0,
            "password_numeric": company.password_numeric or 0,
            "password_special": company.password_special or 0,
            "password_minlength":int(request.env["ir.config_parameter"].sudo().get_param("auth_password_policy.minlength", default=0))
        }
