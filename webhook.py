#!/usr/bin/env python

import requests

class Webhook:
    def Post(webhookUrl, date, speed, unit, travelDirection):
        r = requests.post(webhookUrl, data = {
            'date': date,
            'speed': speed,
            'unit': unit,
            'travelDirection': travelDirection,
        })

        print(r)