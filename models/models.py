# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.addons.payment.models.payment_acquirer import ValidationError
from werkzeug import urls
from odoo.addons.cinetpay.controllers.controllers import Cinetpay
import logging


_logger = logging.getLogger(__name__)


class cinetpay(models.Model):
    _name = 'cinetpay.cinetpay'
    _description = 'cinetpay.cinetpay'
    _inherit = 'payment.acquirer'


    provider = fields.Selection(selection_add=[('cinetpay', 'Cinetpay'),
    ], ondelete={'cinetpay': 'set default'})
    apiKey = fields.Char(string='Merchant ApiKey',required_if_provider='cinetpay',groups='base.group_user')
    Site_Id = fields.Char(string='site_id',required_if_provider='cinetpay',groups='base.group_user')
    notify_url = fields.Char(string='notify_url',required_if_provider='cinetpay',groups='base.group_user')
    apiUrl = fields.Char(string='Endpoind',required_if_provider='cinetpay',groups='base.group_user')

    def cinetpay_form_generate_values(self,tx_values):
        self.ensure_one()
        base_url = self.get_base_url()

        cinetpay_tx_values = dict(tx_values)
        temp_cinetpay_tx_values = {
        'company' : self.company_id.name,
        'amount' : tx_values.get('amount'),
        'reference':tx_values.get('reference'),
        'currency': tx_values.get('currency') and tx_values.get('currency') or '',
        'currency_id': tx_values.get('currency') and tx_values.get('currency').id or '',
        'address_line1': tx_values['partner_address'],
        'address_city': tx_values['partner_city'],
        'address_country':tx_values['partner_country'].name or '',
        'email': tx_values['partner_email'],
        'address_zip': tx_values['partner_zip'],
        'name': tx_values['partner_name'],
        'customer_zip_code':tx_values.get('partner_zip'),
         'phone': tx_values['partner_phone'],
         'notify_url':urls.url_join(base_url,Cinetpay._notifyUrl),
         'return_url':urls.url_join(base_url,Cinetpay._returnUrl),
         "endpoint":self.apiUrl,
         
    }
        cinetpay_tx_values.update(temp_cinetpay_tx_values)
        return cinetpay_tx_values

    def _get_cinetpay_urls(self, environment):
        """ cinetpay URLS """
        return {
            'cinetpay_main_url': '/payment/cinetpay',
        }
    def cinetpay_get_form_action_url(self):
        environment = 'prod' if self.state == 'enabled' else 'test'
        return self._get_cardconnect_urls(environment)['cinetpay_main_url']


class TransactionCinetpay(models.Model):
    _inherit = 'payment.transaction'
    cct_txnid = fields.Char('Transaction ID')
    cct_txcurrency = fields.Char('Transaction Currency')

    def _cinetpay_form_get_tx_from_data(self, data):
        _logger.info("********************form data=%r", data)
        reference, amount, currency, acquirer_reference = data.get('reference'), 
        data.get('amount'), data.get( 'currency'), data.get('acquirer_reference')


        if not reference or not amount or not currency or not acquirer_reference:
            error_msg = 'Cinetpay: received data with missing reference (%s) or acquirer_reference (%s) or Amount (%s)' % ( reference, acquirer_reference, amount)
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        tx = self.search([('reference', '=', reference)])

        if not tx or len(tx) > 1:
            error_msg = _('received data for reference %s') % (pprint.pformat(reference))
            if not tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
                _logger.info(error_msg)
        return tx

        # def _cinetpay_form_get_invalid_parameters(self, data):
        # invalid_parameters = []
        # if float_compare(float(data.get('amount', '0.0')), self.amount, 2) != 0:
        #     invalid_parameters.append(('amount', data.get('amount'), '%.2f' % self.amount))
        # if data.get('currency') != self.currency_id.name:
        #     invalid_parameters.append(('currency', data.get('currency'), self.currency_id.name))
        # return invalid_parameters

        def _cinetpay_form_validate(self, data):
            status = data.get('status')
            res = {
            'acquirer_reference': data.get('acquirer_reference'),
            'state_message': data.get('tx_msg'),
            'cct_txcurrency': data.get('currency'),
            'date': fields.Datetime.now()
        }
            if status:
                logger.info('Validated Cinetpay payment for tx %s: set as done' % (self.reference))
                self._set_transaction_done()
                return self.write(res)

