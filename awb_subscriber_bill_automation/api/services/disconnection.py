from odoo import http
from odoo.http import request
from .authentication import OdooAPI

import importlib
import json
import logging

_logger = logging.getLogger(__name__)

Serializer = importlib.import_module(
    "odoo.addons.odoo-rest-api"
).controllers.serializers.Serializer

SUBSCRIPTION = "sale.subscription"


class OdooAPI(OdooAPI):
    @http.route(
        '/api/subscription/disconnection/',
        type='json',
        auth='public',
        methods=["PATCH"],
        csrf=False
    )
    def _disconnect_subs(
        self, channel, discon_type, subscriptions
    ):
        no_permission = self._no_permission()
        if no_permission:
            return no_permission

        invalid_params = self._check_params(
            channel, discon_type, subscriptions
        )
        if invalid_params:
            return invalid_params

        source = request.env[SUBSCRIPTION]._get_discon_type(
            discon_type=discon_type.lower(), channel=channel
        )

        if not source:
            http.Response.status = "400"
            res = {
                "errors": {
                    "status": 400,
                    "code": 4002,
                    "message": "400 Bad Request",
                    "description": "Incorrect Values",
                    "links": {
                        "about": ""
                    },
                }
            }

            _logger.info(f"----- Disconnection: <Response [{http.Response.status}]> -----")
            return json.dumps(res)
        _logger.info(f"----- Disconnection from {source.get('name')} -----")

        # Get the discon type on Odoo
        discon_status = request.env[SUBSCRIPTION]._get_discon_type(
            discon_type=discon_type.lower(), channel="od"
        )

        sms_ids = []
        subscription_codes = []
        for sub in subscriptions:
            code = sub.get("code")
            sms_id = sub.get("smsid")
            if code:
                subscription_codes.append(code)
            elif sms_id:
                sms_ids.append(sms_id)

        subscription_records = request.env[SUBSCRIPTION].search([
            "|",
            ("code", "in", subscription_codes),
            ("opportunity_id.jo_sms_id_username", "in", sms_ids)
        ])

        if subscription_records.exists() and discon_status:
            executed = False
            function = discon_status.get("executable")
            if function:
                # Call function
                executable = eval(
                    "request.env[SUBSCRIPTION].%s"
                    % function
                )
                executed = executable(subscription_records, discon_status.get("status"), discon_status.get("subs_closed"))

            if executed:
                http.Response.status = "200"
                status = 200
                message = "200 OK"
                code = 200
            else:
                http.Response.status = "201"
                status = 201
                message = "201 OK"
                code = 201

            serializer = Serializer(
                subscription_records,
                "{id, code, display_name, partner_id, subscription_status_subtype}",
                many=True
            )
            data = serializer.data
            res = {
                "success": {
                    "status": status,
                    "message": message,
                    "code": code,
                    "description": "",
                    "links": {
                        "about": "",
                    },
                },
                "data": data,
            }

            _logger.info(f"----- Disconnection: <Response [{http.Response.status}]> -----")
            return res

        http.Response.status = "400"
        res = {
            "errors": {
                "status": 400,
                "code": 4002,
                "message": "400 Bad Request",
                "description": "Incorrect Values",
                "links": {
                    "about": ""
                },
            }
        }

        _logger.info(f"----- Disconnection: <Response [{http.Response.status}]> -----")
        return json.dumps(res)

    def _check_params(self, channel, discon_type, subscriptions):
        missing_params = ""
        if not channel:
            missing_params += '<channel: AR/ SF/ OD>'
        if not discon_type:
            missing_params += '<discon_type: SYSV/ SYSI_EXPIRY/ SYSI_BANDWIDTH/ SYSI_NONPAYMENT/ PHYI_NONPAYMENT/ PHYV>'
        if not subscriptions:
            missing_params += '<subscriptions: dictionary e.g. {code: SUB001, smsid: username}>'

        if missing_params:
            http.Response.status = "400"
            res = {
                "errors": {
                    "status": 400,
                    "code": 4001,
                    "message": "400 Bad Request",
                    "description": "Missing Required Fields: %s" % missing_params,
                    "links": {
                        "about": ""
                    },
                }
            }

            _logger.info(f"----- Disconnection: <Response [{http.Response.status}]> -----")
            return json.dumps(res)
