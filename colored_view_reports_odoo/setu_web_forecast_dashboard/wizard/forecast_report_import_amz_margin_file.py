from odoo import models, fields, api, _
import logging
from odoo.exceptions import UserError
import base64, io, openpyxl, re
_logger = logging.getLogger(__name__)

class ForecastReportImportAmzFileWizard(models.TransientModel):
    _name = 'forecast.report.import.amz.file.wizard'
    _description = "Import Trigger XLSX File Wizard"


    import_file_forecast_wizard_for_margin = fields.Binary(string="Import XLSX File")

    def action_import_forecast_file(self):
        file_data = self.import_file_forecast_wizard_for_margin

        if not file_data:
            raise UserError(_("Please upload an XLSX file."))

        data = base64.b64decode(file_data)
        workbook = openpyxl.load_workbook(io.BytesIO(data))
        sheet = workbook.active

        headers = [str(cell.value).strip().lower() if cell.value else '' for cell in sheet[1]]
        _logger.info("Headers found: %s", headers)

        sku_idx = next((i for i, h in enumerate(headers) if 'sku' in h), None)
        margin_idx = next((i for i, h in enumerate(headers) if 'margin' in h), None)

        if sku_idx is None or margin_idx is None:
            raise UserError(_("Your Excel must contain at least 'SKU' and 'Margin' columns."))

        Product = self.env['product.product']
        MarginModel = self.env['forecast.report.amz.margin']
        missing_products = []
        created_count = 0
        updated_count = 0
        today = fields.Date.today()

        for row in sheet.iter_rows(min_row=2, values_only=True):
            sku_field = row[sku_idx]
            margin_value = row[margin_idx]

            if not sku_field:
                continue

            # Handle multiple SKUs in one cell: split by comma or whitespace
            sku_list = re.split(r'[, ]+', str(sku_field).strip())
            sku_list = [s.strip() for s in sku_list if s.strip()]

            # Keep the margin exactly as it is in Excel (e.g., 20.16%)
            if isinstance(margin_value, str):
                margin_value = margin_value.replace('%', '').strip()
                if margin_value.startswith('='):
                    margin_value = margin_value[1:].strip()
                    # Excel error codes or junk… default 0.0 directly
                    bad_values = ['#DIV/0!', None]
                    if margin_value in bad_values:
                        margin_value = 0.0
            margin_value = float(margin_value or 0.0)

            for sku in sku_list:
                product = Product.search([('default_code', '=', sku)], limit=1)
                if not product:
                    missing_products.append(sku)
                    continue

                # #Update product margin field
                # product.margin = margin_value

                #Check if record exists for same date & product
                existing_record = MarginModel.search([
                    ('amz_margin_product_id', '=', product.id),
                    ('forecast_report_date_amz_margin', '=', today)
                ], limit=1)

                if existing_record:
                    existing_record.amz_margin = margin_value
                    updated_count += 1
                else:
                    MarginModel.create({
                        'forecast_report_date_amz_margin': today,
                        'amz_margin': margin_value,
                        'amz_margin_product_id': product.id,
                    })
                    created_count += 1

        # Final summary message
        msg = _(" %d product margins updated.") % created_count
        if missing_products:
            msg += _("\n Missing SKUs: %s") % ', '.join(missing_products)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Import Complete"),
                'message': msg,
                'type': 'success' if not missing_products else 'warning',
                'sticky': False,
            }
        }
