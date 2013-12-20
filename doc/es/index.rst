============================================
Obtener valores para generar nuevas facturas
============================================

El módulo account_invoice_data permite obtener datos de factura a partir de un
tercero y datos de línea de factura a partir de un producto para simplificar la
creación de una nueva factura.

Se ha diseñado para ofrecer estos dos métodos para ser usados por otros módulos:

Factura
=======

    vals = Invoice.get_invoice_data(party, description=None, invoice_type='out_invoice')

Línea de factura
================

    line_vals = InvoiceLine.get_invoice_line_data(invoice, product, quantity, uom='u', note=None)

Además, si la factura todavía no está creada, este método permite calcular los
datos de línea de factura a partir de un tercero y un producto:

    line_vals = InvoiceLine.get_invoice_line_product(party, product, qty=1, desc=None, invoice_type='out_invoice')
