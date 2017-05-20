# -*- coding: utf-8 -*-
import json

from django.http import Http404

from edx_shopify.models import Order
from edx_shopify.tasks import process
from edx_shopify.utils import record_order

from . import JsonPayloadTestCase


class ProcessOrderTest(JsonPayloadTestCase):

    def test_invalid_sku(self):
        fixup_payload = self.raw_payload.replace("course-v1:org+course+run1",
                                                 "course-v1:org+nosuchcourse+run1")  # noqa: E501
        fixup_json_payload = json.loads(fixup_payload)
        order, created = record_order(fixup_json_payload)

        with self.assertRaises(Http404):
            result = process.delay(fixup_json_payload)
            result.get(5)

        # Even with the exception raised, it's the task failure
        # handler's job to set the status to ERROR
        readback_order = Order.objects.get(id=fixup_json_payload['id'])
        self.assertEqual(readback_order.status, Order.ERROR)
