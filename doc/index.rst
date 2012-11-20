Account Invoice Data Module
###########################

The account_invoice_data module get account.invoice data from a party 
and account.invoice.line data from a product to create a new invoice. 
It's design to use two methods from others modules.

Account Invoice
===============

    vals = Invoice.get_invoice_data(party, description)

Account Invoice Line

    line_vals = InvoiceLine.get_invoice_line_data(invoice, product, quantity, uom='h', note)
