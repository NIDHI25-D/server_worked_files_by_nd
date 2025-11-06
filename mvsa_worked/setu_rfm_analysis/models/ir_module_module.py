# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
#import os
#import pkg_resources
#import shutil
#import tempfile
#import threading
#import zipfile

#import requests
#import werkzeug.urls

#from docutils import nodes
#from docutils.core import publish_string
#from docutils.transforms import Transform, writer_aux

#from docutils.writers.html4css1 import Writer
#import lxml.html
#import psycopg2

#import odoo
from odoo import api, fields, models, modules, tools, _
#from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
#from odoo.exceptions import AccessDenied, UserError
#from odoo.osv import expression
#from odoo.tools.parse_version import parse_version
#from odoo.tools.misc import topological_sort
#from odoo.http import request
from odoo.addons.base.models.ir_module import assert_log_admin_access

_logger = logging.getLogger(__name__)




class Module(models.Model):
    _inherit = "ir.module.module"

    @assert_log_admin_access
    @api.model
    def update_list_setu_rfm_analysis(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : to check for the existence of a specific Odoo module, update its information, and handle its
        dependencies, exclusions, and categorization
        """
        mod_name = 'setu_rfm_analysis_extended'
        mod = self.env['ir.module.module'].sudo().search(
            [('name', '=', mod_name)],
            limit=1)
        res = [0, 0]
        default_version = modules.adapt_version('1.0')
        terp = self.sudo().get_module_info(mod_name)
        values = self.sudo().get_values_from_terp(terp)
        skip = False
        if not mod:
            mod_path = modules.get_module_path(mod_name)
            if not mod_path or not terp:
                skip = True
                pass
            else:
                state = "uninstalled" if terp.get('installable', True) else "uninstallable"
                mod = self.sudo().create(dict(name=mod_name, state=state, **values))
                res[1] += 1

        if not skip:
            _logger.info("===========2=============")
            mod._update_dependencies(terp.get('depends', []), terp.get('auto_install'))
            _logger.info("===========3=============")
            mod._update_exclusions(terp.get('excludes', []))
            _logger.info("===========4=============")
            mod._update_category(terp.get('category', 'Uncategorized'))
            _logger.info("===========5=============")
            _logger.info("===========Final=============")
            updated, added = self.env['ir.module.module'].update_list()
        return res
