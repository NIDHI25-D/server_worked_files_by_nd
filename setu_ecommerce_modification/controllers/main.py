import uuid
import werkzeug
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home
from odoo.addons.auth_oauth.controllers.main import OAuthLogin
import logging

_logger = logging.getLogger("checking_values")
from odoo.tools.translate import _


class HomeExtended(Home):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        """
            Author: jay.garach@setuconsulting.com
            Date: 19/03/25
            Task: Migration from V16 to V18
            Purpose: Send an Email of new signup user
        """
        # # <!-- Below code is comment as recaptcha is done by default by the base  --> TASK : RESET TO PASSWORD
        # token = kw.get('g-recaptcha-response', '')
        # if request.httprequest.method == 'POST':
        #     private_key = request.env['ir.config_parameter'].sudo().get_param('recaptcha_private_key')
        #     message = False
        #     if not token and private_key:
        #         message = _("Suspicious activity detected by Google reCaptcha")
        #     request.params.update({'recaptcha_token_response': token})
        #     try:
        #         if token and not request.env['ir.http']._verify_request_recaptcha_token(False):
        #             message = _("Suspicious activity detected by Google reCaptcha")
        #             _logger.info(f"Suspicious activity detected by Google reCaptcha.-----------signup")
        #     except Exception as e:
        #         _logger.info(f"{e}-----------signup_error")
        #     if message:
        #         qcontext = self.get_auth_signup_qcontext()
        #         qcontext['error'] = message
        #         response = request.render('auth_signup.signup', qcontext)
        #         return response
        response = super(HomeExtended, self).web_auth_signup(*args, **kw)
        if not request.params:
            return response
        try:
            credential = {'login': request.params['login'], 'password': request.params['password'], 'type': 'password'}
            uid = request.session.authenticate(request.session.db, credential)
        except Exception:
            return response
        user_sudo = request.env['res.users'].sudo().search([('id', '=', uid.get('uid'))])
        if not user_sudo.has_group('base.group_portal'):
            return response
        # 1 ARCHIEVEDS RELATED PARTNERS 2->USERS ARCHIVEDS
        user_sudo.partner_id.verification_token = str(uuid.uuid4())
        try:
            request.env.ref('setu_ecommerce_modification.email_template_signup_verification').sudo(). \
                send_mail(user_sudo.id, force_send=True, raise_exception=True)
            request.session.logout(keep_db=True)
            token_link = '/web/verify/status/%s0hb1%s' % (
                user_sudo.partner_id.id, user_sudo.partner_id.verification_token)
            return werkzeug.utils.redirect(token_link, 303)
        except Exception:
            _logger.info(
                f"Mail server is not configured yet.")
            request.session.logout(keep_db=True)
            return request.redirect('/web/login')

    @http.route()
    def web_login(self, redirect=None, **kw):
        """
            Author: jay.garach@setuconsulting.com
            Date: 19/03/25
            Task: Migration from V16 to V18
            Purpose: redirect to verify your account
        """
        # <!-- Below code is comment as recaptcha is done by default by the base  -->  --> TASK : RESET TO PASSWORD
        # token = kw.get('g-recaptcha-response', '')
        # if request.httprequest.method == 'POST':
        #     message = False
        #     private_key = request.env['ir.config_parameter'].sudo().get_param('recaptcha_private_key')
        #     if not token and private_key:
        #         message = _("Suspicious activity detected by Google reCaptcha")
        #     request.params.update({'recaptcha_token_response': token})
        #     try:
        #         if token and not request.env['ir.http']._verify_request_recaptcha_token(False):
        #             message = _("Suspicious activity detected by Google reCaptcha")
        #             _logger.info(f"Suspicious activity detected by Google reCaptcha.-------------login")
        #     except Exception as e:
        #         _logger.info(f"{e}------------------------login_error")
        #     if message:
        #         values = request.params.copy()
        #         providers = OAuthLogin.list_providers(self)
        #         response = request.render('web.login', values)
        #         response.qcontext['providers'] = providers
        #         values['error'] = message
        #         return response
        #
        response = super(HomeExtended, self).web_login(redirect, **kw)

        try:
            credential = {'login': request.params['login'], 'password': request.params['password'], 'type': 'password'}
            uid = request.session.authenticate(request.session.db, credential)
        except Exception:
            return response

        user_sudo = request.env['res.users'].sudo().search([('id', '=', uid.get('uid'))])

        if not user_sudo.has_group('base.group_portal'):
            return response

        if not request.env.user._is_admin() and not user_sudo.partner_id.is_verified_partner:
            request.session.logout(keep_db=True)
            token_link = '/web/verify/status/%s0hb1%s' % (
                user_sudo.partner_id.id, user_sudo.partner_id.verification_token)
            return werkzeug.utils.redirect(token_link, 303)
        return super(HomeExtended, self).web_login(redirect, **kw)

    @http.route(['''/web/verify/<string:verify_token>'''], type="http", auth="public", website=True)
    def verify_partner(self, verify_token=False, **kwargs):
        """
            Author: jay.garach@setuconsulting.com
            Date: 19/03/25
            Task: Migration from V16 to V18
            Purpose: Verify the user and update the fields of partner
        """
        try:
            if verify_token:
                partner_id = verify_token.split("0hb1")[0]
                partner_token = verify_token.split("0hb1")[1]
                partner = request.env['res.partner'].sudo().search(
                    [('id', '=', partner_id), ('verification_token', '=', partner_token)])
                if partner:
                    partner.sudo().write({'is_verified_partner': True})

                    val = {
                        'status': True,
                        'partner': partner
                    }
                else:
                    val = {
                        'status': False,
                        'partner': partner
                    }

                return request.render("setu_ecommerce_modification.res_partner_verified", val)
        except Exception:
            return werkzeug.utils.redirect("/", 303)

    @http.route(['''/web/verify/status/<string:verify_token>'''], type="http", auth="public", website=True)
    def verify_partner_status(self, verify_token=False, **kwargs):
        """
            Author: jay.garach@setuconsulting.com
            Date: 19/03/25
            Task: Migration from V16 to V18
            Purpose: this check the status of the partner is verified or not
        """
        try:
            if verify_token:
                partner_id = verify_token.split("0hb1")[0]
                partner_token = verify_token.split("0hb1")[1]
                partner = request.env['res.partner'].sudo().search(
                    [('id', '=', partner_id), ('verification_token', '=', partner_token)])
                _logger.info(
                    f"{partner_id},{partner_token},{verify_token},{partner.name},{partner.id}{partner.is_verified_partner}")
                if partner.is_verified_partner:
                    val = {
                        'status': True,
                        'is_status_page': True,
                        'partner': partner
                    }
                else:
                    val = {
                        'status': False,
                        'is_status_page': True,
                        'partner': partner
                    }
                return request.render("setu_ecommerce_modification.res_partner_verified", val)
        except Exception:
            return werkzeug.utils.redirect("/", 303)
