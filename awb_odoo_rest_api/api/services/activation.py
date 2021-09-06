from odoo import http, fields, models
from odoo.http import request
from .authentication import OdooAPI 

import importlib
import json

Serializer = importlib.import_module(
    "odoo.addons.odoo-rest-api"
).controllers.serializers.Serializer

SUBSCRIPTION = "sale.subscription"

class AWBOdooActivationAPI(OdooAPI):

    @http.route('/awb/activate_users/', type='json', auth='user', methods=["PUT"], csrf=False)
    def _activate_users(self, user_ids=None):
        if not user_ids:
            res = {
              "errors": [
                {
                  "status": 400,
                  "message": "Bad Request",
                  "code": 352,
                  "description": "required parameters: <user_ids>, <subs_status: expired/ exceed_usage>",
                  "links": {
                    "about": "http://www.domain.com/rest/errorcode/352"
                  },
                  "data": {},
                  "data_count": {},
                }
              ]
            }

            return json.dumps(res)

        records = request.env[SUBSCRIPTION].search([('code', 'in', user_ids)])

        print(records, flush=True)
        for record in records:
            record.write(
                {
                  "is_active": True
                }
            )

        serializer = Serializer(records, "{code, partner_id, partner_id.name}", many=True)
        data = serializer.data
        res = {
            "success": [{
                "status": 200,
                "message": "User found!",
                "code": 200,
                "description": "",
                "links": {
                  "about": "",
                },
                "data": data,
                "data_count": len(data),
            }]
        }

        return res
