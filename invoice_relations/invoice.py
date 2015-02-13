# -*- coding: utf-8 -*-
##############################################################################
#
#     Author:  Tatár Attila <atta@nvm.ro>
#    Copyright (C) 2014-2015 Tatár Attila
#     
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
from openerp import models, fields, api

class account_invoice_relation(models.Model):
    
    _name = "account.invoice.relation"
    
    name = fields.Selection([('advance','Advance'),
                             ('adv_final','Final-Advance'),
                             ('storno','Storno'),
                             ('str_orig','Original-Storno')],
                            string='Name')
    source_inv_id = fields.Many2one('account.invoice',string='Source Invoice')
    derived_inv_id = fields.Many2one('account.invoice',string='Derived Invoice')
    derived_inv_date = fields.Date(related='derived_inv_id.date_invoice',string='Date')
    derived_inv_total = fields.Float(related='derived_inv_id.amount_total', 
                                     string='Invoice Amount')
        

class account_invoice(models.Model):
    
    _name = "account.invoice"
    _inherit = "account.invoice"
    
    @api.depends(        
    )
    def _linked_inv(self):
        for rec_o in self:
            link_ids = self.env['account.invoice.relation'].search(
                                             [('source_inv_id','=',rec_o.id)])
            rec_o.link_invoice_ids = link_ids 
        return

    link_invoice_ids = fields.Many2many('account.invoice.relation',
                                        compute=_linked_inv,                                          
                                        string='Result Invoices')