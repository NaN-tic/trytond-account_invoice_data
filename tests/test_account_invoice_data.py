#!/usr/bin/env python
# This file is part account_invoice_data module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_depends


class AccountInvoiceDataTestCase(unittest.TestCase):
    'Test Account Invoice Data module'

    def setUp(self):
        trytond.tests.test_tryton.install_module('account_invoice_data')

    def test0006depends(self):
        'Test depends'
        test_depends()


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountInvoiceDataTestCase))
    return suite
