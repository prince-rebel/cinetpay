# -*- coding: utf-8 -*-
import base64
import json
import logging
import requests
import  uuid

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)



class Cinetpay(http.Controller):
    _notifyUrl='/payment/cinetpay/success'
    _returnUrl='/payment/cinetpay/validate'
    _cancel_url = '/payment/cinetpay/cancel'

    @http.route(_notifyUrl, auth='public', methods=['GET', 'POST'],csrf=False)
    def getPaymentLinkFromCinetapy(self, **kw):
        reference =kw['reference']
        try:
            if reference :
                tx =request.env['payment.transaction'].sudo().search([('reference', '=', reference)])
                payment_url =tx.endpoint
                Headers ={
                    'Content-Type':'application/json'
                }
                payload=json.dumps({
                    "apikey":tx.acquirer_id.apiKey,
                    "site_id":tx.acquirer_id.Site_Id,
                    "transaction_id":str(uuid.uuid4()),
                    "amount":int(tx.amount),
                    "currency":tx.currency,
                    "description":"Regler votre devis ",
                    "notify_url":tx.notify_url,
                    "channels":"CREDIT_CARD",
                    "metadata":tx.reference,
                    "customer_name":tx.name,
                    "customer_surname":tx.name,
                    "customer_phone_number": tx.phone,
                    "customer_email":tx.email,
                    "customer_address":tx.address_line1,
                    "customer_city":tx.address_city,
                    "customer_country":tx.address_country,
                    "customer_state":tx.address_city,
                    "customer_zip_code":str(tx.customer_zip_code),
                })
                
                r=requests.post(payment_url,headers=Headers,data =payload)
                print('le resultat de la requete est :&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&',r.json())

        except :
            print("ERROR reference")
            
        

        return "Hello, world"

