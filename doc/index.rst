Account Invoice Data Module
###########################

The account_invoice_data module gets account.invoice data from a party and
account.invoice.line data from a product to simplify the creation of a new
invoice.

It's designed to offer these two methods to be used from others modules:

Account Invoice
===============

    vals = Invoice.get_invoice_data(party, description=None, invoice_type='out_invoice')

Account Invoice Line
====================

    line_vals = InvoiceLine.get_invoice_line_data(invoice, product, quantity, uom='u', note=None)

Also, if the invoice is not created yet, this method allows to compute of
account.invoice.line data from a party and a product:

    line_vals = InvoiceLine.get_invoice_line_product(party, product, qty=1, desc=None, invoice_type='out_invoice')
