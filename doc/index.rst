Account Invoice Data Module
###########################

The account_invoice_data module gets account.invoice data from a party and
account.invoice.line data from a product to simplify the creation of a new
invoice.

It's designed to offer these two methods to be used from others modules:

Account Invoice
===============

    invoice = Invoice.get_invoice_data(party, description=None, invoice_type='out_invoice')
    invoice.save()

Account Invoice Line
====================

    invoice_lines = InvoiceLine.get_invoice_line_data(invoice, product, quantity, uom='u', note=None)
    invoice_lines.save()

Also, if the invoice is not created yet, this method allows to compute of
account.invoice.line data from a party and a product:

    invoice_lines = InvoiceLine.get_invoice_line_product(party, product, qty=1, desc=None, invoice_type='out_invoice')
    invoice_lines.save()
