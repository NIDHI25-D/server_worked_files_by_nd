{
    'name': 'EDI for Mexico Extended',
    'version': '18.0.0.0',
    'category': 'Accounting',
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com/',
    "license": "LGPL-3",
    'depends': ['l10n_mx_edi_extended', 'account_edi', 'setu_ecommerce_checkout_extended'],
    "data": [
        # "views/res_partner_ext.xml", --> no needed as removed from this module.
        "views/edi_document_view.xml",
        "views/product_template_view.xml",
        "views/l10n_mx_edi_tariff_fraction_view.xml"
    ],
    'installable': True,
    'auto_install': False
}
