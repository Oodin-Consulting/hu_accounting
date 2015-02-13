# -*- encoding: utf-8 -*-
#
#    :Copyright: (c) 2014 by Tatár Attila
#    :License: AGPLv3, see LICENSE.txt or http://www.gnu.org/licenses/agpl.html 
#    :Created on July 25, 2014
#    :@author: atta
#
from openerp import models
from openerp.osv import fields
from openerp.tools.translate import _

class res_partner(models.Model):
    """ Extending partner object """
    
    _name = "res.partner"
    _inherit = "res.partner"
    
    
    _columns = {
        'vat': fields.char(u'Uniós adószám', help="Tax Identification Number."
                           " Check the box if this contact is subjected to taxes."
                           " Used by the some of the legal statements."),
        'hu_vat': fields.char('HU TIN',  help="Hungarian Tax Identification Number."),                
    }

    def _commercial_fields(self, cr, uid, context=None):        
        res = super(res_partner, self)._commercial_fields(cr, uid, 
                                                          context=context)
        return res + ['hu_vat']

class res_company_ro_invoicing(models.Model):
    
    _inherit = "res.company"
    
    _columns = {
                'invoicing_address':fields.boolean('Invoicing address', 
                        help='Show invoicing type contact address on invoice report')
    }