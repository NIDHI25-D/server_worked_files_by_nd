from odoo import fields, models, api
from datetime import datetime
from dateutil import relativedelta


class UpdateCustomerSegment(models.TransientModel):
    _name = 'update.customer.segment'
    _description = "Update Customer Segment"

    def _default_end_date(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : it calculates a default end date for a date field
        """
        past_x_days_sales = '365'
        if past_x_days_sales:
            return datetime.today() - relativedelta.relativedelta(days=int(past_x_days_sales))

    def _get_default_note(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : it constructs a default note that summarizes the period used for RFM calculations
        """
        segment = self.env['setu.rfm.segment'].search([], limit=1)

        if segment and segment.calculated_on and segment.from_date and segment.to_date:
            return """
                Past sales history has been taken from %s to %s to calculate RFM segment.
                RFM segment calculation was made last on %s 
            """ % (segment.from_date, segment.to_date, segment.calculated_on)

    date_begin = fields.Date(string='Start Date', required=True, default=_default_end_date)
    date_end = fields.Date(string='End Date', required=True, default=datetime.today())
    note = fields.Text(string="Note", default=_get_default_note)

    def update_customer_segment(self):
        """
        added by: Siddharth Vasani | On : OCt-10-2024 | Task: [903] Migration 18 : RFM Analysis - Marketing Strategy
        use : to update segments of customer in sale order and point of sale order and set the segment in res partner
        """
        date_end = datetime.today()
        company_ids = self.env['res.company'].sudo().search([])
        calculation_type = 'static'
        if self.env.user.has_group('setu_rfm_analysis.group_dynamic_rules'):
            calculation_type = 'dynamic'
        segment_type = 'company'
        if self.env.user.has_group('setu_rfm_analysis.group_sales_team_rfm'):
            segment_type = 'sales_team'
        query = """
                    SELECT * FROM update_customer_rfm_segment('%s', null::date, '%s', '%s', '%s')
                """ % (str(set(company_ids.ids)), date_end, calculation_type, segment_type)
        self._cr.execute(query)
        for company in company_ids:
            # sale_order_query = f"""
            #     SELECT partner_id, rfm_segment_id
            #     FROM sale_order
            #     WHERE company_id = {company.id}
            #     AND state IN ('sale', 'done')
            #     ORDER BY create_date DESC
            #     LIMIT 1;
            # """
            # self._cr.execute(sale_order_query)
            # latest_sale_order = self._cr.fetchone()

            # if latest_sale_order:
            #     partner_id, rfm_segment_id = latest_sale_order
            #
            #     partner = self.env['res.partner'].browse(partner_id)
            #     partner.rfm_segment_id = rfm_segment_id
            # else:
            #     partner_ids = self.env['res.partner'].search([('active', '=', True)])
            #     for partner in partner_ids:
            #         team_segments = partner.rfm_team_segment_ids
            #         if not partner.rfm_segment_id:
            #
            #             if team_segments:
            #                 latest_segment = team_segments[0]
            #                 segment_id = latest_segment.segment_id
            #                 segment_name = segment_id.name if hasattr(segment_id, 'name') else str(segment_id)
            #                 last_word = segment_name.split('->')[-1].strip()
            #                 rfm_segment = self.env['setu.rfm.segment'].search([('name', '=', last_word)], limit=1)
            #                 if rfm_segment:
            #                     partner.rfm_segment_id = rfm_segment.id
            #         else:
            #             if team_segments:
            #                 latest_segment = team_segments[0]
            #                 segment_id = latest_segment.segment_id
            #                 segment_name = segment_id.name if hasattr(segment_id, 'name') else str(segment_id)
            #                 last_word = segment_name.split('->')[-1].strip()
            #                 rfm_segment = self.env['setu.rfm.segment'].search([('name', '=', last_word)], limit=1)
            #                 if rfm_segment and partner.rfm_segment_id != rfm_segment.id:
            #                     partner.rfm_segment_id = rfm_segment.id
            #             else:
            #                 partner.rfm_segment_id = False
            history_date = datetime.today() - relativedelta.relativedelta(days=int(company.segment_history_days))
            history_date = history_date.date()
            history_clean_up_query = f"""
                DELETE FROM rfm_partner_history
                WHERE date_changed < '{str(history_date)}' AND company_id = {company.id};
            """
            self._cr.execute(history_clean_up_query)