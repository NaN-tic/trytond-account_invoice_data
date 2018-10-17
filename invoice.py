# This file is part account_invoice_data module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.modules.account_invoice.invoice import _TYPE2JOURNAL

__all__ = ['Invoice', 'InvoiceLine']

# _TYPE2JOURNAL = {
#     'out': 'revenue',
#     'in': 'expense',
# }


class Invoice(metaclass=PoolMeta):
    __name__ = 'account.invoice'

    @classmethod
    def __setup__(cls):
        super(Invoice, cls).__setup__()
        cls._error_messages.update({
                'missing_payment_term': 'A payment term has not been defined.',
                'missing_account_receivable': ('Party "%s" (%s) must have a '
                    'receivable account.'),
                'missing_account_payable': ('Party "%s" (%s) must have a '
                    'payable account.'),
                'missing_journal': 'A journal has not been defined for "%s".',
                })

    @classmethod
    def get_invoice_data(cls, party, description=None, invoice_type='out'):
        '''
        Return invoice values from party
        :param party: the BrowseRecord of the party
        :return: an object
        '''
        pool = Pool()
        Date = pool.get('ir.date')
        Journal = pool.get('account.journal')
        PaymentTerm = pool.get('account.invoice.payment_term')
        Invoice = pool.get('account.invoice')

        payment_terms = PaymentTerm.search([], limit=1)
        if not payment_terms:
            cls.raise_user_error('missing_payment_term')
        payment_term, = payment_terms

        if invoice_type == 'out':
            if not party.account_receivable:
                cls.raise_user_error('missing_account_receivable',
                    error_args=(party.name, party))
            account = party.account_receivable
            payment_term = party.customer_payment_term or payment_term
        else:
            if not party.account_payable:
                cls.raise_user_error('missing_account_payable',
                    error_args=(party.name, party))
            account = party.account_payable
            payment_term = party.supplier_payment_term or payment_term

        journals = Journal.search([
                ('type', '=', _TYPE2JOURNAL.get(invoice_type, 'revenue')),
                ], limit=1)
        if not journals:
            cls.raise_user_error('missing_journal',
                error_args=(invoice_type))
        journal, = journals

        invoice_address = party.address_get(type='invoice')

        invoice = Invoice()
        invoice.type = invoice_type
        invoice.company = invoice.default_company()
        invoice.journal = journal
        invoice.account = account
        invoice.currency = invoice.default_currency()
        invoice.currency_date = Date.today()
        invoice.party = party
        invoice.invoice_address = invoice_address and invoice_address or None
        invoice.on_change_party()

        if not invoice.payment_term:
            invoice.payment_term = payment_term
        if description:
            invoice.description = description
        return invoice


class InvoiceLine(metaclass=PoolMeta):
    __name__ = 'account.invoice.line'

    @classmethod
    def get_invoice_line_data(cls, invoice, product, quantity, note=None):
        '''
        Return invoice line values
        :param invoice: the BrowseRecord of the invoice
        :param product: the BrowseRecord of the product
        :param quantity: the float of the quantity
        :param uom: str of the unit of mesure
        :param note: the str of the note line
        :return: an object
        '''
        InvoiceLine = Pool().get('account.invoice.line')

        invoice_type = invoice.type or 'out'
        # Test if a revenue or an expense account exists for the product
        if invoice_type == 'out':
            product.account_revenue_used
        else:
            product.account_expense_used

        line = InvoiceLine()
        line.invoice = invoice
        line.company = line.default_company()
        line.currency = invoice.default_currency()
        line.party = invoice.party
        line.quantity = quantity
        line.product = product
        line.type = 'line'
        line.sequence = 1
        line.on_change_product()
        if not hasattr(line, 'unit_price'):
            line.unit_price = product.list_price
        if note:
            line.note = note
        return line

    @classmethod
    def get_invoice_line_product(cls, party, product, qty=1, desc=None,
            invoice_type='out'):
        '''
        Get Product values
        :param party: the BrowseRecord of the party
        :param product: the BrowseRecord of the product
        :param qty: Int quantity
        :param desc: Str line
        :param invoice_type: Str invoice type to create
        :return: an object
        '''
        pool = Pool()
        Invoice = pool.get('account.invoice')
        InvoiceLine = pool.get('account.invoice.line')
        Product = pool.get('product.product')
        Date = pool.get('ir.date')

        if not desc:
            lang = party.lang and party.lang.code or Transaction().language
            with Transaction().set_context(language=lang):
                product = Product(product.id)

        # Test if a revenue or an expense account exists for the product
        if invoice_type == 'out':
            product.account_revenue_used
        else:
            product.account_expense_used

        invoice = Invoice()
        invoice.party = party
        invoice.invoice_date = None
        invoice.type = invoice_type
        invoice.currency = invoice.default_currency()
        invoice.currency_date = Date.today()

        line = InvoiceLine()
        line.quantity = qty
        line.invoice = invoice
        line.currency = invoice.default_currency()
        line.product = product
        line.party = party
        line.type = 'line'
        line.sequence = 1
        line.unit_price = product.list_price
        line.on_change_product()
        if desc:
            line.description = desc
        line.invoice = None
        return line
