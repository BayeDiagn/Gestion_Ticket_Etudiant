import requests
import json

class PayTech:
    URL = "https://paytech.sn"
    PAYMENT_REQUEST_PATH = '/api/payment/request-payment'
    PAYMENT_REDIRECT_PATH = '/payment/checkout/'
    MOBILE_CANCEL_URL = "https://paytech.sn/mobile/cancel"
    MOBILE_SUCCESS_URL = "https://paytech.sn/mobile/success"

    def __init__(self, apiKey, apiSecret):
        self.apiKey = apiKey
        self.apiSecret = apiSecret
        self.query = {}
        self.customeField = {}
        self.liveMode = True
        self.testMode = False
        self.isMobile = False
        self.currency = 'XOF'
        self.refCommand = ''
        self.notificationUrl = {}
        
        # Vérifier si le mode mobile est activé
        # if 'is_mobile' in requests.post().values and requests.post().values['is_mobile'] == 'yes':
        #     self.isMobile = True

    def send(self):
        params = {
            'item_name': self.query.get('item_name', ''),
            'item_price': self.query.get('item_price', ''),
            'command_name': self.query.get('command_name', ''),
            'ref_command': self.refCommand,
            'env': 'test' if self.testMode else 'prod',
            'currency': self.currency,
            'ipn_url': self.notificationUrl.get('ipn_url', ''),
            'success_url': self.MOBILE_SUCCESS_URL if self.isMobile else self.notificationUrl.get('success_url', ''),
            'cancel_url': self.MOBILE_CANCEL_URL if self.isMobile else self.notificationUrl.get('cancel_url', ''),
            'custom_field': json.dumps(self.customeField)
        }

        headers = {
            "API_KEY": self.apiKey,
            "API_SECRET": self.apiSecret,
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
        }

        response = requests.post(self.URL + self.PAYMENT_REQUEST_PATH, data=params, headers=headers)

        json_response = response.json()

        if 'token' in json_response:
            query = ''
            return {
                'success': 1,
                'token': json_response['token'],
                'redirect_url': self.URL + self.PAYMENT_REDIRECT_PATH + json_response['token'] + query
            }
        elif 'error' in json_response:
            return {
                'success': -1,
                'errors': json_response['error']
            }
        else:
            return {
                'success': -1,
                'errors': ['Internal Error']
            }

    # @staticmethod
    # def arrayGet(array, name, default=''):
    #     return array.get(name, default)

    @staticmethod
    def post(url, data=None, headers=None):
        response = requests.post(url, data=data, headers=headers)
        return response.text

    def setQuery(self, query):
        self.query = query
        return self

    def setCustomeField(self, customeField):
        if isinstance(customeField, dict):
            self.customeField = customeField
        return self

    def setLiveMode(self, liveMode):
        self.liveMode = liveMode
        self.testMode = not liveMode
        return self

    def setTestMode(self, testMode):
        self.testMode = testMode
        self.liveMode = not testMode
        return self

    def setCurrency(self, currency):
        self.currency = currency.lower()
        return self

    def setRefCommand(self, refCommand):
        self.refCommand = refCommand
        return self

    def setNotificationUrl(self, notificationUrl):
        self.notificationUrl = notificationUrl
        return self

    def setMobile(self, isMobile):
        self.isMobile = isMobile
        return self
