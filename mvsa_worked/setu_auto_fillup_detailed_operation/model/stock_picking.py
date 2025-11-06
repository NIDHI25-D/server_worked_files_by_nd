from odoo import models,fields,_
import base64
import csv
from io import StringIO, BytesIO
from csv import DictReader
from csv import DictWriter
from odoo.exceptions import ValidationError


class AutoFillupDetailedOperation(models.TransientModel):

    _name = 'auto_fillup.detailed_operation'
    _description = 'Auto fillup detailed operation'

    attachment_xml_file = fields.Binary(string="Attach File")
    file_name = fields.Char("File Name")

    def import_csv(self):
        """
            Author: siddharth.vasani@setuconsulting.com
            Date: 16/01/25
            Task: Migration to v18 from v16
            Purpose: This method is used to create a record in stock.picking(detailed operation) of the products mentioned in the csv file.
                     also fixed the issues which throw an error related to no quantity or non digit quantity and same issues with other columns to get it from file.
            Procedure: A csv file should be created with the same column name mention in method.
                       For lot/serial number file should have new numbers otherwise it will raise error.
                       reference_name,product_sku,destination_location should already have a record.Validation related to the condition will be raise.
            NOTE :     Boolean "No negative stock" should be disable otherwise it will give error of no stock for the new lot/serial.
                       Enable detailed operation from Operation Type. For lot/serial to view it should be Operation Type: Delivery Orders as we set lot_id
        """
        if not self.file_name:
            raise ValidationError(_('Please select attachment first.'))
        extention = self.file_name.split('.')
        if 'csv' not in extention:
            raise ValidationError(_('File must be in csv format.'))

        import_file = BytesIO(base64.decodebytes(self.attachment_xml_file))
        csvf = StringIO(import_file.read().decode())
        reader = csv.DictReader(csvf, delimiter=',')
        product_ref_list = []
        for line in reader:
            serial_number_record = False
            ref = line.get('reference_name')
            sku = line.get('product_sku')
            loc = line.get('destination_location')
            qun = line.get('quantity')
            serial_num = line.get('lot_serial_number')
            picking_id = self.env['stock.picking']
            if ref:
                picking_id = picking_id.search([('name','=',ref)])
            product_id = self.env['product.product']
            if sku:
                product_id = product_id.search([('default_code','=like',sku)])
            location_id = self.env['stock.location']
            if loc:
                location_id = location_id.search([('complete_name','=',loc)])
            pro_from_serial_id = self.env['stock.lot'].search([('name','=like',serial_num)])
            ser_num_record = self.env['stock.lot'].search([]).mapped('name')

            if not qun or not qun.isdigit():
                raise ValidationError(_('The quantity in the file are not correct please add correct one.'))

            if product_id and serial_num != '' and serial_num and serial_num not in  ser_num_record:
                if product_id.tracking == 'none':
                    raise ValidationError(
                        _('The sku of product you have entered , configured tracking as none.' % (
                         serial_num)))
                if product_id.tracking == 'serial':
                    if int(qun)> 1:
                        raise ValidationError(
                            _('Serial nunmber is unique for each quantity of product , so you have to enter'
                              ' single quntity in csv sheet if configured tracking base on serial number '))
                    else:
                        create_new_serial_number = self.env['stock.lot'].create({'name':serial_num,
                                                                                            'product_id': product_id.id,
                                                                                            'company_id':picking_id.company_id.id})
                        serial_number_record = create_new_serial_number
                if product_id.tracking == 'lot':
                    create_new_serial_number = self.env['stock.lot'].create({'name': serial_num,
                                                                                        'product_id': product_id.id,
                                                                                        'company_id':picking_id.company_id.id})
                    serial_number_record = create_new_serial_number

            if not picking_id:
                raise ValidationError(_('The reference_name %s you have entered is not found.' % (ref)))
            if not product_id and not pro_from_serial_id.product_id:
                raise ValidationError(_('The sku %s or lot_serial_number %s you have entered in the picking name %s is wrong or not set value in sheet. ' % (sku,serial_num,ref)))
            if pro_from_serial_id.product_id and not product_id:
                raise ValidationError(
                    _('The sku %s you have entered in the picking name %s is wrong or not set in sheet. ' % (
                    sku, ref)))
            if product_id and pro_from_serial_id.product_id and product_id != pro_from_serial_id.product_id:
                raise ValidationError(_('The sku %s and sku of product configured in lot_serial_number %s in the picking name %s is not same.' % (sku,serial_num,ref)))
            if not location_id:
                raise ValidationError(_('The destination_location %s you have entered is not found.' % (loc)))
            if product_id.tracking == 'serial' and serial_num in  ser_num_record:
                raise ValidationError(_('The serial number [%s] has already been assigned.' % (serial_num)))
            # if product_id.tracking == 'lot' and serial_num in  ser_num_record:
            #     raise ValidationError(_('The lot number [%s] has already been assigned.' % (serial_num)))
            location_dest_id = picking_id.location_dest_id
            location_id_with_same_parent_location = location_id.filtered(lambda location:location.location_id == location_dest_id)

            picking_id.write({'move_line_ids_without_package':[(0,0,{'product_id':  pro_from_serial_id.product_id.id if pro_from_serial_id.product_id and  product_id == pro_from_serial_id.product_id  else product_id.id,
                                                               'location_dest_id': location_id.id if len(location_id) == 1 else location_id_with_same_parent_location.id ,
                                                               'lot_id': pro_from_serial_id.id if pro_from_serial_id else serial_number_record.id if serial_number_record else False,
                                                               'qty_done':int(qun),
                                                               'product_uom_id':pro_from_serial_id.product_id.uom_id.id if pro_from_serial_id.product_id and  product_id == pro_from_serial_id.product_id  else product_id.uom_id.id,
                                                               'location_id':picking_id.location_id.id})]})

            if ref not in product_ref_list:
                product_ref_list.append(ref)
                self.env['ir.attachment'].sudo().with_context(
                    binary_field_real_user=self.env.user,
                ).create([{
                    'name': self.file_name,
                    'res_model': 'stock.picking',
                    # 'res_field': self.name,
                    'res_id': picking_id.id,
                    'type': 'binary',
                    'datas': self.attachment_xml_file,
                }])
                body = 'File attached'
                picking_id.message_post(body=body)
        pass


