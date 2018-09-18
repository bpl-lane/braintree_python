from tests.test_helper import *
from distutils.version import LooseVersion
import platform
import braintree
import requests

class TestHttp(unittest.TestCase):
    if LooseVersion(requests.__version__) >= LooseVersion('1.0.0'):
        SSLError = requests.exceptions.SSLError
    else:
        SSLError = requests.models.SSLError

    @staticmethod
    def get_http(environment):
        config = Configuration(environment, "merchant_id", public_key="public_key", private_key="private_key")
        return config.http()

    @raises(AuthenticationError)
    def test_successful_connection_sandbox(self):
        http = self.get_http(Environment.Sandbox)
        http.get("/")

    @raises(AuthenticationError)
    def test_successful_connection_production(self):
        http = self.get_http(Environment.Production)
        http.get("/")

    def test_wrapping_http_exceptions(self):
        config = Configuration(
            Environment("test", "localhost", "1", False, None, Environment.Production.ssl_certificate),
            "integration_merchant_id",
            public_key="integration_public_key",
            private_key="integration_private_key",
            wrap_http_exceptions=True
        )

        gateway = braintree.braintree_gateway.BraintreeGateway(config)

        try:
            gateway.transaction.find("my_id")
        except braintree.exceptions.unexpected_error.UnexpectedError:
            correct_exception = True
        except Exception:
            correct_exception = False

        self.assertTrue(correct_exception)

    def test_unsuccessful_connection_to_good_ssl_server_with_wrong_cert(self):
        if platform.system() == "Darwin":
            return

        #any endpoint that returns valid XML with a status of 3xx or less and serves SSL
        environment = Environment("test", "aws.amazon.com/ec2", "443", "http://auth.venmo.dev:9292", True, Environment.Production.ssl_certificate)
        http = self.get_http(environment)
        try:
            http.get("/")
        except self.SSLError as e:
            self.assertTrue("certificate verify failed" in str(e))
        except AuthenticationError:
            self.fail("Expected to receive an SSL error but received an Authentication Error instead, check your local openssl installation")
        else:
            self.fail("Expected to receive an SSL error but no exception was raised")

    def test_unsuccessful_connection_to_ssl_server_with_wrong_domain(self):
        #ip address of api.braintreegateway.com
        environment = Environment("test", "204.109.13.121", "443", "http://auth.venmo.dev:9292", True, Environment.Production.ssl_certificate)
        http = self.get_http(environment)
        try:
            http.get("/")
        except self.SSLError:
            pass
        else:
            self.fail("Expected to receive an SSL error but no exception was raised")

    def test_timeouts(self):
        config = Configuration(
            Environment.Development,
            "integration_merchant_id",
            public_key="integration_public_key",
            private_key="integration_private_key",
            wrap_http_exceptions=True,
            timeout=0.001
        )

        gateway = braintree.braintree_gateway.BraintreeGateway(config)

        try:
            gateway.transaction.find("my_id")
        except braintree.exceptions.http.timeout_error.TimeoutError:
            correct_exception = True
        except Exception:
            correct_exception = False

        self.assertTrue(correct_exception)

    def test_read_timeouts(self):
        """It should handle a request read timeout."""
        try:
            raise requests.exceptions.ReadTimeout()
        except braintree.exceptions.http.timeout_error.ReadTimeoutError:
            correct_exception = True
        except Exception:
            correct_exception = False

        self.assertTrue(correct_exception)


    def test_connection_timeouts(self):
        """It should handle a request connection timeout."""
        try:
            raise requests.exceptions.ConnectTimeout()
        except braintree.exceptions.http.timeout_error.ConnectTimeoutError:
            correct_exception = True
        except Exception:
            correct_exception = False

        self.assertTrue(correct_exception)
