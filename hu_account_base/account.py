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

class account_account(models.Model):
    
    _name = 'account.account'
    _inherit = 'account.account'
    
    _columns = {
        'check_side': fields.selection(
                        [('credit', 'Credit'),
                         ('debit', 'Debit'),
                         # TODO ('force_credit', 'Auto credit'),
                         # TODO ('force_debit', 'Auto debit'),
                        ],
                        'Check/force side', size=16, required=False,
                        help="Check that all postings on this account are done"
                             " on credit or debit side only.\n"
                             "This rule is not applied on year closing/opening periods.\n"
                        # TODO "Auto will change side automatically.\n"
                                        ),
    }


class account_journal(models.Model):
    
    _name = "account.journal"
    _inherit = "account.journal"
    
    _columns = {
        'posting_policy': fields.selection(
                            [('contra', 'Contra (debit<->credit)'),
                             ('storno', 'Storno (-)'),
                            ],
                            'Storno or Contra', size=16, required=True,
                            help="Storno allows minus postings, Refunds are"
                                 " posted on the same joural/account * (-1).\n"
                                 "Contra doesn't allow negative posting."
                                 " Refunds are posted by swaping credit and debit side."
        ),
        'refund_journal_id': fields.many2one('account.journal', 'Refund journal',
                               help="Journal for refunds/returns from this journal."
                                    " Leave empty to use same journal for normal and"
                                    " refund/return postings.",
        ),
        'cash_rounding': fields.boolean('Rounding to 5 HUF'),        
    }
    
    _defaults = {
        'posting_policy': 'storno',
    }


class account_move_line(models.Model):
    
    _name = "account.move.line"
    _inherit = "account.move.line"
    
    #Original constraints
    #_sql_constraints = [
    #('credit_debit1', 'CHECK (credit*debit=0)',  'Wrong credit or debit value in accounting entry !'),
    #('credit_debit2', 'CHECK (credit+debit>=0)', 'Wrong credit or debit value in accounting entry !'),
    #]
    # credit_debit1 is valid constraint. Make message more explicit
    #    # credit_debit2 is replaced with dummy constraint that is always true.

    def _auto_init(self, cr, context=None):
        result = super(account_move_line, self)._auto_init(cr, context=context)
        # Remove constrains for credit_debit1, credit_debit2        
        cr.execute(
            """
            ALTER TABLE account_move_line DROP CONSTRAINT IF EXISTS account_move_line_credit_debit1;
            ALTER TABLE account_move_line DROP CONSTRAINT IF EXISTS account_move_line_credit_debit2;
            """
        )
        return result
        
    _sql_constraints = [
        ('credit_debit3', 'CHECK (credit*debit=0)', 'Wrong credit or debit value in accounting entry! Either credit or debit must be 0.00.'),
        #!a
        #('credit_debit4', 'CHECK (abs(credit+debit)>=0)', 'Wrong credit or debit value in accounting entry !'),  # Does nothing, maybe one day (abs(credit+debit)>0.0)
    ]

    def _check_contra_minus(self, cr, uid, ids, context=None):
        """ 
           This is to restore credit_debit2 check functionality, for contra journals 
        """
        for l in self.browse(cr, uid, ids, context=context):
            if l.journal_id.posting_policy == 'contra':
                if l.debit + l.credit < 0.0:
                    return False
        return True

    def _check_storno_tax(self, cr, uid, ids, context=None):
        """For Storno accounting Tax/Base amount is always == (debit + credit)
           Still trying to find the case where it is not.
           Maybe for contra check is abs(tax_amount) = abs(debit + credit) ???
        """
        #!a - to delete all the function?
        #for l in self.browse(cr, uid, ids, context=context):
        #    if l.journal_id.posting_policy == 'storno' and l.tax_code_id:
        #        if float_compare((l.debit + l.credit), l.tax_amount, precision_digits=2) != 0:  # precision_digits=dp.get_precision('Account')[1])
        #            return False
        return True

    def _check_side(self, cr, uid, ids, context=None):
        """For Storno accounting some account are using only one side during FY
        """
        for l in self.browse(cr, uid, ids, context=context):
            check_side = l.account_id.check_side
            if (check_side and
                check_side == 'debit' and abs(l.credit) > 0.0 or
                check_side == 'credit' and abs(l.debit) > 0.0):
                    return False
        return True

    _constraints = [
        (_check_contra_minus, _('Negative credit or debit amount is not allowed for "contra" journal policy.'), ['journal_id']),
        (_check_storno_tax, _('Invalid tax amount. Tax amount can be 0.00 or equal to (Credit + Debit).'), ['tax_amount']),
        (_check_side, _('Invalid side for account.'), ['account_id']),
    ]
    
    # Rewrite residual function to allow amount residual according to storno journals.
    def _amount_residual(self, cr, uid, ids, field_names, args, context=None):        
        if context is None:
            context = {}
        res = {}
        if context is None:
            context = {}
        cur_obj = self.pool.get('res.currency')
        for move_line in self.browse(cr, uid, ids, context=context):
            res[move_line.id] = {
                'amount_residual': 0.0,
                'amount_residual_currency': 0.0,
            }

            if move_line.reconcile_id:
                continue
            if not move_line.account_id.reconcile:
                #this function does not suport to be used on move lines not related to a reconcilable account
                continue

            if move_line.currency_id:
                move_line_total = move_line.amount_currency
                sign = move_line.amount_currency < 0 and -1 or 1
            else:
                move_line_total = move_line.debit - move_line.credit
                sign = (move_line.debit - move_line.credit) < 0 and -1 or 1
            line_total_in_company_currency =  move_line.debit - move_line.credit
            context_unreconciled = context.copy()
            if move_line.reconcile_partial_id:
                for payment_line in move_line.reconcile_partial_id.line_partial_ids:
                    if payment_line.id == move_line.id:
                        continue
                    if payment_line.currency_id and move_line.currency_id and payment_line.currency_id.id == move_line.currency_id.id:
                            move_line_total += payment_line.amount_currency
                    else:
                        if move_line.currency_id:
                            context_unreconciled.update({'date': payment_line.date})
                            amount_in_foreign_currency = cur_obj.compute(cr, uid, move_line.company_id.currency_id.id, move_line.currency_id.id, (payment_line.debit - payment_line.credit), round=False, context=context_unreconciled)
                            move_line_total += amount_in_foreign_currency
                        else:
                            move_line_total += (payment_line.debit - payment_line.credit)
                    line_total_in_company_currency += (payment_line.debit - payment_line.credit)

            result = move_line_total
            res[move_line.id]['amount_residual_currency'] =  sign * (move_line.currency_id and self.pool.get('res.currency').round(cr, uid, move_line.currency_id, result) or result)
            res[move_line.id]['amount_residual'] = sign * line_total_in_company_currency
            if move_line.journal_id.posting_policy == 'storno':
                if move_line.debit<0 or move_line.credit<0:
                    res[move_line.id]['amount_residual_currency'] =  res[move_line.id]['amount_residual_currency'] * (-1)
                    res[move_line.id]['amount_residual'] = res[move_line.id]['amount_residual'] * (-1)
        return res
        
    _columns = {
        'amount_residual_currency': fields.function(_amount_residual, string='Residual Amount in Currency', multi="residual", help="The residual amount on a receivable or payable of a journal entry expressed in its currency (maybe different of the company currency)."),
        'amount_residual': fields.function(_amount_residual, string='Residual Amount', multi="residual", help="The residual amount on a receivable or payable of a journal entry expressed in the company currency."),
    }    

class account_model_line(models.Model):
    
    _name = "account.model.line"
    _inherit = "account.model.line"
    
    def _auto_init(self, cr, context=None):
        # Remove constrains for credit_debit1, credit_debit2
        
        cr.execute("""
            ALTER TABLE account_model_line DROP CONSTRAINT IF EXISTS account_model_line_credit_debit1;
            ALTER TABLE account_model_line DROP CONSTRAINT IF EXISTS account_model_line_credit_debit2;
        """)
        result = super(account_model_line, self)._auto_init(cr, context=context)
        return result
        
    _sql_constraints = [
        ('credit_debit3', 'CHECK (credit*debit=0)', 'Wrong credit or debit value in model! Either credit or debit must be 0.00.'),
        ('credit_debit4', 'CHECK (abs(credit+debit)>=0)', 'Wrong credit or debit value in accounting entry !'),
    ]
