# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def prepare_company_domain(self):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 08/01/2025
        Task: [1393] Setu Customer Rating v18
        Purpose: This method will used to prepare journals domain company wise
        :return: domain list of tuple
        """
        return [('company_id', '=', self.env.company.id)]

    # Integer Fields
    customer_score_days = fields.Integer(
        string="Customer Score Based On Past X Days",
        config_parameter="setu_customer_rating.customer_score_days")
    past_days_for_invoice = fields.Integer(
        string="Unpaid Invoices Of Past X Days",
        config_parameter="setu_customer_rating.past_days_for_invoice")
    grace_days_to_paid_invoice = fields.Integer(
        string="Grace days to paid invoice after due date",
        config_parameter="setu_customer_rating.grace_days_to_paid_invoice")

    # Relational Fields
    journal_ids = fields.Many2many(
        comodel_name="account.journal",
        relation="res_journal_tab_rel",
        column1="res_id",
        column2="journal_id",
        domain=prepare_company_domain,
        string="Journals")
    invoice_journal_ids = fields.Many2many(
        comodel_name="account.journal",
        relation="invoice_journal_tab_rel",
        column1="res_id",
        column2="invoice_journal_id",
        domain=prepare_company_domain,
        string="Invoice Journals")
    grace_days_journal_ids = fields.Many2many(
        comodel_name="account.journal",
        relation="res_grace_days_journal_tab_rel",
        column1="res_id",
        column2="journal_id",
        domain=prepare_company_domain,
        string="Journals")

    def get_values(self):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 01/01/2025
        Task: [1393] Setu Customer Rating v18
        Purpose: View journal, invoice journals and grace days journals in config parameter and ir.default value company wise
        :return:
        """
        res = super(ResConfigSettings, self).get_values()
        company_id = self.env.company
        cust_score_days_param_k = f'setu_customer_rating.customer_score_days_{company_id.id}'
        cust_score_days_param_v = self.env['ir.config_parameter'].sudo().get_param(cust_score_days_param_k, default=365)
        past_days_for_invoice_param_k = f'setu_customer_rating.past_days_for_invoice_{company_id.id}'
        past_days_for_invoice_param_v = self.env['ir.config_parameter'].sudo().get_param(past_days_for_invoice_param_k, default=60)
        grace_days_param_key = f'setu_customer_rating.grace_days_to_paid_invoice_{company_id.id}'
        grace_days_param_v = self.env['ir.config_parameter'].sudo().get_param(grace_days_param_key, default=0)
        res.update(
            customer_score_days=cust_score_days_param_v,
            past_days_for_invoice=past_days_for_invoice_param_v,
            grace_days_to_paid_invoice=grace_days_param_v,
        )
        journal_param_key = f'setu_customer_rating.journal_ids_{company_id.id}'
        journal_param_value = self.env['ir.config_parameter'].sudo().get_param(journal_param_key, default='')
        invoice_journal_param_key = f'setu_customer_rating.invoice_journal_ids_{company_id.id}'
        invoice_journal_param_value = self.env['ir.config_parameter'].sudo().get_param(invoice_journal_param_key,
                                                                                       default='')
        grace_days_journal_param_key = f'setu_customer_rating.grace_days_journal_ids_{company_id.id}'
        grace_days_journal_param_value = self.env['ir.config_parameter'].sudo().get_param(grace_days_journal_param_key,
                                                                                          default='')
        if journal_param_value or invoice_journal_param_value or grace_days_journal_param_value:
            journal_ids = [int(x) for x in journal_param_value.split(',') if x]
            invoice_journal_ids = [int(x) for x in invoice_journal_param_value.split(',') if x]
            grace_days_journal_ids = [int(x) for x in grace_days_journal_param_value.split(',') if x]
            res.update(
                       journal_ids=[(6, 0, journal_ids)],
                       invoice_journal_ids=[(6, 0, invoice_journal_ids)],
                       grace_days_journal_ids=[(6, 0, grace_days_journal_ids)]
                       )
        return res

    def set_values(self):
        """
        Author: siddharth.vasani@setuconsulting.com
        Date: 01/01/2025
        Task: [1393] Setu Customer Rating v18
        Purpose: Set journal, invoice journals and grace days journals etc... in config parameter and ir.default company wise
        :return:
        """
        res = super(ResConfigSettings, self).set_values()
        company_id = self.env.company
        customer_score_days_param = f'setu_customer_rating.customer_score_days_{company_id.id}'
        past_days_for_invoice_param = f'setu_customer_rating.past_days_for_invoice_{company_id.id}'
        grace_days_to_paid_invoice_param = f'setu_customer_rating.grace_days_to_paid_invoice_{company_id.id}'
        journal_company_param = f'setu_customer_rating.journal_ids_{company_id.id}'
        invoice_journal_company_param = f'setu_customer_rating.invoice_journal_ids_{company_id.id}'
        grace_days_journals_company_param = f'setu_customer_rating.grace_days_journal_ids_{company_id.id}'
        self.env['ir.config_parameter'].sudo().set_param(customer_score_days_param, self.customer_score_days)
        self.env['ir.config_parameter'].sudo().set_param(past_days_for_invoice_param, self.past_days_for_invoice)
        self.env['ir.config_parameter'].sudo().set_param(grace_days_to_paid_invoice_param, self.grace_days_to_paid_invoice)
        self.env['ir.config_parameter'].sudo().set_param(journal_company_param,
                                                         ','.join(map(str, self.journal_ids.ids)))
        self.env['ir.config_parameter'].sudo().set_param(invoice_journal_company_param,
                                                         ','.join(map(str, self.invoice_journal_ids.ids)))
        self.env['ir.config_parameter'].sudo().set_param(grace_days_journals_company_param,
                                                         ','.join(map(str, self.grace_days_journal_ids.ids)))
        return res
