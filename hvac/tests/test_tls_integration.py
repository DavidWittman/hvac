from unittest import TestCase

from nose.plugins.attrib import attr
from nose.tools import *
import requests

from hvac import Client, exceptions
from hvac.tests import util

def create_client():
    return Client(url='https://localhost:8200',
                  cert=('test/client-cert.pem', 'test/client-key.pem'),
                  verify='test/server-cert.pem')

@attr(tls=True)
class TLSIntegrationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manager = util.ServerManager(config_path='test/vault-tls.hcl', client=create_client())
        cls.manager.start()
        cls.manager.initialize()
        cls.manager.unseal()

    @classmethod
    def tearDownClass(cls):
        cls.manager.stop()

    def setUp(self):
        cls = type(self)

        self.client = create_client()
        self.client.auth_token(cls.manager.root_token)

    def test_tls_auth(self):
        self.client.enable_auth_backend('cert')

        with open('test/client-cert.pem') as fp:
            certificate = fp.read()

        self.client.write('auth/cert/certs/test', display_name='test',
                          policies='root', certificate=certificate)

        result = self.client.auth_tls()
