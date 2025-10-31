from odoo import fields, models, api
from lxml import etree


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    rfm_segment_id = fields.Many2one(comodel_name='setu.rfm.segment', compute='_compute_rfm_segment', store=True)

    @api.depends('partner_id', 'partner_id.rfm_segment_id')
    def _compute_rfm_segment(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : it computes the leads of partner and its segment
        """
        for lead in self:
            if lead.partner_id.rfm_segment_id:
                lead.rfm_segment_id = lead.partner_id.rfm_segment_id
            else:
                lead.rfm_segment_id = False

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : it does not allow to create record and manages the architecture when view is list and form view
        """
        res = super(CRMLead, self).get_view(view_id, view_type, **options)
        if view_type in ['list', 'form']:
            # action = self._context.get('params', {}).get('action', False) or False
            # if not action:
            action = self._context.get('action_id', False)
            # action = action and self.env['ir.actions.act_window'].sudo().browse(action)
            try:
                if action == 'setu_rfm_analysis.action_all_open_leads':
                    arch = res.get('arch', False)
                    if arch:
                        doc = etree.XML(arch)
                        doc.set("create", "0")
                        res['arch'] = etree.tostring(doc, encoding='unicode')
            except Exception as e:
                pass
        return res

    @api.model
    def get_views(self, views, options=None):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : to adjust the context to ensure proper handling of views and prevents record creation
        """
        context = self._context.copy() or {}
        action = context and context is not None and context.get('action_id', False) or False
        # action = action and self.env['ir.actions.act_window'].sudo().browse(action)
        # action = action and self.sudo().env.ref(action) or False
        try:
            if action and action == 'setu_rfm_analysis.action_all_open_leads':
                context.update({'action': action.id})
        except Exception as e:
            pass
        return super(CRMLead, self.with_context(context)).get_views(views=views, options=options)

