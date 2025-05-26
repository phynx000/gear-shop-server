import hashlib
import hmac
import urllib
from urllib.parse import urlencode


class VNPay:
    """
    VNPAY Payment Gateway integration using the official implementation style
    """
    requestData = {}
    responseData = {}

    def get_payment_url(self, vnpay_payment_url, secret_key):
        """
        Generate the payment URL according to VNPAY's specification
        """
        # Sort input data to ensure consistent ordering
        inputData = sorted(self.requestData.items())
        queryString = ''
        seq = 0

        # Build query string with proper URL encoding
        for key, val in inputData:
            if seq == 1:
                queryString = queryString + "&" + key + '=' + urllib.parse.quote_plus(str(val))
            else:
                seq = 1
                queryString = key + '=' + urllib.parse.quote_plus(str(val))

        # Generate HMAC-SHA512 hash
        hashValue = self.__hmacsha512(secret_key, queryString)

        # Return full payment URL
        return vnpay_payment_url + "?" + queryString + '&vnp_SecureHash=' + hashValue

    def validate_response(self, secret_key):
        """
        Validate the response data from VNPAY
        """
        # Get the secure hash from response
        vnp_SecureHash = self.responseData['vnp_SecureHash']

        # Remove hash params
        if 'vnp_SecureHash' in self.responseData.keys():
            self.responseData.pop('vnp_SecureHash')

        if 'vnp_SecureHashType' in self.responseData.keys():
            self.responseData.pop('vnp_SecureHashType')

        # Sort and build hash data string
        inputData = sorted(self.responseData.items())
        hasData = ''
        seq = 0

        for key, val in inputData:
            # Only include vnp_ parameters in the hash calculation
            if str(key).startswith('vnp_'):
                if seq == 1:
                    hasData = hasData + "&" + str(key) + '=' + urllib.parse.quote_plus(str(val))
                else:
                    seq = 1
                    hasData = str(key) + '=' + urllib.parse.quote_plus(str(val))

        # Generate hash for verification
        hashValue = self.__hmacsha512(secret_key, hasData)

        # print(f'Validate debug, HashData: {hasData}\nHashValue: {hashValue}\nInputHash: {vnp_SecureHash}')

        # Compare the generated hash with the provided hash
        return vnp_SecureHash == hashValue

    @staticmethod
    def __hmacsha512(key, data):
        """
        Generate HMAC-SHA512 hash
        """
        byteKey = key.encode('utf-8')
        byteData = data.encode('utf-8')
        return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()