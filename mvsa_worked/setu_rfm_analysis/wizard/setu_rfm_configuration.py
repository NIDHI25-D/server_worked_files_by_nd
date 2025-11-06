from odoo import fields, models, api, tools
from odoo.modules.module import get_module_resource
import base64
import logging

_logger = logging.getLogger(__name__)


class ModelName(models.TransientModel):
    _name = 'setu.rfm.configuration'
    _description = 'Setu RFM Configuration'

    install_setu_rfm_analysis_extended = fields.Boolean(string="Enable PoS Sales")
    install_image = fields.Binary(
        string='Installation Image',
        default=lambda s: s._default_install_image()
    )

    @api.model
    def _default_install_image(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : it is intended to load a predefined image file from the module's static resources, encode it in base64 
        format, and return it
        """
        image_path = get_module_resource(
            'setu_rfm_analysis', 'static/src', 'install_pos_config2.png'
        )
        with open(image_path, 'rb') as handler:
            image_data = handler.read()
        return base64.encodebytes(image_data)

    @api.model
    def default_get(self, fields):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : allows to define default values for fields when a user is creating a new record
        """
        res = super(ModelName, self).default_get(fields)
        install_setu_rfm_analysis = self.env['ir.config_parameter'].sudo().get_param(
            'setu_rfm_analysis.install_setu_rfm_analysis_extended')
        if install_setu_rfm_analysis:
            res['install_setu_rfm_analysis_extended'] = True if install_setu_rfm_analysis == 'installed' else False
        return res

    def execute(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : the installation of an extended module related to the setu_rfm_analysis functionality
        """
        install_setu_rfm_analysis = self.sudo().env.ref('setu_rfm_analysis.install_setu_rfm_analysis_extended')
        self.unzip_and_install_extended_module(True, install_setu_rfm_analysis)
        self.env['ir.config_parameter'].set_param('setu_rfm_analysis.extended_module_in_registry', True)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def unzip_and_install_extended_module(self, state, install_setu_rfm_analysis):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : the installation and uninstallation of the extended module by handling the necessary file operations and 
        updating the module's status.
        """
        try:
            extended_rfm_analysis = self.env['ir.module.module'].sudo().search(
                [('name', '=', 'setu_rfm_analysis_extended')],
                limit=1)
            status = ''
            source_dir = __file__.replace('/wizard/setu_rfm_configuration.py',
                                          '/module/setu_rfm_analysis_extended.zip')
            target_dir = __file__.split('/setu_rfm_analysis/wizard/setu_rfm_configuration.py')[0]
            if not state and extended_rfm_analysis and extended_rfm_analysis.state == 'installed':
                status = 'uninstall'
            if state:
                if extended_rfm_analysis and extended_rfm_analysis.state != 'installed':
                    status = 'install'
                elif not extended_rfm_analysis:
                    import zipfile
                    with zipfile.ZipFile(source_dir, 'r') as zip_ref:
                        zip_ref.extractall(target_dir)
                    self.env['ir.module.module'].sudo().update_list_setu_rfm_analysis()
            return True
        except Exception as e:
            _logger.info("====================%s==================" % e)
            return False
