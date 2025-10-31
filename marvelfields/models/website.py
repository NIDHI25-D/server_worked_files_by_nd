from odoo import models


class Website(models.Model):
    _inherit = "website"

    def _search_get_details(self, search_type, order, options):
        """
              Author: jay.garach@setuconsulting.com
              Date: 02/01/25
              Task: Migration from V16 to V18
              Purpose: to add compatible_ids into search fields.
        """
        result = super()._search_get_details(search_type, order, options)
        if search_type in ['products_only']:
            compatible_ids = 'compatible_ids.name'
            result[0]['search_fields'].append(compatible_ids)
        return result
