##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models

import logging

_logger = logging.getLogger(__name__)

class sale_advance_payment_inv(models.TransientModel):
    
    _name = "sale.advance.payment.inv"
    _inherit = "sale.advance.payment.inv"    

    def _create_invoices(self, cr, uid, inv_values, sale_id, context=None):
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        sale_obj = self.pool.get('sale.order')
        invoice_id = super(sale_advance_payment_inv,self)._create_invoices(
                                    cr, uid, inv_values, sale_id, context=None)
        # write advance invoice flag to created invoice
        new_data = {'adv_inv': True}
        # get the tax_id(s) on separate lines        
        inv_line = inv_obj.read(cr, uid, [invoice_id],['invoice_line'])[0]
        inv_line_id = inv_line['invoice_line']
        il_o = inv_line_obj.browse(cr, uid, inv_line_id, context=context)
        i_line = {
            'name': il_o.name,
            'origin': il_o.origin,
            'account_id': il_o.account_id.id,
            'price_unit': il_o.price_unit,
            'quantity': il_o.quantity,            
            'uos_id': il_o.uos_id.id,
            'product_id': il_o.product_id.id,
            'invoice_line_tax_id': il_o.invoice_line_tax_id.id,
            'account_analytic_id': il_o.account_analytic_id.id,
        }         
        so_o = sale_obj.browse(cr, uid, sale_id, context=context)        
        new_data['invoice_line'] = [(3, inv_line_id[0], 0)]
        adv_amount = il_o.price_unit
        for line in so_o.order_line:            
            part_line = i_line.copy()
            line_amount = min(adv_amount,line.price_subtotal)
            part_line['price_unit'] = line_amount                        
            part_line['invoice_line_tax_id'] = [(6,0,[x.id for x in line.tax_id])]            
            new_data['invoice_line'].append((0,0,part_line))
            adv_amount -= line_amount
            if not adv_amount:
                break        
        inv_obj.write(cr, uid, [invoice_id], new_data, context=context)
        inv_obj.button_reset_taxes(cr, uid, [invoice_id], context)        
        return invoice_id

    