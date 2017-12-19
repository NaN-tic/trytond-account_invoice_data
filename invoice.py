# This file is part account_invoice_data module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool, PoolMeta

__all__ = ['Invoice', 'InvoiceLine']


class Invoice:
    __metaclass__ = PoolMeta
    __name__ = 'account.invoice'

    @classmethod
    def get_invoice_data(cls, party, description=None,
            invoice_type='out_invoice'):
        '''
        Return invoice values from party
        :param party: the BrowseRecord of the party
        :return: an object
        '''
        pool = Pool()
        Invoice = pool.get('account.invoice')

        invoice = Invoice()
        invoice.type = invoice_type
        invoice.company = invoice.default_company()
        invoice.currency = invoice.default_currency()
        invoice.party = party
        invoice.on_change_type()
        invoice.on_change_party()

        if description:
            invoice.description = description
        return invoice


class InvoiceLine:
    __metaclass__ = PoolMeta
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

        line = InvoiceLine()
        line.invoice = invoice
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
        Date = pool.get('ir.date')

        invoice = Invoice()
        invoice.party = party
        invoice.invoice_date = None
        invoice.type = invoice_type
        invoice.currency = invoice.default_currency()
        invoice.currency_date = Date.today()

        line = InvoiceLine()
        line.quantity = qty
        line.invoice = invoice
        line.company = line.default_company()
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
