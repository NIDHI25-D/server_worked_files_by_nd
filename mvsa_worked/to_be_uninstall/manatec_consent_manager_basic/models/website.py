# -*- coding: utf-8 -*-
"""
    Author: Konrad Sawade (konrad.sawade@manatec.de)
    Copyright: 2020, manaTec GmbH
    Date created: 21.08.2020
"""

import logging

from odoo import fields, models

logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = "website"

    privacy_policy_url = fields.Char('URL')
    cookie_domain = fields.Char('Cookie Domain', default=lambda x: x.domain)
