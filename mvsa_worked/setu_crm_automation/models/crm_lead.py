from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    name = fields.Char('Opportunity', index=True, required=True, default='New')
    untaxed_invoice_amount = fields.Float(string="Untaxed Invoiced Amount", compute="_calculate_untaxed_amount",
                                          store=True)

    def write(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 29/01/25
            Task: Migration to v18 from v16
            Purpose: This method is used to give error when the user changes the state of the crm.lead if the 
                     boolean : "Enable to change CRM Lead stage manually" is not enable
        """
        message = self.env['ir.config_parameter'].sudo().get_param('setu_crm_automation.message') or ''
        if vals.get('stage_id') and self.stage_id.id != vals.get('stage_id') and not self._context.get(
                'is_from_sale_order') and not self.env.user.has_group(
            'setu_crm_automation.group_crm_user_to_change_stage_manually'):
            raise ValidationError(_(f"{message}"))
        res = super(CrmLead, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 29/01/25
            Task: Migration to v18 from v16
            Purpose: This method is used to create a new crm i.e. from Pipeline with sequence starting from CRM 
                     as mentioned in crm_sequence.xml
        """
        seq = self.env['ir.sequence'].next_by_code('crm.lead') or 'New'
        vals['name'] = seq
        partner_obj = self.env['res.partner'].browse(vals.get('partner_id'))
        if partner_obj.category_id:
            ids = []
            for cat in partner_obj.category_id:
                cat_ids = self.env['crm.tag'].search([('name', 'ilike', cat.name)]).ids
                if cat_ids:
                    ids.extend(cat_ids)
            vals.update({'tag_ids': [(6, 0, ids)]})
        elif partner_obj.zone_id:
            vals.update(
                {'tag_ids': [(6, 0, self.env['crm.tag'].search([('name', 'ilike', partner_obj.zone_id.name)]).ids)]})
        else:
            vals.update({'tag_ids': False})
        res = super(CrmLead, self).create(vals)
        return res

    def change_state_of_opportunity(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 29/01/25
            Task: Migration to v18 from v16
            Purpose: This method is used in Cron. This method changes the state to lost of those crm_lead whose state = new and move the record in archive with lost reason.
                     It will set the lost reason as Final del Periodo i.e. End of Period
        """
        leads_in_new_state = self.search([('stage_id.id', '=', self.env.ref('crm.stage_lead1').id)])
        lost_reason = self.env['crm.lost.reason'].search([('name', '=', 'Final del Periodo')])
        for lead in leads_in_new_state:
            lead.action_set_lost(lost_reason_id=lost_reason.id)


    @api.depends('order_ids.invoice_ids', 'order_ids.invoice_ids.state')
    def _calculate_untaxed_amount(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 29/01/25
            Task: Migration to v18 from v16
            Purpose: This method is used to assign untaxed_amount of invoices
        """
        for op in self:
            untaxed_amount = sum(
                op.order_ids.invoice_ids.filtered(lambda i: i.state == 'posted').mapped('amount_untaxed'))
            op.untaxed_invoice_amount = untaxed_amount

    @api.onchange('partner_id')
    def change_tags(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 29/01/25
            Task: Migration to v18 from v16
            Purpose: This method is used to call when the partner_id of the crm.lead is changed. It will assign the fields 
                    such as user_id,team_id,tag_ids of the new partner_id
        """
        if self.partner_id.user_id:
            self.user_id = self.partner_id.user_id
        # as it not available in res.partner (contact)
        # if self.partner_id.team_id:
        #     self.team_id = self.partner_id.team_id
        if self.partner_id.category_id:
            ids = []
            for cat in self.partner_id.category_id:
                cat_ids = self.env['crm.tag'].search([('name', 'ilike', cat.name)]).ids
                if cat_ids:
                    ids.extend(cat_ids)
            self.tag_ids = [(6, 0, ids)]
        elif self.partner_id.zone_id:
            self.tag_ids = [(6, 0, self.env['crm.tag'].search([('name', 'ilike', self.partner_id.zone_id.name)]).ids)]
        else:
            self.tag_ids = False
