# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Import Supplier Invoice from XML',
    'summary': 'Create multiple Invoices from XML',
    'version': '18.0.0.0',
    'category': 'Localization/Mexico',
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://setuconsulting.com/',
    'depends': [
        'l10n_mx_edi',
        'setu_l10n_mx_edi_extended'
    ],
    'license': 'LGPL-3',
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        # 'views/assets.xml',
        # 'views/account_invoice_view.xml',
        'wizards/attach_xmls_wizard_view.xml',
    ],
    'demo': [
        'demo/ir_attachment.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'l10n_mx_edi_vendor_bills/static/src/css/style.css',
            'l10n_mx_edi_vendor_bills/static/src/xml/attach_xmls_template.xml',
            'l10n_mx_edi_vendor_bills/static/src/js/attach_xml.js'

        ]
    },
    'installable': True,
}
