#This file is part account_invoice_data module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

__all__ = ['Invoice', 'InvoiceLine']
__metaclass__ = PoolMeta


class Invoice:
    'Invoice'
    __name__ = 'account.invoice'

    @classmethod
    def __setup__(cls):
        super(Invoice, cls).__setup__()
        cls._error_messages.update({
            'missing_payment_term': 'Party "%s" (%s) must be a Payment term!',
            'missing_account_receivable': 'Party "%s" (%s) must be a '
                'Account Receivable!',
            })

    @classmethod
    def get_invoice_data(self, party, description=None):
        '''
        Return invoice values from party
        :param party: the BrowseRecord of the party
        :return: a dict values
        '''
        Journal = Pool().get('account.journal')
        PaymentTerm = Pool().get('account.invoice.payment_term')

        journal_id = Journal.search([
            ('type', '=', 'expense'),
            ], limit=1)
        if journal_id:
            journal_id = journal_id[0]

        payment_term_ids = PaymentTerm.search([('active', '=', True)])
        if not len(payment_term_ids) > 0:
            self.raise_user_error('missing_payment_term',
                error_args=(party.name, party))

        if not party.account_receivable:
            self.raise_user_error('missing_account_receivable',
                error_args=(party.name, party))

        invoice_address = party.address_get(type='invoice')
        company = Transaction().context.get('company')
        company = Pool().get('company.company')(company)

        res = {
            'company': company.id,
            'type': 'out_invoice',
            'journal': journal_id,
            'party': party.id,
            'invoice_address': invoice_address and invoice_address or None,
            'currency': company.currency.id,
            'account': party.account_receivable.id,
            'payment_term': party.customer_payment_term and
                party.customer_payment_term.id or
                payment_term_ids[0],
            'description': description,
        }
        return res


class InvoiceLine:
    'Invoice Line'
    __name__ = 'account.invoice.line'

    @classmethod
    def __setup__(cls):
        super(InvoiceLine, cls).__setup__()
        cls._error_messages.update({
            'missing_account_revenue': 'Product "%s" (%s) must be a '
                'Account Revenue!',
            'missing_product_uom': 'Not available Product Uom "%s"',
            })

    @classmethod
    def get_invoice_line_data(self, invoice, product, quantity, uom='u', note=None):
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

        if not product.account_revenue and not (product.category and
            product.category.account_revenue):
            self.raise_user_error('missing_account_revenue',
                error_args=(product.name, product))

        uoms = ProductUom.search(['symbol', '=', uom])
        if not len(uoms) > 0:
            self.raise_user_error('missing_product_uom', error_args=(uom))
        uom = uoms[0]

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
            'product': product.id,
            'description': product.name,
            'party': invoice.party,
            'product_uom_category': product.category and
                product.category.id or None,
            'account': values.get('account'),
            'unit_price': values.get('unit_price'),
            'taxes': [('add', product.customer_taxes)],
            'note': note,
            'sequence': 1,
        }
        return res

    @classmethod
    def get_invoice_line_product(self, party, product, qty=1, desc=None):
        """
        Get Account Invoice Lines values
        :param contract: the BrowseRecord of the contract
        :param product: the BrowseRecord of the product
        :param qty: Int quantity
        :param desc: Str line
        :return: dict account invoice values
        """
        if not product.account_revenue and not (product.category and
            product.category.account_revenue):
            self.raise_user_error('missing_account_revenue',
                error_args=(product.name, product))

        vals = {
            'type': 'line',
            'quantity': qty,
            'unit': product.default_uom,
            'product': product,
            'description': desc or product.name,
            'party': party,
            'product_uom_category': product.category and
                product.category.id or None,
            'account': product.account_revenue or
                product.category.account_revenue,
            'unit_price': product.list_price,
            'taxes': [('add', product.customer_taxes)],
            'sequence': 1,
         }
        return vals
