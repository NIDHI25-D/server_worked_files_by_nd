from odoo import models,fields,_
import base64
from io import BytesIO , StringIO
import xlsxwriter
from pandas import read_excel
import pandas as pd
from odoo.exceptions import UserError, ValidationError

class SetuExportSheetData(models.TransientModel):
    _name = "setu.export.sheet.data"
    _description = "Export Data"

    datas = fields.Binary('Excel Report',attachment=True)

    def prepare_excel_report(self):
        """
            Author: udit@setuconsulting
            Date: 05/05/23
            Task: mvsa migration
            Purpose: prepare demo excel sheet to import amount of account in budget record
        """

        active_ids = self._context.get('active_ids')
        adb_sheet = self.env['setu.advance.budget.forecasted.sheet'].browse(active_ids)
        file_pointer = BytesIO()
        wb = xlsxwriter.Workbook(file_pointer)
        for sheet in adb_sheet:
            lines = self.env['setu.advance.budget.forecasted.sheet.line'].search(
                [('setu_advance_budget_forecasted_sheet_id', '=', sheet.id)])
            sheet_1 = wb.add_worksheet(sheet.analytic_account_id.name or 'Undefined')
            sheet_1.write(0, 0, "Analytic_Account")
            sheet_1.write(0, 1, sheet.analytic_account_id.name or 'Undefined')
            sheet_1.write(1, 0, "Plan")
            sheet_1.write(1, 1, sheet.setu_advance_budget_forecasted_id.name)
            sheet_1.write(3, 0, "Account_Group")
            sheet_1.write(3, 1, "Account")
            sheet_1.write(3,2,"Account_Code")
            sheet_1.write(3, 3, "Account_Type")

            list_of_period = []
            for row_index, line in enumerate(lines, start=4):
                if line.account_id:
                    sheet_1.write(row_index, 0, line.account_id.group_id.name or "")
                    sheet_1.write(row_index, 1, line.account_id.name)
                    sheet_1.write(row_index,2,line.account_id.code)
                    sheet_1.write(row_index, 3, line.account_id.account_type)

                    for index, period in enumerate(line.setu_advance_budget_forecasted_position_ids, start=4):
                        if f"{period.start_date.strftime('%Y/%m/%d')}-{period.end_date.strftime('%Y/%m/%d')}" in list_of_period:
                            sheet_1.write(row_index, index, period.planned_amount)
                        else:
                            list_of_period.append(
                                f"{period.start_date.strftime('%Y/%m/%d')}-{period.end_date.strftime('%Y/%m/%d')}")
                            sheet_1.write(3, index,
                                          f"{period.start_date.strftime('%Y/%m/%d')}-{period.end_date.strftime('%Y/%m/%d')}")
                            sheet_1.write(4, index, period.planned_amount)

        wb.close()
        file_pointer.seek(0)
        file_data = base64.encodebytes(file_pointer.read())
        self.write({'datas': file_data})
        file_pointer.close()

        return {
            'name': 'Budget and forecasting report',
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=setu.export.sheet.data&id=%s&field=datas&filename=Budget_and_forecasting.xlsx&download=true' % (
                self.id),
            'target': 'self',
        }


class SetuImportSheetData(models.TransientModel):
    _name = "setu.import.sheet.data"
    _description = "Import Data"

    import_xml_file = fields.Binary(string="Attach File")
    file_name = fields.Char("File Name")

    def import_report_data(self):
        """
            Author: udit@setuconsulting
            Date: 05/05/23
            Task: mvsa migtration
            Purpose: set amount in indicidual
        """
        import_file = BytesIO(base64.decodebytes(self.import_xml_file))
        all_data_file = pd.read_excel(import_file)
        plan_name = all_data_file.values[0][1]
        object_sheet_list= pd.ExcelFile(import_file)
        sheet_list = object_sheet_list.sheet_names
        for sheet_name in sheet_list:
            analytic_account_object = self.env['account.analytic.account'].search([('name','=',sheet_name)])
            sheet_wise_df_samples = pd.read_excel(import_file, header=3 , sheet_name = sheet_name)
            for index , df in sheet_wise_df_samples.iterrows():
                sheet_id = self.env['setu.advance.budget.forecasted.sheet'].search(
                    [('analytic_account_id.name', '=', sheet_name),
                     ('setu_advance_budget_forecasted_id.name', '=', plan_name)])
                Undefined_sheet_id = self.env['setu.advance.budget.forecasted.sheet'].search(
                    [('analytic_account_id', '=', False), ('setu_advance_budget_forecasted_id.name', '=', plan_name)])
                if (len(df) > 16) or (len(sheet_wise_df_samples.index.values) > (len(sheet_id.setu_advance_budget_forecasted_sheet_line_ids) if sheet_id else len(Undefined_sheet_id.setu_advance_budget_forecasted_sheet_line_ids) )) or (len(sheet_wise_df_samples.index.values) < (len(sheet_id.setu_advance_budget_forecasted_sheet_line_ids) if sheet_id else len(Undefined_sheet_id.setu_advance_budget_forecasted_sheet_line_ids) )) :
                    raise ValidationError(_("There is an extra content in any rows or columns.Please check excel sheet and re-import sheet."))

                periods =df[df.where(df[4:]>0).notna()]
                line = self.env['setu.advance.budget.forecasted.sheet.line'].search([('account_id.code','=',df.Account_Code), ('setu_advance_budget_forecasted_sheet_id','=',sheet_id.id if sheet_id else Undefined_sheet_id.id)])
                data = []
                for key,value in periods.items():
                    split_period = key.split("-")
                    period_start_date = split_period[0]
                    period_end_date = split_period[1]
                    position = line.setu_advance_budget_forecasted_position_ids.filtered(lambda pos:pos.start_date.strftime('%Y/%m/%d') == period_start_date and pos.end_date.strftime('%Y/%m/%d') == period_end_date)
                    data.append((1,position.id,{'planned_amount':value}))
                line.write({"setu_advance_budget_forecasted_position_ids":data})
        # return True

