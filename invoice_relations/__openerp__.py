# -*- encoding: utf-8 -*-
#"""
#    Odoo modul descriptor for invoice_relations module
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#    :Copyright: (c) 2014-2015 by Tatár Attila
#    :License: AGPLv3, see LICENSE.txt or http://www.gnu.org/licenses/agpl.html 
#    :Created on december 10, 2014
#    :@author: atta
#    :External dependency - 
#"""
{
    "name" : "Linked Invoices",
    "version" : "*0.6 for v8",
    "author" : "Tatár Attila",
    "website": "",
    "category" : "Accounting & Finance",
    "depends" : [ 'account'                                                
                ],
    "description": """
Relations between several invoices: Storno, Advance, ... 
    """,    
    "data" : [
              'security/ir.model.access.csv',
              'invoice_view.xml',
              ],
    "test" : [],
    "demo" : [],
    "auto_install": False,
    "installable": True,    
    "application": False,    
    'images': [],
}


