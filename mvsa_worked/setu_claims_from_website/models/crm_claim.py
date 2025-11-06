# -*- coding: utf-8 -*-

import odoo
from odoo import models, fields, api, _
from odoo.tools import html2plaintext
from odoo.exceptions import UserError
from datetime import timedelta


class crm_claim(models.Model):
    """ Crm claim
    """
    _name = "crm.claim"
    _description = "Claim"
    _fold_name = 'fold'
    _order = "priority,date desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    product_tmpl_id = fields.Many2one('product.template', string="Modelo", required=True)
    contact_information = fields.Char("Contact Information", required=True)
    product_id = fields.Many2one('product.product', string="Product")
    is_from_website = fields.Boolean('Is from Website', default=False)
    irrigation_system = fields.Boolean('Irrigation System', default=False)
    potential_trouble = fields.Boolean('Potential Trouble', default=False)
    ctb_repair = fields.Boolean('CTB Repair', default=False)
    product_default_code = fields.Char('Default Code')
    product_default_name = fields.Char('Name')
    fold = fields.Boolean(string='Folded in Kanban',
                          help='This stage is folded in the kanban view when there are no records in that stage to display.')
    vendor_rejection_motive = fields.Text(string="Vendor rejection motive")
    vendor_charges_status = fields.Many2one('vendor.charge.status')
    related_po = fields.Many2one('purchase.order', string='Related PO')
    internal_claim_reference = fields.Text()

    @api.onchange('no_warranty_apply')
    def onchange_no_warranty_apply(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 25/03/25
            Task: Migration from V16 to V18 (https://app.clickup.com/t/86du6a1cz)
            Purpose: when no_warranty_apply is True then stage set to be Entregado.
        """
        if self.no_warranty_apply:
            self._origin.stage_id = self.env['crm.claim.stage'].search([('sequence', '=', 6)]).id

    @api.onchange('product_tmpl_id')
    def onchange_product_default_code_name(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 25/03/25
            Task: Migration from V16 to V18 Claims Module Enhancement.
            Purpose: to set the value of product_default_code field and product_default_name field.
        """
        self.product_default_code = self.product_tmpl_id.default_code
        self.product_default_name = self.product_tmpl_id.name

    @api.model
    def _get_default_stage_id(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 25/03/25
            Task: Migration from V16 to V18
            Purpose: Gives default stage_id
        """
        team_id = self.env['crm.team']._get_default_team_id()
        return self.stage_find([], team_id, [('sequence', '=', '1')])

    # THERE IS NO SUCH MODULE SO ITS COMMENTED
    # @api.model
    # def _reference_models(self):
    #     models = self.env['res.request.link'].search([])
    #     return [(model.object, model.name) for model in models]

    id = fields.Integer('ID', readonly=True)
    name = fields.Char('Claim Subject', readonly=True, required=True, copy=False, default='New')
    active = fields.Boolean('Active', default=1)
    action_next = fields.Char('Next Action')
    date_action_next = fields.Datetime('Next Action Date')
    description = fields.Text('Description', required=True)
    resolution = fields.Text('Resolution')
    create_date = fields.Datetime('Creation Date', readonly=True)
    write_date = fields.Datetime('Update Date', readonly=True)
    date_deadline = fields.Date('Deadline', required=True, compute='_compute_deadline', store=True, precompute=True)
    date_closed = fields.Datetime('Closed', copy=False)
    # date_closed = fields.Datetime('Closed', readonly=True)
    date = fields.Datetime('Claim Date', index=True, default=fields.Datetime.now)

    ref = fields.Char('Ref', required=True)
    # ref = fields.Reference(string='Reference', selection='_reference_models')
    # ref = fields.Reference(string='Reference', selection=openerp.addons.base.res.res_request.referencable_models)

    categ_id = fields.Many2one('crm.case.categ', 'Category',
                               domain="[('team_id','=',team_id),   ('object_id.model', '=', 'crm.claim')]")
    priority = fields.Selection(
        [('0', 'Low'), ('1', 'Normal'), ('2', 'High')], 'Priority', default='1')
    # remove selection and instead of this put action_type_id with relation crm.action.type as per the task -- https://app.clickup.com/t/86duw615z
    # type_action = fields.Selection([('correction', 'Corrective Action'), ('prevention', 'Preventive Action')],
    #                                'Action Type')
    action_type_id = fields.Many2one('crm.action.type', string="Action Type",
                                     domain="[('crm_case_categ_id','=',categ_id)]")
    user_id = fields.Many2one('res.users', 'Responsible',
                              tracking=True, default=lambda self: self.env.user.id)
    user_fault = fields.Char('Trouble Responsible')
    team_id = fields.Many2one('crm.team', 'Sales Team',
                              index=True, help="Responsible sales team."
                                               " Define Responsible user and Email account for"
                                               " mail gateway.")

    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('crm.case'))
    partner_id = fields.Many2one('res.partner', 'Partner', required=True)
    email_cc = fields.Text('Watchers Emails', size=252,
                           help="These email addresses will be added to the CC field of all inbound and outbound emails for this record before being sent. Separate multiple email addresses with a comma")
    email_from = fields.Char('Email', size=128, required=True, help="Destination email for email gateway.")
    partner_phone = fields.Char('Phone', required=True)
    stage_id = fields.Many2one('crm.claim.stage', 'Stage', tracking=True, default=_get_default_stage_id,
                               group_expand='_read_group_stage_ids')
    # domain="['|', ('team_ids', '=', team_id), ('case_default', '=', True)]")
    cause = fields.Text('Root Cause', copy=False)

    is_expense = fields.Boolean(default=False, string='Is Expense')
    parent_id = fields.Many2one('hr.department', 'Deparment')
    cost_without_vat = fields.Float(string="Cost Without Vat", digits=(6, 2))
    invoice_ids = fields.Many2many('account.move', string='Invoices')
    # service_number = fields.Char(string="Service Number", readonly=True, required=True, copy=False, default='New')
    warranty_ids = fields.One2many('stock.picking', 'claim_id', string="Warranty Id")
    shipping_carrier_id = fields.Many2one('shipping.carrier', string="Carrier", compute="_compute_fields_from_picking",
                                          store=True)
    # related='warranty_ids.shipping_carrier_id')
    x_studio_fecha_de_envio = fields.Datetime(string="Shipping Date", compute="_compute_fields_from_picking",
                                              store=True)
    # , related='warranty_ids.x_studio_fecha_de_envio', copy=False)
    carrier_tracking_ref = fields.Char(string='Tracking Reference', compute="_compute_fields_from_picking", store=True)
    # , related='warranty_ids.carrier_tracking_ref',copy=False)
    no_warranty_apply = fields.Boolean(string='No warranty apply')
    claim_sent = fields.Boolean(string='Claim Sent')
    claim_date_sent_to_vendor = fields.Date(string='Claim Date Sent To Vendor')
    claim_comments = fields.Text(string='Claim Comments')
    recovered_balance_in_usd = fields.Float(string="Recovered Balance($)")
    payed_claim_finished = fields.Boolean(string='Payed Claim Finished')
    rejected = fields.Boolean(string='Rejected')
    rejection_reason = fields.Text(string='Rejection reason')
    claim_history_ids = fields.One2many('claim.state.history', 'claim_id', string="Claim History", tracking=True)

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        """
            Author: Siddharth@setuconsulting.com
            Date: 11/09/23
            Task: Claims Module Enhancement.
            Purpose: To show all stages in Kanban view even if there are no records.
        """
        return self.env['crm.claim.stage'].search([], order=stages._order)

    @api.model
    def stage_find(self, cases, team_id, domain=[], order='sequence'):
        """
            Authour: nidhi@setconsulting
            Date: 09/05/23
            Task: Migration from V14 to V16
            Purpose: Override of the base.stage method
                    Parameter of the stage search taken from the lead:
                   - team_id: if set, stages must belong to this team or be a default case
                   -creates a domain for stage_id
        """
        if isinstance(cases, (int)):
            cases = self.browse(cases)
        # collect all team_ids
        team_ids = []
        if team_id:
            team_ids.append(team_id.id)
        for claim in cases:
            if claim.team_id:
                team_ids.append(claim.team_id.id)
        # OR all team_ids and OR with case_default
        search_domain = []
        if team_ids:
            search_domain += [('|')] * len(team_ids)
            for team_id in team_ids:
                search_domain.append(('team_ids', '=', team_id))
        search_domain.append(('case_default', '=', True))
        # AND with the domain in parameter
        search_domain += list(domain)
        # perform search, return the first found
        stage_id = self.env['crm.claim.stage'].search(search_domain, order=order, limit=1)
        if stage_id:
            return stage_id.id
        return False

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
            Authour: nidhi@setconsulting
            Date: 09/05/23
            Task: Migration from V14 to V16
            Purpose: When the partner of claims(backend) is changed then this will update the email and phone
        """
        if not self.partner_id:
            return {'value': {'email_from': False, 'partner_phone': False}}
        address = self.partner_id
        return {'value': {'email_from': address.email, 'partner_phone': address.phone}}

    @api.model_create_multi
    def create(self, vals_list):
        """
            Authour: nidhi@setconsulting
            Date: 09/05/23
            Task: Migration from V14 to V16
            Purpose: This method is to create the claims in backend as well as set the sequence, team_id and enable the website boolean
        """
        for vals in vals_list:
            if self._context.get('website_id'):
                vals.update({'is_from_website': True})

            if vals.get('team_id') and not self.env.context.get('default_team_id'):
                default_team_id = vals.get('team_id')
                self = self.with_context(default_team_id=default_team_id)

            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('crm.claim')
            # context: no_log, because subtype already handle this
            stage_id = self.env['crm.claim.stage'].browse(vals.get('stage_id'))
            # if vals.get('partner_id') and vals.get('contact_information') and vals.get('partner_phone') and vals.get('email_from') and vals.get('product_tmpl_id') and vals.get('user_fault') and vals.get('categ_id') and vals.get('ref') and vals.get('description'):
            vals.update({'stage_id': 2})
            if vals.get('stage_id', False):
                vals['claim_history_ids'] = [(0, 0, {'stage_id': vals['stage_id']})]
        claims = super(crm_claim, self).create(vals_list)
        for claim in claims:
            claim.message_post(
                body=_(
                    f"the state are changed from {stage_id.name} --> {claim.stage_id.name}"
                )
            )
        return claims

    def copy(self, default=None):
        """
            Authour: nidhi@setconsulting
            Date: 09/05/23
            Task: Migration from V14 to V16
            Purpose: This method will add the prefix copy to the claims which are duplicated
        """
        claim = self
        default = dict(default or {}, stage_id=self._get_default_stage_id(),
                       name=_('%s (copy)') % claim.name)
        return super(crm_claim, self).copy(default)

    # -------------------------------------------------------
    # Mail gateway
    # -------------------------------------------------------

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """
            Authour: nidhi@setconsulting
            Date: 09/05/23
            Task: Migration from v14 to v16
            Purpose: Overrides mail_thread message_new that is called by the mailgateway
                through message_process.
                This override updates the document according to the email.
            Procedure : Settings->Messages..Body claim created
        """
        if custom_values is None:
            custom_values = {}
        desc = html2plaintext(msg_dict.get('body')) if msg_dict.get('body') else ''
        defaults = {
            'name': msg_dict.get('subject') or _("No Subject"),
            'description': desc,
            'email_from': msg_dict.get('from'),
            'email_cc': msg_dict.get('cc'),
            'partner_id': msg_dict.get('author_id', False),
        }
        if msg_dict.get('priority'):
            defaults['priority'] = msg_dict.get('priority')
        defaults.update(custom_values)
        return super(crm_claim, self).message_new(msg_dict, custom_values=defaults)

    def write(self, vals):
        if vals.get('rejected') and vals.get('rejection_reason'):
            vals['stage_id'] = self.env['crm.claim.stage'].search([('sequence', '=', 8)]).id
        if vals.get('stage_id'):
            vals['claim_history_ids'] = [(0, 0, {'stage_id': vals['stage_id']})]
        # manage claim stage by next stage(next_stage_id) automation
        # if vals.get('stage_id'):
        # next_stage_id = self.stage_id.next_stage_id.id
        # if next_stage_id == vals.get('stage_id') or self.stage_id.is_last_stage:
        #     return super().write(vals)
        # else:
        #     stage_id = self.env['crm.claim.stage'].browse(vals.get('stage_id'))
        #     if self.env.user.lang and self.env.user.lang == 'es_MX':
        #         raise UserError(_(f"No puedes mover el reclamo en estatus {self.stage_id.name} a {stage_id.name}"))
        #     else:
        #         raise UserError(_(f"You can not move to state from {self.stage_id.name} to {stage_id.name}"))

        return super().write(vals)

    @api.depends('date')
    def _compute_deadline(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 25/03/25
            Task: Migration from V16 to V18
            Purpose: computing date deadline without a weekday.
        """
        for record in self:
            date = fields.Datetime.from_string(record.date)
            days_to_add = 7
            while days_to_add > 0:
                date += timedelta(days=1)
                if date.weekday() < 5:
                    days_to_add -= 1
            record.date_deadline = date

    @api.depends('warranty_ids', 'warranty_ids.shipping_carrier_id', 'warranty_ids.x_studio_fecha_de_envio',
                 'warranty_ids.carrier_tracking_ref')
    def _compute_fields_from_picking(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 25/03/25
            Task: Migration from V16 to V18
            Purpose: setting up fields.
        """
        for rec in self:
            if rec.warranty_ids:
                warranty_ids = rec.warranty_ids[0]
                shipping_carrier_id = warranty_ids.shipping_carrier_id
                x_studio_fecha_de_envio = warranty_ids.x_studio_fecha_de_envio
                carrier_tracking_ref = warranty_ids.carrier_tracking_ref
                rec.shipping_carrier_id = shipping_carrier_id.id if shipping_carrier_id else False
                rec.x_studio_fecha_de_envio = x_studio_fecha_de_envio
                rec.carrier_tracking_ref = carrier_tracking_ref

    @api.onchange('date_closed', 'cause')
    def _onchange_stage(self):
        """
            Author: jay.garach@setuconsulting.com
            Date: 25/03/25
            Task: Migration from V16 to V18
            Purpose: setting the Settled state to claim
        """
        claim_settled_stage_id = self.env['crm.claim.stage'].search([('sequence', '=', 7)])
        if self.date_closed and self.cause and self.stage_id.sequence < claim_settled_stage_id.sequence:
            self._origin.stage_id = claim_settled_stage_id.id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
