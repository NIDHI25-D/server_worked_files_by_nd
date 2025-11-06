from odoo import models, api, fields,_
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_preorder = fields.Boolean(
        string="Pre-Order", readonly=True, default=False, copy=False)

    is_presale = fields.Boolean(
        string="Pre-Sale", readonly=True, default=False, copy=False)
    is_next_day_shipping = fields.Boolean(string="Next Day Shipping",related='sale_id.is_next_day_shipping')
    assortment_start_date = fields.Datetime(string="Assortment Start Date",
                                              help="This date will be set once the Assorted button is clicked.",copy=False)
    assortment_end_date = fields.Datetime(string="Assortment End Date",
                                            help="This date will be set when the picking is Validated.",copy=False)


    @api.onchange('responsible_person')
    def onchange_responsible_person_to_set_assortment_start_date(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 17/04/25
            Task: Migration to v18 from v16
            Purpose:To set current date in field : assortment_start_date when responsible_person is set in the Transfer.
            If the date is mentioned in the field:assortment_start_date than user cannot cancel the order from the website even though
            the Time limit mentioned in the Sale order is not completed.
        """
        for picking in self:
            if picking.responsible_person and not picking.assortment_start_date :
                picking.assortment_start_date = datetime.now()
                _logger.info("Assortment start date: %s ", picking.assortment_start_date)

    def button_validate(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 17/04/25
            Task: Migration to v18 from v16
            Purpose:To set current date in field : assortment_end_date when transfer is validate.
        """
        res = super(StockPicking, self).button_validate()
        for rec in self:
            rec.assortment_end_date = datetime.now()
            rec.message_post(
                body=_("Assortment End Date is: %s during the validation of Transfer") % (datetime.now())
            )
        return res
