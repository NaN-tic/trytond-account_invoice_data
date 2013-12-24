#This file is part account_invoice_data module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.modules.account_invoice.invoice import _TYPE2JOURNAL

__all__ = ['Invoice', 'InvoiceLine']
__metaclass__ = PoolMeta

#_TYPE2JOURNAL = {
    #'out_invoice': 'revenue',
    #'in_invoice': 'expense',
    #'out_credit_note': 'revenue',
    #'in_credit_note': 'expense',
#}


class Invoice:
    __name__ = 'account.invoice'

    @classmethod
    def __setup__(cls):
        super(Invoice, cls).__setup__()
        cls._error_messages.update({
                'missing_payment_term': 'A payment term has not been defined.',
                'missing_account_receivable': 'Party "%s" (%s) must have a '
                    'receivable account.',
                'missing_account_payable': 'Party "%s" (%s) must have a '
                    'payable account.',
                })

    @classmethod
    def get_invoice_data(self, party, description=None,
            invoice_type='out_invoice'):
        '''
        Return invoice values from party
        :param party: the BrowseRecord of the party
        :return: a dict values
        '''
        pool = Pool()
        Journal = pool.get('account.journal')
        PaymentTerm = pool.get('account.invoice.payment_term')

        payment_terms = PaymentTerm.search([], limit=1)
        if not payment_terms:
            self.raise_user_error('missing_payment_term')
        payment_term, = payment_terms

        if invoice_type in ['out_invoice', 'out_credit_note']:
            if not party.account_receivable:
                self.raise_user_error('missing_account_receivable',
                    error_args=(party.name, party))
            account = party.account_receivable
            payment_term = party.customer_payment_term or payment_term
        else:
            if not party.account_payable:
                self.raise_user_error('missing_account_payable',
                    error_args=(party.name, party))
            account = party.account_payable
            payment_term = party.supplier_payment_term or payment_term

        journals = Journal.search([
                ('type', '=', _TYPE2JOURNAL.get(invoice_type, 'revenue')),
                ], limit=1)
        if journals:
            journal, = journals

        company = Transaction().context.get('company')
        company = Pool().get('company.company')(company)

        values = {'party': party}
        vals = Invoice(**values).on_change_party()

        vals['party'] = party
        vals['type'] = invoice_type
        vals['journal'] = journal
        vals['account'] = account

        if description:
            vals['description'] = description

        if not 'payment_term' in vals:
            vals['payment_term'] = payment_term

        if not 'company' in vals:
            vals['company'] = company

        if not 'currency' in vals:
            vals['currency'] = company.currency

        return vals


class InvoiceLine:
    __name__ = 'account.invoice.line'

    @classmethod
    def __setup__(cls):
        super(InvoiceLine, cls).__setup__()
        cls._error_messages.update({
                'missing_product_uom': 'Product Uom "%s" is not available.',
                })

    @classmethod
    def get_invoice_line_data(self, invoice, product, quantity, uom='u',
            note=None):
        '''
        Return invoice line values
        :param invoice: the BrowseRecord of the invoice
        :param product: the BrowseRecord of the product
        :param quantity: the float of the quantity
        :param uom: str of the unit of mesure
        :param note: the str of the note line
        :return: a dict values
        '''
        InvoiceLine = Pool().get('account.invoice.line')
        ProductUom = Pool().get('product.uom')

        invoice_type = invoice.type or 'out_invoice'
        # Test if a revenue or an expense account exists for the product
        if invoice_type in ['out_invoice', 'out_credit_note']:
            product.account_revenue_used
        else:
            product.account_expense_used

        uoms = ProductUom.search(['symbol', '=', uom], limit=1)
        if not uoms:
            self.raise_user_error('missing_product_uom', error_args=(uom))
        uom, = uoms

        line = InvoiceLine()
        line.unit = uom
        line.quantity = quantity
        line.product = product
        line.invoice = invoice
        line.description = None
        line.party = invoice.party
        values = line.on_change_product()
        res = {
            'invoice': invoice,
            'type': 'line',
            'quantity': quantity,
            'unit': uom,
            'product': product,
            'description': product.name,
            'party': invoice.party,
            'product_uom_category': product.category or None,
            'account': values.get('account'),
            'unit_price': values.get('unit_price'),
            'taxes': [('add', values.get('taxes'))],
            'note': note,
            'sequence': 1,
        }
        return res

    @classmethod
    def get_invoice_line_product(self, party, product, qty=1, desc=None,
            invoice_type='out_invoice'):
        '''
        Get Product values
        :param party: the BrowseRecord of the party
        :param product: the BrowseRecord of the product
        :param qty: Int quantity
        :param desc: Str line
        :param invoice_type: Str invoice type to create
        :return: a dict values
        '''
        pool = Pool()
        Invoice = pool.get('account.invoice')
        InvoiceLine = pool.get('account.invoice.line')
        Date = pool.get('ir.date')

        # Test if a revenue or an expense account exists for the product
        if invoice_type in ['out_invoice', 'out_credit_note']:
            product.account_revenue_used
        else:
            product.account_expense_used

        invoice = Invoice()
        invoice.party = party
        invoice.type = invoice_type
        invoice.currency = invoice.default_currency()
        invoice.currency_date = Date.today()

        line = InvoiceLine()
        line.quantity = qty
        line.invoice = invoice
        line.product = product
        line.description = desc or product.name
        line.party = party
        line.unit = product.default_uom
        values = line.on_change_product()

        vals = {
            'type': 'line',
            'quantity': qty,
            'unit': product.default_uom,
            'product': product,
            'description': desc or product.name,
            'party': party,
            'product_uom_category': product.category or None,
            'account': values.get('account'),
            'unit_price': values.get('unit_price'),
            'taxes': [('add', values.get('taxes'))],
            'sequence': 1,
            }
        return vals
