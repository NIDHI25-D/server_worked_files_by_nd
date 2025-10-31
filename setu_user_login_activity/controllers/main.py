from datetime import datetime, timedelta

import httpagentparser
import odoo.modules.registry
from odoo.http import request

import odoo
from odoo import http
from odoo.addons.web.controllers.utils import ensure_db
from odoo.addons.website.controllers.main import Website
CREDENTIAL_PARAMS = ['login', 'password', 'type']


class Home(Website):

    @http.route()
    def web_login(self, redirect=None, **kw):
        """
            Author: jay.garach@setuconsulting.com
            Date: 02/12/2024
            Task: Migration from V16 to V18
            Purpose: This method will collect the data of the system which is going to login in the give route
        """
        ensure_db()
        if not request.params:
            return super(Home, self).web_login(redirect, **kw)
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)
        if request.httprequest.method == 'POST':
            try:
                credential = {key: value for key, value in request.params.items() if key in CREDENTIAL_PARAMS and value}
                credential.setdefault('type', 'password')
                auth_info = request.session.authenticate(request.db, credential)
            except odoo.exceptions.AccessDenied as e:
                return super(Home, self).web_login(redirect=redirect, **kw)
            if auth_info is not False:
                previous_date = datetime.now().date() - timedelta(days=90)
                request._cr.execute("delete from user_login_activity where date(login_time)='%s'" % str(previous_date))
                agent = request.httprequest.environ.get('HTTP_USER_AGENT')
                agent_details = httpagentparser.detect(agent)
                user_os = agent_details['os']['name']
                browser_name = agent_details['browser']['name']
                ip_address = request.httprequest.environ['REMOTE_ADDR']
                request.env['user.login.activity'].sudo().create({'user_id': auth_info['uid'],
                                                                  'login_time': datetime.now().strftime(
                                                                      "%Y-%m-%d %H:%M:%S"),
                                                                  'user_ip_address': ip_address,
                                                                  'user_device': "%s - %s" % (user_os, browser_name)})
        return super(Home, self).web_login(redirect=redirect, **kw)
