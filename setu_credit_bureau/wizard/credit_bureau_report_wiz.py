from odoo import api, fields, models
import xlsxwriter
from io import BytesIO
import base64
from datetime import datetime, timedelta


class CreditBureauReportWiz(models.TransientModel):
    _name = 'credit.bureau.report.wiz'
    _description = 'Credit Bureau Report Wizard'

    datas = fields.Binary('Excel Report',attachment=True)

    def get_length_validation(self, length):
        return {
            'validate': 'length',
            'criteria': 'less than or equal to',
            'value': length,
            'error_message': f'Input must be {length} characters or less',
        }

    def get_numeric_validation(self, length):
        return {
            'validate': 'integer',
            'criteria': 'between',
            'minimum': f'-{length}',
            'maximum': f'{length}',
            'error_message': f'Input must be a numeric value and {len(str(length))} Characters Length',
        }


    def create_credit_bureau_report(self):
        contact_to_generate_credit_report = self.env['res.partner'].search([('credit_bureau_report', '!=', False)])
        data = BytesIO()
        workbook = xlsxwriter.Workbook(data)
        worksheet = workbook.add_worksheet('Credit Bureau Report')
        bold_with_color = workbook.add_format({'bold': True, 'bg_color': 'blue', 'font_color': 'white', 'font_size': 8, 'border': 1})
        index_style = workbook.add_format({'bold': True, 'bg_color': '8c8c8c', 'font_color': 'black', 'font_size': 8, 'border': 1})
        size_for_main_text = workbook.add_format({'font_size': 10, 'border': 1, 'text_wrap': True})


        #HD Segment Header MX
        worksheet.write('B1', 'Identificador', bold_with_color)
        worksheet.write('C1', 'Institucion', bold_with_color)
        worksheet.write('D1', 'Inst. Ant', bold_with_color)
        worksheet.write('E1', 'Tipo Institucion', bold_with_color)
        worksheet.write('F1', 'Formato', bold_with_color)
        worksheet.write('G1', 'Fecha', bold_with_color)
        worksheet.write('H1', 'Periodo', bold_with_color)
        worksheet.write('I1', 'Version', bold_with_color)
        worksheet.write('J1', 'Usuario', bold_with_color)

        # HD Segment Index
        worksheet.write('B2', 'HD', bold_with_color)
        worksheet.write('C2', '00', index_style)
        worksheet.write('D2', '01', index_style)
        worksheet.write('E2', '02', index_style)
        worksheet.write('F2', '03', index_style)
        worksheet.write('G2', '04', index_style)
        worksheet.write('H2', '05', index_style)
        worksheet.write('I2', '06', index_style)
        worksheet.write('J2', '07', index_style)

        # HD Segment Partner Data
        current_date = datetime.now().strftime('%d%m%Y')

        now = datetime.now()
        if now.month == 1:
            previous_month = 12
            year = now.year - 1
        else:
            previous_month = now.month - 1
            year = now.year
        current_month = now.strftime('%m')
        current_year = now.strftime('%Y')
        formatted_date = f'{previous_month:02}{year}'
        row = 2

        worksheet.write(row, 1, 'BNCPM', size_for_main_text)
        worksheet.write(row, 2, 'A155', size_for_main_text)
        worksheet.write(row, 3, '', size_for_main_text)
        worksheet.data_validation(row, 3, row, 3, self.get_length_validation(4))
        worksheet.data_validation(row, 3, row, 3, self.get_numeric_validation(9999))
        worksheet.write(row, 4, '999', size_for_main_text)
        worksheet.write(row, 5, '2', size_for_main_text)
        worksheet.write(row, 6, current_date, size_for_main_text)
        worksheet.write(row, 7, formatted_date, size_for_main_text)
        worksheet.write(row, 8, '', size_for_main_text)
        worksheet.data_validation(row, 8, row, 8, self.get_length_validation(2))
        worksheet.data_validation(row, 8, row, 8, self.get_numeric_validation(99))
        worksheet.write(row, 9, 'MARVELSA', size_for_main_text)

        # EM Segment Header MX
        worksheet.write(row + 1, 1, 'Identificador', bold_with_color)
        worksheet.write(row + 1, 2, 'RFC', bold_with_color)
        worksheet.write(row + 1, 3, 'Codigo Ciudadano', bold_with_color)
        worksheet.write(row + 1, 4, 'Numero Dun', bold_with_color)
        worksheet.write(row + 1, 5, 'Compañía', bold_with_color)
        worksheet.write(row + 1, 6, 'Nombre 1', bold_with_color)
        worksheet.write(row + 1, 7, 'Nombre 2', bold_with_color)
        worksheet.write(row + 1, 8, 'Paterno', bold_with_color)
        worksheet.write(row + 1, 9, 'Materno', bold_with_color)
        worksheet.write(row + 1, 10, 'Nacionalidad', bold_with_color)
        worksheet.write(row + 1, 11, 'Calificacion Banco de Mex.', bold_with_color)
        worksheet.write(row + 1, 12, 'Banxico 1', bold_with_color)
        worksheet.write(row + 1, 13, 'Banxico 2', bold_with_color)
        worksheet.write(row + 1, 14, 'Banxico 3', bold_with_color)
        worksheet.write(row + 1, 15, 'Direccion 1', bold_with_color)
        worksheet.write(row + 1, 16, 'Direccion 2', bold_with_color)
        worksheet.write(row + 1, 17, 'Colonia/Poblacion', bold_with_color)
        worksheet.write(row + 1, 18, 'Delegacion/Municipio', bold_with_color)
        worksheet.write(row + 1, 19, 'Ciudad', bold_with_color)
        worksheet.write(row + 1, 20, 'Estado', bold_with_color)
        worksheet.write(row + 1, 21, 'C.P.', bold_with_color)
        worksheet.write(row + 1, 22, 'Telefono', bold_with_color)
        worksheet.write(row + 1, 23, 'Extension', bold_with_color)
        worksheet.write(row + 1, 24, 'Fax', bold_with_color)
        worksheet.write(row + 1, 25, 'Tipo Cliente', bold_with_color)
        worksheet.write(row + 1, 26, 'Estado extranjero', bold_with_color)
        worksheet.write(row + 1, 27, 'Pais', bold_with_color)
        worksheet.write(row + 1, 28, 'Clave de Cosolidación', bold_with_color)

        # AC Segment Header MX
        worksheet.write(row + 1, 29, 'Identificador', bold_with_color)
        worksheet.write(row + 1, 30, 'RFC Accionista', bold_with_color)
        worksheet.write(row + 1, 31, 'Codigo Ciudadano', bold_with_color)
        worksheet.write(row + 1, 32, 'Numero Dun', bold_with_color)
        worksheet.write(row + 1, 33, 'Nombre Cia.', bold_with_color)
        worksheet.write(row + 1, 34, 'Nombre 1', bold_with_color)
        worksheet.write(row + 1, 35, 'Nombre 2', bold_with_color)
        worksheet.write(row + 1, 36, 'Paterno', bold_with_color)
        worksheet.write(row + 1, 37, 'Materno', bold_with_color)
        worksheet.write(row + 1, 38, 'Porcentaje', bold_with_color)
        worksheet.write(row + 1, 39, 'Direccion 1', bold_with_color)
        worksheet.write(row + 1, 40, 'Direccion 2', bold_with_color)
        worksheet.write(row + 1, 41, 'Colonia/Población', bold_with_color)
        worksheet.write(row + 1, 42, 'Delegación/Municipio', bold_with_color)
        worksheet.write(row + 1, 43, 'Ciudad', bold_with_color)
        worksheet.write(row + 1, 44, 'Estado', bold_with_color)
        worksheet.write(row + 1, 45, 'C.P.', bold_with_color)
        worksheet.write(row + 1, 46, 'Telefono', bold_with_color)
        worksheet.write(row + 1, 47, 'Extension', bold_with_color)
        worksheet.write(row + 1, 48, 'Fax', bold_with_color)
        worksheet.write(row + 1, 49, 'Tipo Cliente', bold_with_color)
        worksheet.write(row + 1, 50, 'Estado extranjero', bold_with_color)
        worksheet.write(row + 1, 51, 'Pais', bold_with_color)

        # CR Segment Header MX
        worksheet.write(row + 1, 52, 'Identificador', bold_with_color)
        worksheet.write(row + 1, 53, 'RFC Empresa', bold_with_color)
        worksheet.write(row + 1, 54, 'Numero Experiencias', bold_with_color)
        worksheet.write(row + 1, 55, 'Contrato', bold_with_color)
        worksheet.write(row + 1, 56, 'Contrato Anterior', bold_with_color)
        worksheet.write(row + 1, 57, 'Fecha Apertura', bold_with_color)
        worksheet.write(row + 1, 58, 'Plazo en meses', bold_with_color)
        worksheet.write(row + 1, 59, 'Tipo de Credito', bold_with_color)
        worksheet.write(row + 1, 60, 'Saldo Inicial', bold_with_color)
        worksheet.write(row + 1, 61, 'Moneda', bold_with_color)
        worksheet.write(row + 1, 62, 'Numero Pagos', bold_with_color)
        worksheet.write(row + 1, 63, 'Frecuencia de Pagos', bold_with_color)
        worksheet.write(row + 1, 64, 'Importe de Pagos', bold_with_color)
        worksheet.write(row + 1, 65, 'Fecha Ultimo Pago', bold_with_color)
        worksheet.write(row + 1, 66, 'Fecha Reestructura', bold_with_color)
        worksheet.write(row + 1, 67, 'Pago en efectivo', bold_with_color)
        worksheet.write(row + 1, 68, 'Fecha Liquidacion', bold_with_color)
        worksheet.write(row + 1, 69, 'Quita', bold_with_color)
        worksheet.write(row + 1, 70, 'Dacion', bold_with_color)
        worksheet.write(row + 1, 71, 'Quebranto', bold_with_color)
        worksheet.write(row + 1, 72, 'Observaciones', bold_with_color)
        worksheet.write(row + 1, 73, 'Especiales', bold_with_color)
        worksheet.write(row + 1, 74, 'Fecha Primer Incum', bold_with_color)
        worksheet.write(row + 1, 75, 'Saldo Insoluto', bold_with_color)
        worksheet.write(row + 1, 76, 'Crédito Máximo Utilizado', bold_with_color)
        worksheet.write(row + 1, 77, 'Fecha de Ingreso a cartera vencida', bold_with_color)

        # DE Segment Header MX
        worksheet.write(row + 1, 78, 'Identificador', bold_with_color)
        worksheet.write(row + 1, 79, 'RFC Empresa', bold_with_color)
        worksheet.write(row + 1, 80, 'Contrato', bold_with_color)
        worksheet.write(row + 1, 81, 'Dias Vencimiento', bold_with_color)
        worksheet.write(row + 1, 82, 'Cantidad', bold_with_color)
        worksheet.write(row + 1, 83, 'Interes', bold_with_color)

        # AV Segment Header MX
        worksheet.write(row + 1, 84, 'Identificador', bold_with_color)
        worksheet.write(row + 1, 85, 'RFC Aval', bold_with_color)
        worksheet.write(row + 1, 86, 'Codigo Ciudadano', bold_with_color)
        worksheet.write(row + 1, 87, 'Numero Dun', bold_with_color)
        worksheet.write(row + 1, 88, 'Nombre Cia.', bold_with_color)
        worksheet.write(row + 1, 89, 'Nombre 1', bold_with_color)
        worksheet.write(row + 1, 90, 'Nombre 2', bold_with_color)
        worksheet.write(row + 1, 91, 'Paterno', bold_with_color)
        worksheet.write(row + 1, 92, 'Materno', bold_with_color)
        worksheet.write(row + 1, 93, 'Direccion 1', bold_with_color)
        worksheet.write(row + 1, 94, 'Direccion 2', bold_with_color)
        worksheet.write(row + 1, 95, 'Colonia/Población', bold_with_color)
        worksheet.write(row + 1, 96, 'Delegación/Municipio', bold_with_color)
        worksheet.write(row + 1, 97, 'Ciudad', bold_with_color)
        worksheet.write(row + 1, 98, 'Estado', bold_with_color)
        worksheet.write(row + 1, 99, 'C.P.', bold_with_color)
        worksheet.write(row + 1, 100, 'Telefono', bold_with_color)
        worksheet.write(row + 1, 101, 'Extension', bold_with_color)
        worksheet.write(row + 1, 102, 'Fax', bold_with_color)
        worksheet.write(row + 1, 103, 'Tipo Cliente', bold_with_color)
        worksheet.write(row + 1, 104, 'Estado extranjero', bold_with_color)
        worksheet.write(row + 1, 105, 'Pais', bold_with_color)

        # TS Segment Header MX
        worksheet.write(row + 1, 106, 'Identificador', bold_with_color)
        worksheet.write(row + 1, 107, 'Numero de Compañias', bold_with_color)
        worksheet.write(row + 1, 108, 'Cantidad', bold_with_color)


        # EM Segment Index
        worksheet.write(row + 2, 1, 'EM', bold_with_color)
        worksheet.write(row + 2, 2, '00', index_style)
        worksheet.write(row + 2, 3, '01', index_style)
        worksheet.write(row + 2, 4, '02', index_style)
        worksheet.write(row + 2, 5, '03', index_style)
        worksheet.write(row + 2, 6, '04', index_style)
        worksheet.write(row + 2, 7, '05', index_style)
        worksheet.write(row + 2, 8, '06', index_style)
        worksheet.write(row + 2, 9, '07', index_style)
        worksheet.write(row + 2, 10, '08', index_style)
        worksheet.write(row + 2, 11, '09', index_style)
        worksheet.write(row + 2, 12, '10', index_style)
        worksheet.write(row + 2, 13, '11', index_style)
        worksheet.write(row + 2, 14, '12', index_style)
        worksheet.write(row + 2, 15, '13', index_style)
        worksheet.write(row + 2, 16, '14', index_style)
        worksheet.write(row + 2, 17, '15', index_style)
        worksheet.write(row + 2, 18, '16', index_style)
        worksheet.write(row + 2, 19, '17', index_style)
        worksheet.write(row + 2, 20, '18', index_style)
        worksheet.write(row + 2, 21, '19', index_style)
        worksheet.write(row + 2, 22, '20', index_style)
        worksheet.write(row + 2, 23, '21', index_style)
        worksheet.write(row + 2, 24, '22', index_style)
        worksheet.write(row + 2, 25, '23', index_style)
        worksheet.write(row + 2, 26, '24', index_style)
        worksheet.write(row + 2, 27, '25 ', index_style)
        worksheet.write(row + 2, 28, '26 ', index_style)

        # AC Segment Index
        worksheet.write(row + 2, 29, 'AC', bold_with_color)
        worksheet.write(row + 2, 30, '00', index_style)
        worksheet.write(row + 2, 31, '01', index_style)
        worksheet.write(row + 2, 32, '02', index_style)
        worksheet.write(row + 2, 33, '03', index_style)
        worksheet.write(row + 2, 34, '04', index_style)
        worksheet.write(row + 2, 35, '05', index_style)
        worksheet.write(row + 2, 36, '06', index_style)
        worksheet.write(row + 2, 37, '07', index_style)
        worksheet.write(row + 2, 38, '08', index_style)
        worksheet.write(row + 2, 39, '09', index_style)
        worksheet.write(row + 2, 40, '10', index_style)
        worksheet.write(row + 2, 41, '11', index_style)
        worksheet.write(row + 2, 42, '12', index_style)
        worksheet.write(row + 2, 43, '13', index_style)
        worksheet.write(row + 2, 44, '14', index_style)
        worksheet.write(row + 2, 45, '15', index_style)
        worksheet.write(row + 2, 46, '16', index_style)
        worksheet.write(row + 2, 47, '17', index_style)
        worksheet.write(row + 2, 48, '18', index_style)
        worksheet.write(row + 2, 49, '19', index_style)
        worksheet.write(row + 2, 50, '20', index_style)
        worksheet.write(row + 2, 51, '21', index_style)

        # CR Segment Index
        worksheet.write(row + 2, 52, 'CR', bold_with_color)
        worksheet.write(row + 2, 53, '00', index_style)
        worksheet.write(row + 2, 54, '01', index_style)
        worksheet.write(row + 2, 55, '02', index_style)
        worksheet.write(row + 2, 56, '03', index_style)
        worksheet.write(row + 2, 57, '04', index_style)
        worksheet.write(row + 2, 58, '05', index_style)
        worksheet.write(row + 2, 59, '06', index_style)
        worksheet.write(row + 2, 60, '07', index_style)
        worksheet.write(row + 2, 61, '08', index_style)
        worksheet.write(row + 2, 62, '09', index_style)
        worksheet.write(row + 2, 63, '10', index_style)
        worksheet.write(row + 2, 64, '11', index_style)
        worksheet.write(row + 2, 65, '12', index_style)
        worksheet.write(row + 2, 66, '13', index_style)
        worksheet.write(row + 2, 67, '14', index_style)
        worksheet.write(row + 2, 68, '15', index_style)
        worksheet.write(row + 2, 69, '16', index_style)
        worksheet.write(row + 2, 70, '17', index_style)
        worksheet.write(row + 2, 71, '18', index_style)
        worksheet.write(row + 2, 72, '19', index_style)
        worksheet.write(row + 2, 73, '20', index_style)
        worksheet.write(row + 2, 74, '21', index_style)
        worksheet.write(row + 2, 75, '22', index_style)
        worksheet.write(row + 2, 76, '23', index_style)
        worksheet.write(row + 2, 77, '24', index_style)

        # DE Segment Index
        worksheet.write(row + 2, 78, 'DE', bold_with_color)
        worksheet.write(row + 2, 79, '00', index_style)
        worksheet.write(row + 2, 80, '01', index_style)
        worksheet.write(row + 2, 81, '02', index_style)
        worksheet.write(row + 2, 82, '03', index_style)
        worksheet.write(row + 2, 83, '04', index_style)

        # AV Segment Index
        worksheet.write(row + 2, 84, 'AV', bold_with_color)
        worksheet.write(row + 2, 85, '00', index_style)
        worksheet.write(row + 2, 86, '01', index_style)
        worksheet.write(row + 2, 87, '02', index_style)
        worksheet.write(row + 2, 88, '03.', index_style)
        worksheet.write(row + 2, 89, '04', index_style)
        worksheet.write(row + 2, 90, '05', index_style)
        worksheet.write(row + 2, 91, '06', index_style)
        worksheet.write(row + 2, 92, '07', index_style)
        worksheet.write(row + 2, 93, '08', index_style)
        worksheet.write(row + 2, 94, '09', index_style)
        worksheet.write(row + 2, 95, '10', index_style)
        worksheet.write(row + 2, 96, '11', index_style)
        worksheet.write(row + 2, 97, '12', index_style)
        worksheet.write(row + 2, 98, '13', index_style)
        worksheet.write(row + 2, 99, '14', index_style)
        worksheet.write(row + 2, 100, '15', index_style)
        worksheet.write(row + 2, 101, '16', index_style)
        worksheet.write(row + 2, 102, '17', index_style)
        worksheet.write(row + 2, 103, '18', index_style)
        worksheet.write(row + 2, 104, '19', index_style)
        worksheet.write(row + 2, 105, '20', index_style)

        # TS Segment Index
        worksheet.write(row + 2, 106, 'TS', bold_with_color)
        worksheet.write(row + 2, 107, '00', index_style)
        worksheet.write(row + 2, 108, '01', index_style)

        new_row = row+3

        amount_of_all_companies = []
        companies = []
        de_quantity_sum = []
        for partner in contact_to_generate_credit_report:
            if partner.credit_bureau_report_company_type and partner.credit_bureau_report:
                continue
            current_date = datetime.now()
            first_day_of_current_month = current_date.replace(day=1)
            last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
            unpaid_invoice_of_partner = partner.unpaid_invoice_ids
            filtered_till_previous_month_last_date = unpaid_invoice_of_partner.filtered(lambda x: x.invoice_date <= last_day_of_previous_month.date())
            number_of_unpaid_invoice = len(filtered_till_previous_month_last_date)
            present_year = current_date.date().year
            present_month = current_date.date().month
            partner_invoice = partner.invoice_ids.filtered(
                lambda x: x.move_type == 'out_invoice' and x.state == 'posted' and (
                    x.payment_state in ['not_paid', 'partial'] or
                    (
                        x.payment_state == 'paid' and x.payment_date and
                        (
                            (x.payment_date.month == present_month and x.payment_date.year == present_year) or
                            (x.payment_date.month == present_month - 1 and x.payment_date.year == present_year) or
                            (x.payment_date.month == 12 and x.payment_date.year == present_year - 1 and present_month == 1)
                        )
                    )
                )
            )

            paid_invoice = self.env['account.move'].search([('partner_id', '=', partner.id),
                                                            ('move_type', 'in', ['out_invoice']),
                                                            ('payment_state', '=', 'paid'),
                                                            ('state', '=', 'posted'), ('payment_date', '!=', False)])
            if partner.property_payment_term_id:
                partner_payment_terms = partner.property_payment_term_id._compute_terms(
                    date_ref=fields.Date.context_today(partner),
                    currency=partner.currency_id,
                    tax_amount_currency=0.0,
                    tax_amount=0.0,
                    untaxed_amount_currency=0.0,
                    untaxed_amount=0.0,
                    company=self.env.company,
                    sign=1
                )
                partner_payment_terms_max_dates = max([(i.get('date')) for i in partner_payment_terms.get('line_ids')]) - datetime.now().date()
                partner_payment_terms_max_dates_days = (partner_payment_terms_max_dates).days
            else:
                partner_payment_terms_max_dates_days = 0.0
            endorser_customer_for_current_partner = contact_to_generate_credit_report.filtered(
                lambda p: p.credit_bureau_report_company_type == 'endorser' and p.contact_related_id.id == partner.id)
            shareholder_customer_for_current_partner = contact_to_generate_credit_report.filtered(lambda
                                                                                                      p: p.credit_bureau_report_company_type == 'shareholder' and p.contact_related_id.id == partner.id)
            formatted_date_of_last_paid_invoice = ''
            if paid_invoice:
                last_paid_invoice_date = paid_invoice.sorted(key=lambda x: x.payment_date, reverse=True)[0].payment_date
                last_paid_invoice_d = last_paid_invoice_date.strftime('%d')
                last_paid_invoice_month = last_paid_invoice_date.strftime('%m')
                last_paid_invoice_year = last_paid_invoice_date.strftime('%Y')
                formatted_date_of_last_paid_invoice = f"{last_paid_invoice_d}{last_paid_invoice_month}{last_paid_invoice_year}"

            payment_terms = {}
            multiple_same_dues = {}
            invoice_due_date_calculate_from_first_day = {}
            account_invoice_date = {}
            for invoice in partner_invoice:
                payment_due_date = invoice.invoice_date_due

                if payment_due_date:
                    invoice_due_date_calculate_from_the_first_day_of_current_month = (first_day_of_current_month.date() - payment_due_date).days
                    days_diff_btwn_due_date_and_current_date = (now.date() - payment_due_date).days
                    if days_diff_btwn_due_date_and_current_date > 0:
                        payment_term_id = invoice.invoice_payment_term_id.id
                        total_amount_payment_term_wise = invoice.amount_residual_signed
                        status = invoice.payment_state
                        keyy = (days_diff_btwn_due_date_and_current_date, status)
                        if payment_term_id:
                            if invoice.payment_state in ['not_paid', 'partial'] and keyy not in payment_terms:
                                account_invoice_date[keyy] = 0
                            elif invoice.payment_state == 'paid' and keyy not in payment_terms:
                                account_invoice_date[keyy] = f"{invoice.payment_date.strftime('%d')}{invoice.payment_date.strftime('%m')}{invoice.payment_date.strftime('%Y')}"
                            invoice_due_date_calculate_from_first_day[
                                keyy] = invoice_due_date_calculate_from_the_first_day_of_current_month
                            if keyy not in payment_terms:
                                payment_terms[
                                    keyy] = total_amount_payment_term_wise
                                multiple_same_dues[keyy] = 1
                            else:
                                payment_terms[
                                    keyy] += total_amount_payment_term_wise
                                multiple_same_dues[keyy] += 1


            default_dict = {0: 0}
            dates_of_invoice_paid = account_invoice_date if account_invoice_date else default_dict
            days_and_amount_of_dues = payment_terms if payment_terms else default_dict
            for values in range(len(days_and_amount_of_dues)):
                due_date_first_row = list(days_and_amount_of_dues.items())[0][0]
                de_overdue_days = list(days_and_amount_of_dues.items())[values][0]
                de_quantity = list(days_and_amount_of_dues.items())[values][1]


                # EM Segment Values
                worksheet.write(new_row, 1, 'EM', size_for_main_text)
                worksheet.write(new_row, 2, partner.vat.upper() if partner.vat else '', size_for_main_text)
                worksheet.write(new_row, 3, partner.l10n_mx_edi_curp.upper() if partner.l10n_mx_edi_curp else '', size_for_main_text)
                worksheet.data_validation(new_row, 3, new_row, 3, self.get_length_validation(18))
                worksheet.write(new_row, 4, '', size_for_main_text)
                worksheet.data_validation(new_row, 4, new_row, 4, self.get_length_validation(10))
                worksheet.data_validation(new_row, 4, new_row, 4, self.get_numeric_validation(9999999999))
                worksheet.write(new_row, 5, f"{partner.name.upper()} {partner.legal_person_id.name.upper()}" if partner.name and partner.legal_person_id and partner.setu_company_type == 'legal' else '', size_for_main_text)
                worksheet.data_validation(new_row, 5, new_row, 5, self.get_length_validation(150))
                worksheet.write(new_row, 6, partner.name1.upper() if partner.name1 and partner.setu_company_type == 'pisical' else '', size_for_main_text)
                worksheet.data_validation(new_row, 6, new_row, 6, self.get_length_validation(30))
                worksheet.write(new_row, 7, partner.name2.upper() if partner.name2 and partner.setu_company_type == 'pisical' else '', size_for_main_text)
                worksheet.data_validation(new_row, 7, new_row, 7, self.get_length_validation(30))
                worksheet.write(new_row, 8, partner.last_name.upper() if partner.last_name and partner.setu_company_type == 'pisical' else '', size_for_main_text)
                worksheet.data_validation(new_row, 8, new_row, 8, self.get_length_validation(25))
                worksheet.write(new_row, 9, partner.mother_last_name.upper() if partner.mother_last_name and partner.setu_company_type == 'pisical' else '', size_for_main_text)
                worksheet.data_validation(new_row, 9, new_row, 9, self.get_length_validation(25))
                worksheet.write(new_row, 10, partner.country_id.code.upper() if partner.country_id else '', size_for_main_text)
                worksheet.data_validation(new_row, 10, new_row, 10, self.get_length_validation(2))
                worksheet.write(new_row, 11, '', size_for_main_text)
                worksheet.data_validation(new_row, 11, new_row, 11, self.get_length_validation(2))
                worksheet.write(new_row, 12, '88888888', size_for_main_text)
                worksheet.write(new_row, 13, '', size_for_main_text)
                worksheet.data_validation(new_row, 13, new_row, 13, self.get_length_validation(11))
                worksheet.data_validation(new_row, 13, new_row, 13, self.get_numeric_validation(99999999999))
                worksheet.write(new_row, 14, '', size_for_main_text)
                worksheet.data_validation(new_row, 14, new_row, 14, self.get_length_validation(11))
                worksheet.data_validation(new_row, 14, new_row, 14, self.get_numeric_validation(99999999999))
                worksheet.write(new_row, 15, f'{partner.street_name.upper()} {partner.street_number.upper()}' if partner.street_name and partner.street_number else '', size_for_main_text)
                worksheet.write(new_row, 16, '', size_for_main_text)
                worksheet.data_validation(new_row, 16, new_row, 16, self.get_length_validation(40))
                worksheet.write(new_row, 17, partner.l10n_mx_edi_colony.upper() if partner.l10n_mx_edi_colony else '', size_for_main_text)
                worksheet.data_validation(new_row, 17, new_row, 17, self.get_length_validation(60))
                worksheet.write(new_row, 18, partner.l10n_mx_edi_locality_id.name.upper() if partner.l10n_mx_edi_locality_id else '', size_for_main_text)
                worksheet.data_validation(new_row, 18, new_row, 18, self.get_length_validation(40))
                worksheet.write(new_row, 19, partner.city.upper() if partner.city else '', size_for_main_text)
                worksheet.data_validation(new_row, 19, new_row, 19, self.get_length_validation(40))
                worksheet.write(new_row, 20, partner.state_id.code if partner.state_id else '', size_for_main_text)
                worksheet.data_validation(new_row, 20, new_row, 20, self.get_length_validation(4))
                worksheet.write(new_row, 21, partner.postal_code_id.postal_code if partner.postal_code_id else '', size_for_main_text)
                worksheet.data_validation(new_row, 21, new_row, 21, self.get_length_validation(10))
                worksheet.write(new_row, 22, partner.phone if partner.phone else '', size_for_main_text)
                worksheet.data_validation(new_row, 22, new_row, 22, self.get_length_validation(11))
                worksheet.write(new_row, 23, '', size_for_main_text)
                worksheet.data_validation(new_row, 23, new_row, 23, self.get_length_validation(8))
                worksheet.write(new_row, 24, '', size_for_main_text)
                worksheet.data_validation(new_row, 24, new_row, 24, self.get_length_validation(11))
                if partner.setu_company_type:
                    worksheet.write(new_row, 25, '1' if partner.setu_company_type == 'legal' else '2',
                                    size_for_main_text)
                else:
                    worksheet.write(new_row, 25, '', size_for_main_text)
                worksheet.data_validation(new_row, 25, new_row, 25, self.get_length_validation(1))
                worksheet.write(new_row, 26, '', size_for_main_text)
                worksheet.data_validation(new_row, 26, new_row, 26, self.get_length_validation(40))
                worksheet.write(new_row, 27, partner.country_id.code.upper() if partner.country_id else '', size_for_main_text)
                worksheet.data_validation(new_row, 27, new_row, 27, self.get_length_validation(2))
                worksheet.write(new_row, 28, '', size_for_main_text)
                worksheet.data_validation(new_row, 28, new_row, 28, self.get_length_validation(8))
                worksheet.data_validation(new_row, 28, new_row, 28, self.get_numeric_validation(99999999))

                # AC Segment Values
                worksheet.write(new_row, 29, 'AC', size_for_main_text)

                worksheet.data_validation(new_row, 31, new_row, 31, self.get_length_validation(18))
                worksheet.data_validation(new_row, 32, new_row, 32, self.get_length_validation(10))
                worksheet.data_validation(new_row, 32, new_row, 32, self.get_numeric_validation(9999999999))
                worksheet.data_validation(new_row, 38, new_row, 38, self.get_length_validation(2))
                worksheet.data_validation(new_row, 38, new_row, 38, self.get_numeric_validation(99))
                worksheet.data_validation(new_row, 39, new_row, 39, self.get_length_validation(40))
                worksheet.data_validation(new_row, 40, new_row, 40, self.get_length_validation(40))
                worksheet.data_validation(new_row, 41, new_row, 41, self.get_length_validation(60))
                worksheet.data_validation(new_row, 42, new_row, 42, self.get_length_validation(40))
                worksheet.data_validation(new_row, 43, new_row, 43, self.get_length_validation(40))
                worksheet.data_validation(new_row, 44, new_row, 44, self.get_length_validation(4))
                worksheet.data_validation(new_row, 45, new_row, 45, self.get_length_validation(10))
                worksheet.data_validation(new_row, 46, new_row, 46, self.get_length_validation(11))
                worksheet.data_validation(new_row, 47, new_row, 47, self.get_length_validation(8))
                worksheet.data_validation(new_row, 48, new_row, 48, self.get_length_validation(11))
                worksheet.data_validation(new_row, 49, new_row, 49, self.get_length_validation(1))
                worksheet.data_validation(new_row, 50, new_row, 50, self.get_length_validation(40))
                worksheet.data_validation(new_row, 51, new_row, 51, self.get_length_validation(2))
                if shareholder_customer_for_current_partner:
                    worksheet.write(new_row, 30, shareholder_customer_for_current_partner[0].vat.upper() if shareholder_customer_for_current_partner[0].vat else '', size_for_main_text)
                    worksheet.write(new_row, 31, shareholder_customer_for_current_partner[0].l10n_mx_edi_curp.upper() if shareholder_customer_for_current_partner[0].l10n_mx_edi_curp else '', size_for_main_text)
                    worksheet.write(new_row, 33, f"{shareholder_customer_for_current_partner[0].contact_related_id.name.upper()} {shareholder_customer_for_current_partner[0].contact_related_id.legal_person_id.name.upper()}" if shareholder_customer_for_current_partner[0].contact_related_id and shareholder_customer_for_current_partner[0].contact_related_id.name and shareholder_customer_for_current_partner[0].contact_related_id.legal_person_id and shareholder_customer_for_current_partner[0].contact_related_id.setu_company_type == 'legal' else '', size_for_main_text)
                    worksheet.write(new_row, 34, shareholder_customer_for_current_partner[0].ac_name1.upper() if shareholder_customer_for_current_partner[0].ac_name1 else '', size_for_main_text)
                    worksheet.write(new_row, 35, shareholder_customer_for_current_partner[0].ac_name2.upper() if shareholder_customer_for_current_partner[0].ac_name2 else '', size_for_main_text)
                    worksheet.write(new_row, 36, shareholder_customer_for_current_partner[0].ac_last_name.upper() if shareholder_customer_for_current_partner[0].ac_last_name else '', size_for_main_text)
                    worksheet.write(new_row, 37, shareholder_customer_for_current_partner[0].ac_mother_last_name.upper() if shareholder_customer_for_current_partner[0].ac_mother_last_name else '', size_for_main_text)
                    worksheet.write(new_row, 38, shareholder_customer_for_current_partner[0].percent if shareholder_customer_for_current_partner[0].percent else '', size_for_main_text)
                    worksheet.write(new_row, 39, f'{shareholder_customer_for_current_partner[0].street_name.upper()} {shareholder_customer_for_current_partner[0].street_number.upper()}' if shareholder_customer_for_current_partner[0].street_name and shareholder_customer_for_current_partner[0].street_number else '', size_for_main_text)
                    worksheet.write(new_row, 40, shareholder_customer_for_current_partner[0].ac_address2.upper() if shareholder_customer_for_current_partner[0].ac_address2 else '', size_for_main_text)
                    worksheet.write(new_row, 41, shareholder_customer_for_current_partner[0].l10n_mx_edi_colony.upper() if shareholder_customer_for_current_partner[0].l10n_mx_edi_colony else '', size_for_main_text)
                    worksheet.write(new_row, 42, shareholder_customer_for_current_partner[0].l10n_mx_edi_locality_id.name.upper() if shareholder_customer_for_current_partner[0].l10n_mx_edi_locality_id else '', size_for_main_text)
                    worksheet.write(new_row, 43, shareholder_customer_for_current_partner[0].city.upper() if shareholder_customer_for_current_partner[0].city else '', size_for_main_text)
                    worksheet.write(new_row, 44, shareholder_customer_for_current_partner[0].state_id.code if shareholder_customer_for_current_partner[0].state_id else '', size_for_main_text)
                    worksheet.write(new_row, 45, shareholder_customer_for_current_partner[0].postal_code_id.postal_code if shareholder_customer_for_current_partner[0].postal_code_id else '', size_for_main_text)
                    worksheet.write(new_row, 46, shareholder_customer_for_current_partner[0].phone if shareholder_customer_for_current_partner[0].phone else '', size_for_main_text)

                    if shareholder_customer_for_current_partner[0].setu_company_type:
                        worksheet.write(new_row, 49, '1' if shareholder_customer_for_current_partner[
                                                                0].setu_company_type == 'legal' else '2',
                                        size_for_main_text)
                    else:
                        worksheet.write(new_row, 49, '', size_for_main_text)
                    worksheet.write(new_row, 51, shareholder_customer_for_current_partner[0].country_id.code.upper() if
                    shareholder_customer_for_current_partner[0].country_id else '', size_for_main_text)

                else:
                    worksheet.write(new_row, 30, '', size_for_main_text)
                    worksheet.write(new_row, 31, '', size_for_main_text)
                    worksheet.write(new_row, 33, '', size_for_main_text)
                    worksheet.write(new_row, 34, '', size_for_main_text)
                    worksheet.write(new_row, 35, '', size_for_main_text)
                    worksheet.write(new_row, 36, '', size_for_main_text)
                    worksheet.write(new_row, 37, '', size_for_main_text)
                    worksheet.write(new_row, 38, '', size_for_main_text)
                    worksheet.write(new_row, 39, '', size_for_main_text)
                    worksheet.write(new_row, 40, '', size_for_main_text)
                    worksheet.write(new_row, 41, '', size_for_main_text)
                    worksheet.write(new_row, 42, '', size_for_main_text)
                    worksheet.write(new_row, 43, '', size_for_main_text)
                    worksheet.write(new_row, 44, '', size_for_main_text)
                    worksheet.write(new_row, 45, '', size_for_main_text)
                    worksheet.write(new_row, 46, '', size_for_main_text)
                    worksheet.write(new_row, 49, '', size_for_main_text)
                    worksheet.write(new_row, 51, '', size_for_main_text)

                worksheet.write(new_row, 32, '', size_for_main_text)
                worksheet.write(new_row, 47, '', size_for_main_text)
                worksheet.write(new_row, 48, '', size_for_main_text)
                worksheet.write(new_row, 50, '', size_for_main_text)


                # CR Segment Values
                worksheet.write(new_row, 52, 'CR', size_for_main_text)
                worksheet.write(new_row, 53, partner.vat.upper() if partner.vat else '', size_for_main_text)
                worksheet.write(new_row, 54, multiple_same_dues.get(de_overdue_days, 0), size_for_main_text)
                worksheet.write(new_row, 55, '', size_for_main_text)
                worksheet.data_validation(new_row, 55, new_row, 55, self.get_length_validation(25))
                worksheet.write(new_row, 56, '', size_for_main_text)
                worksheet.data_validation(new_row, 56, new_row, 56, self.get_length_validation(25))
                worksheet.write(new_row, 57, '', size_for_main_text)
                worksheet.data_validation(new_row, 57, new_row, 57, self.get_length_validation(8))
                worksheet.write(new_row, 58, round(partner_payment_terms_max_dates_days / 30.4, 2), size_for_main_text)
                worksheet.data_validation(new_row, 58, new_row, 58, self.get_length_validation(6))
                worksheet.data_validation(new_row, 58, new_row, 58, self.get_numeric_validation(999999))
                worksheet.write(new_row, 59, '',size_for_main_text)
                worksheet.data_validation(new_row, 59, new_row, 59, self.get_length_validation(4))
                worksheet.data_validation(new_row, 59, new_row, 59, self.get_numeric_validation(9999))
                worksheet.write(new_row, 60, '', size_for_main_text)
                worksheet.data_validation(new_row, 60, new_row, 60, self.get_length_validation(20))
                worksheet.data_validation(new_row, 60, new_row, 60, self.get_numeric_validation(99999999999999999999))
                worksheet.write(new_row, 61, '1', size_for_main_text)
                worksheet.write(new_row, 62, '', size_for_main_text)
                worksheet.data_validation(new_row, 62, new_row, 62, self.get_length_validation(4))
                worksheet.data_validation(new_row, 62, new_row, 62, self.get_numeric_validation(9999))
                worksheet.write(new_row, 63, '7', size_for_main_text)
                worksheet.write(new_row, 64, sum([round(value) for value in days_and_amount_of_dues.values()]) if list(dates_of_invoice_paid.values())[values] == 0 else '0', size_for_main_text)
                worksheet.data_validation(new_row, 64, new_row, 64, self.get_length_validation(20))
                worksheet.data_validation(new_row, 64, new_row, 64, self.get_numeric_validation(99999999999999999999))
                worksheet.write(new_row, 65, dates_of_invoice_paid.get(de_overdue_days, 0), size_for_main_text)
                worksheet.data_validation(new_row, 65, new_row, 65, self.get_length_validation(8))
                worksheet.data_validation(new_row, 65, new_row, 65, self.get_numeric_validation(99999999))
                worksheet.write(new_row, 66, '', size_for_main_text)
                worksheet.data_validation(new_row, 66, new_row, 66, self.get_length_validation(8))
                worksheet.data_validation(new_row, 66, new_row, 66, self.get_numeric_validation(99999999))
                worksheet.write(new_row, 67, '', size_for_main_text)
                worksheet.data_validation(new_row, 67, new_row, 67, self.get_length_validation(20))
                worksheet.data_validation(new_row, 67, new_row, 67, self.get_numeric_validation(99999999999999999999))
                worksheet.write(new_row, 68, partner.liquidation_date if partner.liquidation_date else '', size_for_main_text)
                worksheet.data_validation(new_row, 68, new_row, 68, self.get_length_validation(8))
                worksheet.data_validation(new_row, 68, new_row, 68, self.get_numeric_validation(99999999))
                worksheet.write(new_row, 69, partner.debt_discount if partner.debt_discount else '', size_for_main_text)
                worksheet.data_validation(new_row, 69, new_row, 69, self.get_length_validation(20))
                worksheet.data_validation(new_row, 69, new_row, 69, self.get_numeric_validation(99999999999999999999))
                worksheet.write(new_row, 70, partner.datio_in_solutum if partner.datio_in_solutum else '', size_for_main_text)
                worksheet.data_validation(new_row, 70, new_row, 70, self.get_length_validation(20))
                worksheet.data_validation(new_row, 70, new_row, 70, self.get_numeric_validation(99999999999999999999))
                worksheet.write(new_row, 71, partner.debt_condonation if partner.debt_condonation else '', size_for_main_text)
                worksheet.data_validation(new_row, 71, new_row, 71, self.get_length_validation(20))
                worksheet.data_validation(new_row, 71, new_row, 71, self.get_numeric_validation(99999999999999999999))
                worksheet.write(new_row, 72, partner.observations if partner.observations else '', size_for_main_text)
                worksheet.data_validation(new_row, 72, new_row, 72, self.get_length_validation(4))
                worksheet.write(new_row, 73, partner.special_credit if partner.special_credit else '', size_for_main_text)
                worksheet.data_validation(new_row, 73, new_row, 73, self.get_length_validation(1))
                worksheet.write(new_row, 74, '', size_for_main_text)
                worksheet.data_validation(new_row, 74, new_row, 74, self.get_length_validation(8))
                worksheet.data_validation(new_row, 74, new_row, 74, self.get_numeric_validation(99999999))
                worksheet.write(new_row, 75, '', size_for_main_text)
                worksheet.data_validation(new_row, 75, new_row, 75, self.get_length_validation(20))
                worksheet.data_validation(new_row, 75, new_row, 75, self.get_numeric_validation(99999999999999999999))
                worksheet.write(new_row, 76, '', size_for_main_text)
                worksheet.data_validation(new_row, 76, new_row, 76, self.get_length_validation(8))
                worksheet.data_validation(new_row, 76, new_row, 76, self.get_numeric_validation(99999999))
                worksheet.write(new_row, 77, '', size_for_main_text)
                worksheet.data_validation(new_row, 77, new_row, 77, self.get_length_validation(20))
                worksheet.data_validation(new_row, 77, new_row, 77, self.get_numeric_validation(99999999999999999999))

                # DE Segment Values
                worksheet.write(new_row, 78, 'DE', size_for_main_text)
                worksheet.write(new_row, 79, partner.vat.upper() if partner.vat else '', size_for_main_text)
                worksheet.write(new_row, 80, '', size_for_main_text)
                worksheet.data_validation(new_row, 80, new_row, 80, self.get_length_validation(25))
                worksheet.data_validation(new_row, 80, new_row, 80, self.get_numeric_validation(9999999999999999999999999))
                worksheet.write(new_row, 81, invoice_due_date_calculate_from_first_day.get(de_overdue_days, 0) if list(dates_of_invoice_paid.values())[values] == 0 else '0', size_for_main_text)
                worksheet.data_validation(new_row, 81, new_row, 81, self.get_length_validation(3))
                worksheet.data_validation(new_row, 81, new_row, 81, self.get_numeric_validation(999))
                worksheet.write(new_row, 82, round(de_quantity, 0) if list(dates_of_invoice_paid.values())[values] == 0 else '0', size_for_main_text)
                worksheet.data_validation(new_row, 82, new_row, 82, self.get_length_validation(20))
                worksheet.data_validation(new_row, 82, new_row, 82, self.get_numeric_validation(99999999999999999999))
                worksheet.write(new_row, 83, '', size_for_main_text)
                worksheet.data_validation(new_row, 83, new_row, 83, self.get_length_validation(20))
                worksheet.data_validation(new_row, 83, new_row, 83, self.get_numeric_validation(99999999999999999999))

                # AV Segment Values
                worksheet.write(new_row, 84, 'AV', size_for_main_text)

                worksheet.data_validation(new_row, 85, new_row, 85, self.get_length_validation(13))
                worksheet.data_validation(new_row, 86, new_row, 86, self.get_length_validation(18))
                worksheet.data_validation(new_row, 87, new_row, 87, self.get_length_validation(10))
                worksheet.data_validation(new_row, 87, new_row, 87, self.get_numeric_validation(9999999999))
                worksheet.data_validation(new_row, 88, new_row, 88, self.get_length_validation(150))
                worksheet.data_validation(new_row, 89, new_row, 89, self.get_length_validation(30))
                worksheet.data_validation(new_row, 90, new_row, 90, self.get_length_validation(30))
                worksheet.data_validation(new_row, 91, new_row, 91, self.get_length_validation(25))
                worksheet.data_validation(new_row, 92, new_row, 92, self.get_length_validation(25))
                worksheet.data_validation(new_row, 93, new_row, 93, self.get_length_validation(40))
                worksheet.data_validation(new_row, 94, new_row, 94, self.get_length_validation(40))
                worksheet.data_validation(new_row, 95, new_row, 95, self.get_length_validation(60))
                worksheet.data_validation(new_row, 96, new_row, 96, self.get_length_validation(40))
                worksheet.data_validation(new_row, 97, new_row, 97, self.get_length_validation(40))
                worksheet.data_validation(new_row, 98, new_row, 98, self.get_length_validation(4))
                worksheet.data_validation(new_row, 99, new_row, 99, self.get_length_validation(10))
                worksheet.data_validation(new_row, 100, new_row, 100, self.get_length_validation(11))
                worksheet.data_validation(new_row, 101, new_row, 101, self.get_length_validation(8))
                worksheet.data_validation(new_row, 102, new_row, 102, self.get_length_validation(11))
                worksheet.data_validation(new_row, 104, new_row, 104, self.get_length_validation(40))
                worksheet.data_validation(new_row, 105, new_row, 105, self.get_length_validation(2))

                if endorser_customer_for_current_partner:
                    worksheet.write(new_row, 85, endorser_customer_for_current_partner[0].vat.upper() if endorser_customer_for_current_partner[0].vat else '', size_for_main_text)
                    worksheet.write(new_row, 86, endorser_customer_for_current_partner[0].l10n_mx_edi_curp.upper() if endorser_customer_for_current_partner[0].l10n_mx_edi_curp else '', size_for_main_text)
                    worksheet.write(new_row, 88, f"{endorser_customer_for_current_partner[0].name.upper()} {endorser_customer_for_current_partner[0].legal_person_id.name.upper()}" if endorser_customer_for_current_partner[0].name and endorser_customer_for_current_partner[0].legal_person_id and endorser_customer_for_current_partner[0].contact_related_id.setu_company_type == 'legal' else '', size_for_main_text)
                    worksheet.write(new_row, 89, f"{endorser_customer_for_current_partner[0].av_name1.upper()} {endorser_customer_for_current_partner[0].av_last_name.upper()}" if endorser_customer_for_current_partner[0].av_name1 and endorser_customer_for_current_partner[0].av_last_name and endorser_customer_for_current_partner[0].contact_related_id and endorser_customer_for_current_partner[0].contact_related_id.setu_company_type == 'pisical' else '', size_for_main_text)
                    worksheet.write(new_row, 90, endorser_customer_for_current_partner[0].av_name2.upper() if endorser_customer_for_current_partner[0].av_name2 else '', size_for_main_text)
                    worksheet.write(new_row, 91, endorser_customer_for_current_partner[0].av_last_name.upper() if endorser_customer_for_current_partner[0].av_last_name else '', size_for_main_text)
                    worksheet.write(new_row, 92, endorser_customer_for_current_partner[0].av_mother_last_name.upper() if endorser_customer_for_current_partner[0].av_mother_last_name else '', size_for_main_text)
                    worksheet.write(new_row, 93, f'{endorser_customer_for_current_partner[0].street_name.upper()} {endorser_customer_for_current_partner[0].street_number.upper()}' if endorser_customer_for_current_partner[0].street_name and endorser_customer_for_current_partner[0].street_number else '', size_for_main_text)
                    worksheet.write(new_row, 94, endorser_customer_for_current_partner[0].av_address2.upper() if endorser_customer_for_current_partner[0].av_address2 else '', size_for_main_text)
                    worksheet.write(new_row, 95, endorser_customer_for_current_partner[0].l10n_mx_edi_colony.upper() if endorser_customer_for_current_partner[0].l10n_mx_edi_colony else '', size_for_main_text)
                    worksheet.write(new_row, 96, endorser_customer_for_current_partner[0].l10n_mx_edi_locality_id.name.upper() if endorser_customer_for_current_partner[0].l10n_mx_edi_locality_id else '', size_for_main_text)
                    worksheet.write(new_row, 97, endorser_customer_for_current_partner[0].city.upper() if endorser_customer_for_current_partner[0].city else '', size_for_main_text)
                    worksheet.write(new_row, 98, endorser_customer_for_current_partner[0].state_id.code if endorser_customer_for_current_partner[0].state_id else '', size_for_main_text)
                    worksheet.write(new_row, 99, endorser_customer_for_current_partner[0].postal_code_id.postal_code if endorser_customer_for_current_partner[0].postal_code_id else '', size_for_main_text)
                    worksheet.write(new_row, 100, endorser_customer_for_current_partner[0].phone if endorser_customer_for_current_partner[0].phone else '', size_for_main_text)
                    worksheet.write(new_row, 103, '1' if endorser_customer_for_current_partner[0].legal_person_id else '2', size_for_main_text)
                    worksheet.write(new_row, 105, endorser_customer_for_current_partner[0].country_id.code.upper() if endorser_customer_for_current_partner[0].country_id else '', size_for_main_text)
                else:
                    worksheet.write(new_row, 85, '', size_for_main_text)
                    worksheet.write(new_row, 86, '', size_for_main_text)
                    worksheet.write(new_row, 88, '', size_for_main_text)
                    worksheet.write(new_row, 89, '', size_for_main_text)
                    worksheet.write(new_row, 90, '', size_for_main_text)
                    worksheet.write(new_row, 91, '', size_for_main_text)
                    worksheet.write(new_row, 92, '', size_for_main_text)
                    worksheet.write(new_row, 93, '', size_for_main_text)
                    worksheet.write(new_row, 94, '', size_for_main_text)
                    worksheet.write(new_row, 95, '', size_for_main_text)
                    worksheet.write(new_row, 96, '', size_for_main_text)
                    worksheet.write(new_row, 97, '', size_for_main_text)
                    worksheet.write(new_row, 98, '', size_for_main_text)
                    worksheet.write(new_row, 99, '', size_for_main_text)
                    worksheet.write(new_row, 100, '', size_for_main_text)
                    worksheet.write(new_row, 103, '', size_for_main_text)
                    worksheet.write(new_row, 105, '', size_for_main_text)

                worksheet.write(new_row, 87, '', size_for_main_text)
                worksheet.write(new_row, 101, '', size_for_main_text)
                worksheet.write(new_row, 102, '', size_for_main_text)
                worksheet.write(new_row, 104, '', size_for_main_text)

                # TS Segment Values
                worksheet.write(new_row, 106, '', size_for_main_text)
                worksheet.write(new_row, 107, '', size_for_main_text)
                worksheet.write(new_row, 108, '', size_for_main_text)
                de_quantity_sum.append(round(de_quantity, 0))
                companies.append(partner.vat)
                amount_of_all_companies.append(sum(payment_terms.values()))
                new_row += 1
        worksheet.write(new_row - 1, 106, 'TS', size_for_main_text)
        worksheet.write(new_row - 1, 107, len(set(companies)), size_for_main_text)
        worksheet.write(new_row - 1, 108, round(sum(de_quantity_sum)), size_for_main_text)

        workbook.close()
        data.seek(0)
        file_data = base64.encodebytes(data.read())
        self.write({'datas': file_data})
        data.close()

        return {
            'name': 'Credit Bureau Report',
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=credit.bureau.report.wiz&id=%s&field=datas&filename=Credit_bureau_report.xlsx&download=true' % (
                self.id),
            'target': 'self',
        }
