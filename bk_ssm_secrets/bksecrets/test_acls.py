# import pytest, os
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
import os
from . import bksecrets
import boto3
from botocore.stub import Stubber

class TestAclMethods(unittest.TestCase):
    def test_check_pipeline_acl(self):
        print("acls")
        client = boto3.client('ssm', region_name='ap-southwest-2')
        stubber = Stubber(client)
        # stub.add_response(...)
        # store = ssm_parameter_store.SSMParameterStore(prefix='/path', ssm_client=stubber)
        secrets = bksecrets.BkSecrets(ssm_client=stubber, base_path='/path')
        # with patch.dict(os.environ, {'BUILDKITE_PIPELINE_SLUG': 'zip'}, clear=True):
        #     assert(secrets.check_pipeline_acl() == 'zip')
        
        assert(secrets.check_pipeline_acl() == True)

if __name__ == '__main__':
    unittest.main()