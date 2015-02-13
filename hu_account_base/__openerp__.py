# -*- encoding: utf-8 -*-
#"""
#    Odoo modul descriptor for hu_account_base module
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#    :Copyright: (c) 2014-2015 by Tatár Attila
#    :License: AGPLv3, see LICENSE.txt or http://www.gnu.org/licenses/agpl.html 
#    :Created on July 25, 2014
#    :@author: atta
#    :External dependency - 
#"""
{
    "name" : "Hungary - Accounting Base",
    "version" : "*0.1 for v8",
    "author" : "OODIN Consulting",
    "website": "",
    "category" : "Accounting",
    "sequence": 1,
    "depends" : [ 
                 'base_vat',
                 'base_iban', 
                 'l10n_hu',
                 'account_accountant',
                 'invoice_relations',
                 'sale' 
                 ],
    "description": """
Extending HU localization:
--------------------------

* Partner data:

 - HU tax number
 - Tax fullfillment date on invoices
    
* List of counties
                        
Accounting:
-----------

 - Storno accounting
 - Advance invoicing
 - Linked Invoices
 - Cash paid invoices - Rounding
* 
			

    """,    
    "data" : [
              'data/res.country.state.csv',
              'data/report_paperformat.xml',
              'data/product_data.xml',
              'res_partner_view.xml',
              'account_invoice_view.xml',
              'account_invoice_workflow.xml',
              'account_report.xml',
              'account_view.xml',
              'views/layouts.xml',
              'views/report_invoice.xml',              
              ],
    "test" : [],
    "demo" : [],
    "auto_install": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

