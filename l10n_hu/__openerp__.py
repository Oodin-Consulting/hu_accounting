# -*- encoding: utf-8 -*-
#"""
#    Odoo modul descriptor for l10n_hu module
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    :Copyright: (c) 2014-2015 by Tatár Attila
#    :License: AGPLv3, see LICENSE.txt or http://www.gnu.org/licenses/agpl.html 
#    :Created on December 15, 2014
#    :@author: atta
#    :External dependency - 
#"""
{
    "name" : "Hungary - Localization-Accounting",
    "version" : "*1.0 for v8",
    "author" : "OODIN Consulting",
    "website": "",
    "category" : "Localization/Account Charts",
    "sequence": 16,
    "depends" : [ 'base_vat', 'base_iban', 'account', ],
    "description": """
HU Localization and Accounting
------------------------------

* Chart of accounts for Hungary
* Taxes, Tax-Codes, Fiscal Positions, Journals
* List of Countys 
* Bank list from Hungarian National Bank 
* Several settings: currency, rounding  
			
    """,    
    "data" : [
              'data/res.country.state.csv',
              'data/partners.xml',
              'data/banks.xml',
              'data/account_account_type.xml',
              'data/account_account_template.xml',                           
              'data/account.tax.code.template.csv',
              'data/account_chart_template.xml',              
              'data/account.tax.template.csv',               
              'data/account.fiscal.position.template.csv',
              'data/account.fiscal.position.tax.template.csv',
              'data/journals.xml',
              'data/data.xml',
              'l10n_hu_wizard.xml',
              ],
    "test" : [],
    "demo" : [],
    "auto_install": False,
    "installable": True,
}


