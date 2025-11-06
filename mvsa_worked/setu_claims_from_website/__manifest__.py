{
    'name': "Claims From Website",
    'version': "18.0.0.0",
    'author': "Setu Consulting Services Pvt. Ltd.",
    'license': "OPL-1",
    'category': "eCommerce",
    'website': "https://www.setuconsulting.com/",
    'depends': ['base', 'portal', 'account', 'sales_team', 'setu_prefered_delivery_methods',
                'setu_sales_time_dashboard'],
    'images': ['images/shop.png'],
    # 'demo': ['data/crm_claim_demo.xml'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/crm_claim_data.xml',
        'data/crm_claim_sequence.xml',
        'views/claims_inherit.xml',
        'views/new_claim_form.xml',
        'views/show_claim_view.xml',
        'views/res_config_settings_views.xml',
        'views/crm_claim_view.xml',
        'views/set_service_agent_in_crm_team.xml',
        'views/button_in_invoice.xml',
        'views/crm_claim_menu.xml',
        'views/res_partner_view.xml',
        'views/stock_picking_views.xml',
        'report/crm_claim_report_view.xml',
        'report/claim_report_view.xml',
        'report/claim_report_template.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'setu_claims_from_website/static/src/js/onchange_for_products.js',
            'web/static/lib/jquery/jquery.js',
        ],
    },
    # 'test': [
    #     'test/process/claim.yml',
    #     'test/ui/claim_demo.yml'
    # ],
    'installable': True,
}
