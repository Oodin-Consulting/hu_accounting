# -*- encoding: utf-8 -*-
#
#    :Copyright: (c) 2014 by Tatár Attila
#    :License: AGPLv3, see LICENSE.txt or http://www.gnu.org/licenses/agpl.html 
#    :Created on July 25, 2014
#    :@author: atta
#
from datetime import datetime
from openerp import models, api
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import  Warning

class account_invoice(models.Model):
    """ Extending invoice object """
    
    _name = "account.invoice"
    _inherit = "account.invoice"    
    
    _columns = {        
        'tax_fulfillment_date': fields.date(u'Teljesitési dátum', 
                                   readonly=True, states={'draft':[('readonly',False)]},
                                   select=True),    
        'adv_inv':fields.boolean('Előleg számla'),
        'original':fields.boolean('Számlakép másolat'),
    }
    def check_last_date_invoice(self, cr, uid, invoice_o, i_date):
        """ 
            Check max invoice date on valid invoices <= this invoice date
            return: False if this invoice date is ok, or
                    max date from valid invoices 
        """
        res = False
        comp = invoice_o.company_id.id
        if 'out' in invoice_o.type:
            i_type = ('out_invoice','out_refund')
        else:
            i_type = ('in_invoice','in_refund')
        qry = """ SELECT max(date_invoice) FROM account_invoice
                    WHERE company_id=%s AND
                          type in %s AND 
                          state in ('open','paid')
              """
        cr.execute(qry,(comp,i_type))
        m_date = cr.fetchone()
        if m_date:
            if m_date[0]<=i_date:
                return False
            else:
                return m_date[0]        
        return res
    
    def action_hu_verify(self, cr, uid, ids, context):
        """ Fill/check specific fields for Hungarian Accounting:
                     - invoice_date if not exist = today()
                     - check invoice_date if greater or equal like the last validated date
                     - tax_fulfillment_date if not exist = invoice_date
                     - check if difference between invoice_date and tax_filfillment_date is < 15 days                         
                     - force accounting period to tax_fulfillment_date                      
        """
        mod_data_obj = self.pool.get('ir.model.data')
        prod_obj = self.pool.get('product.product')
        inv_line_obj = self.pool.get('account.invoice.line')
        for inv_o in self.browse(cr, uid, ids, context=context):
            new_data = {}
            act_d = fields.date.context_today(self, cr, uid, context=context)
            if not inv_o.date_invoice:                
                new_data['date_invoice'] = act_d 
            # check if invoice date is valid
            chk_date = inv_o.date_invoice or act_d
            last_d = self.check_last_date_invoice(cr, uid, inv_o, chk_date)
            if last_d:
                raise Warning('The date of invoice is before the last date of'
                              ' the validated invoices (%s) !'% last_d)
            if not inv_o.tax_fulfillment_date:
                new_data['tax_fulfillment_date'] = inv_o.date_invoice or act_d
            # check the difference
#            inv_d = inv_o.date_invoice or new_data['date_invoice']
            ful_d = inv_o.tax_fulfillment_date or new_data['tax_fulfillment_date']
#            i_d = datetime.strptime(inv_d, "%Y-%m-%d")
#            f_d = datetime.strptime(ful_d, "%Y-%m-%d")
#            diff_d = abs((f_d - i_d).days)
            #!a
            # figyelmeztetes javascriptbol, folytatassal !!! ? ir_ui_view , render() function qweb template megadassal?
#            if diff_d > 15:
#                raise Warning('Difference between invoice date and fulfillment date can'
#                              ' be maximum 15 days')
            # force period to tax_fulfillment_date
            period = inv_o.period_id
            if not period:
                period_obj = self.pool.get('account.period')                
                period = period_obj.find(cr, uid, ful_d, context=context)[:1]
                if period:
                    new_data['period_id'] = period[0]  
            # if cash paid invoice add rounding line if necessary - only if is not a storno invoice
            res = mod_data_obj.get_object_reference(cr, uid, 
                                                            'hu_account_base',
                                                            'rounding_product')
            product_id = res and res[1] or False
            if product_id:
                # delete previous rounding line
                rounding_ids = [x.id for x in inv_o.invoice_line
                                 if x.product_id.id==product_id]  
                if rounding_ids:  
                    inv_line_obj.unlink(cr, uid, rounding_ids, context=context)            
                # recalculate the invoice
                self.button_reset_taxes(cr, uid, [inv_o.id], context=context)
            if inv_o.amount_total>0:
                to_round = inv_o.amount_total%5
                if inv_o.journal_id.cash_rounding and to_round:                
                    # add rounding line accordingly to total_amount
                    if to_round >= 0.01 and to_round <= 2.49:
                        line_amount = -to_round
                        f_property = 'property_account_expense'
                    else:
                        line_amount = 5.0 - to_round
                        f_property = 'property_account_income'                    
                    descr = ('lefele' if line_amount<0 else 'fölfele')+' kerekités'
                    pr_o = prod_obj.browse(cr, uid, product_id, context)
                    account_id = getattr(pr_o,f_property).id
                    inv_line_values = {
                        'name': descr,                    
                        'account_id': account_id,
                        'price_unit': line_amount,
                        'quantity': 1.0,
                        'discount': False,
                        'uos_id': 1,
                        'product_id': product_id,      
                    }
                    new_data['invoice_line'] = [(0, 0, inv_line_values)]                
            if new_data:                
                self.write(cr, uid, [inv_o.id], new_data)
        return True
    
    @api.model
    def line_get_convert(self, line, part, date):
        """
           Storno
        """
        res = super(account_invoice, self).line_get_convert(line, part, date)
        #ctx = dict(self._context)
        if self.journal_id.posting_policy == 'storno':
            credit = debit = 0.0
            if self.type in ('out_invoice', 'out_refund'):
                if line.get('type', 'src') in ('dest'):
                    debit = line['price']  
                else:  # 'src','tax'
                    credit = line['price'] * (-1)                    
            else:  # 'in_invoice', 'in_refund'
                if line.get('type', 'src') in ('dest'):
                    credit = line['price'] * (-1)
                else:
                    debit = line['price']
                    print line
                    if (line['type']=='tax') and self.type=='in_invoice' and line['price']<0.00:
                        credit = line['price'] * (-1)
                        debit = 0.00
                 
            res['debit'] = debit
            res['credit'] = credit
            if self and self.currency_id.id != self.company_id.currency_id.id:
                if abs(res['tax_amount']) > 0.00:  
                    res['tax_amount'] = res['debit'] + res['credit']
        return res

    def group_lines(self, iml, line):
        """
           Storno
           Merge account move lines (and hence analytic lines)
            if invoice line hashcodes are equals
        """
        if self.journal_id.group_invoice_lines:
            if self.journal_id.posting_policy == 'contra':
                return super(account_invoice, self).group_lines(iml, line)
            if self.journal_id.posting_policy == 'storno':
                line2 = {}
                for x, y, l in line:                    
                    hash_x = self.inv_line_characteristic_hashcode(l)
                    side = abs(l['credit']) > 0.0 and 'credit' or 'debit'
                    if l['credit'] == 0.00 and l['debit'] == 0:
                        tmp_c = '-'.join((hash_x, 'credit'))
                        side = (tmp_c in line2) and 'credit' or side
                    tmp = '-'.join((hash_x, side))
                    if tmp in line2:
                        line2[tmp]['debit'] += l['debit'] or 0.0
                        line2[tmp]['credit'] += l['credit'] or 0.00
                        line2[tmp]['tax_amount'] += l['tax_amount']
                        line2[tmp]['analytic_lines'] += l['analytic_lines']
                        line2[tmp]['amount_currency'] += l['amount_currency']
                        line2[tmp]['quantity'] += l['quantity']
                    else:
                        line2[tmp] = l
                line = []
                for key, val in line2.items():
                    line.append((0, 0, val))
        return line
    
    def get_inv_addr(self, p_o):
        """ Invoice template used function
            Return: invoice type contact browse record of the p_o 
        """                
        if p_o.parent_id:
            # if p_o is a contact of type 'invoice' return it
            if p_o.type=='invoice':
                return p_o
            # else return the company's first 'invoice' type contact
            partn = p_o.parent_id                     
        else:
            partn = p_o
        inv_type_contacts = [x for x in partn.child_ids if x.type=='invoice']
        if inv_type_contacts:
            return inv_type_contacts[0]
        else:
            return False
        
    def first_print(self, cr, uid, ids, inv):
        # get setting from configuration
        hu_inv_track_copies = False
        if hu_inv_track_copies:
            if inv.state in ('open','paid'):        
                if inv.original:
                    return False
                else:
                    self.write(cr, uid, [inv.id],{'original':True})
                    return True
        return None
        
        

#    def invoice_final(self, cr, uid, ids, context=None):
#        """
#            Button called function - creates final invoice where exists advance invoice,
#            and set the relation between these invoices.
#        """
#        return True

class sale_order(models.Model):
    
    _name = "sale.order"
    _inherit = "sale.order"
    
    def _make_invoice(self, cr, uid, order, lines, context=None):
        """
        """
        invoice_id = super(sale_order,self)._make_invoice( cr, uid, order, lines, context=context)                
        adv_inv_ids = [ x.id for x in order.invoice_ids if x.adv_inv]        
        inv_rel_obj = self.pool.get('account.invoice.relation')
        for adv_id in adv_inv_ids:
            inv_rel_obj.create(cr, uid, 
                               {'name':'advance',
                                'source_inv_id':invoice_id,
                                'derived_inv_id':adv_id,
                               }, context=context)
            inv_rel_obj.create(cr, uid, 
                               {'name':'adv_final',
                                'source_inv_id':adv_id,
                                'derived_inv_id': invoice_id,
                               }, context=context)     
        return invoice_id