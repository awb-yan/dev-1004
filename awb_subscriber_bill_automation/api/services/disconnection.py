from odoo import http
from odoo.http import request
from .authentication import OdooAPI

import importlib
import json

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

        # Get the discon type
        discon_status = request.env[SUBSCRIPTION]._get_discon_type(
            discon_type=discon_type.lower(), channel=channel.lower()
        )

        if not discon_status:
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

            return json.dumps(res)

        # Extracting code in subscriptions
        subscription_codes = [
            sub['code'] for sub in subscriptions
            if "code" in sub
        ]

        subscription_records = request.env[SUBSCRIPTION].search([
            ("code", "in", subscription_codes)
        ])

        if subscription_records.exists() and discon_status:
            function = discon_status.get("executable")
            if function:
                # Call function
                executable = eval(
                    "request.env[SUBSCRIPTION].%s"
                    % function
                )
                executable(subscription_records, discon_status.get("status"))

            http.Response.status = "200"
            serializer = Serializer(
                subscription_records,
                "{id, code, display_name, partner_id, subscription_status_subtype}",
                many=True
            )
            data = serializer.data
            res = {
                "success": {
                    "status": 200,
                    "message": "200 OK",
                    "code": 200,
                    "description": "",
                    "links": {
                        "about": "",
                    },
                },
                "data": data,
            }

            return res

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

            return json.dumps(res)
