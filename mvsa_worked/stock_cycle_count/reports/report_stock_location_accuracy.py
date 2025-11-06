from odoo import api, models


class LocationAccuracyReport(models.AbstractModel):
    _name = "report.stock_cycle_count.stock_location_accuracy"
    _description = "Location Accuracy Report"

    @api.model
    def _get_inventory_domain(self, loc_id, exclude_sublocation=True):
        return [('location_ids', '=', loc_id),
                ('exclude_sublocation', '=', exclude_sublocation),
                ('state', '=', 'done')]

    @api.model
    def _get_location_data(self, locations):
        data = dict()
        inventory_obj = self.env["stock.inventory"]
        for loc in locations:
            counts = inventory_obj.search(self._get_inventory_domain(loc.id))
            data[loc] = counts
        return data

    @api.model
    def _get_report_values(self, docids, data=None):
        locs = self.env["stock.location"].browse(docids)
        data = self._get_location_data(locs)
        return {
            'doc_ids': docids,
            'doc_model': 'stock.location',
            'docs': locs,
            'data': data,
        }