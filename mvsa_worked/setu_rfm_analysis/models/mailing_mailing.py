from odoo import fields, models, api, _
from lxml import etree


class MailingMailing(models.Model):
    _inherit = 'mailing.mailing'

    rfm_segment_id = fields.Many2one(comodel_name="setu.rfm.segment", string="RFM Segment",
                                     help="Connect RFM segment with Mailing feature")

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : it does not allow to create record and manages the architecture when view is list and form view
        """
        res = super(MailingMailing, self).get_view(view_id, view_type, **options)
        if view_type in ['list', 'form']:
            action = self._context.get('action_id', False)
            try:
                if action == 'setu_rfm_analysis.action_open_all_mailings':
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
        try:
            if action and action == 'setu_rfm_analysis.action_open_all_mailings':
                context.update({'action': action.id})
        except Exception as e:
            pass
        return super(MailingMailing, self.with_context(context)).get_views(views=views, options=options)
