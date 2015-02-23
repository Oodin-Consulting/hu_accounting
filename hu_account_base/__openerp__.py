# -*- encoding: utf-8 -*-
#"""
#    Odoo modul descriptor for hu_account_base module
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#    :Copyright: (c) 2014-2015 by Tatár Attila
#    :License: AGPLv3, see LICENSE.txt or http://www.gnu.org/licenses/agpl.html
#    :Created on July 25, 2014
#    :@author: atta
#    :External dependency - 
#"""
{
    "name" : "Hungary - Accounting Base",
    "version" : "*1.0 for v8",
    "author" : "OODIN Consulting",
    "website": "",
    "category" : "Accounting",
    "sequence": 17,
    "depends" : [ 
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
                        
Accounting:
-----------

 - Storno accounting
 - Advance invoicing
 - Linked Invoices
 - Cash paid invoices - Rounding

*** A számlázómodul használatához a jogszabályoknak megfelelően, igazolni kel az adóalanyiságot az adószám megadásával a regisztrációs felületünkön ( a regisztrációhóz kattintson ide ) , valamit be kell jelenteni a NAV felé a számlázómodul használatának megkezdését a SZAMLAZO nyomtatvány SZÁMLÁZÓ PROGRAM fejezetének kitöltésével. 
Köszönettel: Oodin Consulting

 To use our hungarian invoicing module according to hungarian law, you have to verify your hungarian tax number on our regisration form (click here). You also have to register the usage of our accounting modulethis module to NAV, by filling the SZAMLAZO at the SZÁMLÁZÓ PROGRAM chapter.
Thank you: Oodin Consulting ***

    """,    
    "data" : [              
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
