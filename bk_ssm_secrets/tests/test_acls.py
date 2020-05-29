from unittest import TestCase, mock
import os
from ..bksecrets import BkSecrets
from ..ssm_parameter_store import SSMParameterStore

class TestAclMethods(TestCase):
    def test_check_team_allowed(self):
      get_buildkite_teams = lambda: {'team1', 'team2'}
      with mock.patch.object(SSMParameterStore, '__init__', return_value=None):
        secrets = BkSecrets('/path')
        with mock.patch.object(SSMParameterStore, '__contains__', return_value='allowed_pipelines'):
          with mock.patch.dict(os.environ, {
              'BUILDKITE_PIPELINE_SLUG': 'zip',
              'BUILDKITE_SOURCE': 'api'
            }, clear=True):
            # get_buildkite_teams = MagicMock(return_value=get_teams)
            with mock.patch.object(SSMParameterStore, 'get', return_value='no_team'):
              with self.assertRaises(RuntimeError):
                secrets.check_team_allowed()

      get_buildkite_teams = lambda: {}
      # No teams set
      # scheduler set
      with mock.patch.object(SSMParameterStore, '__init__', return_value=None):
        secrets = BkSecrets('/path')
        with mock.patch.object(SSMParameterStore, '__contains__', return_value='allowed_pipelines'):
          with mock.patch.dict(os.environ, {
              'BUILDKITE_PIPELINE_SLUG': 'zip',
              'BUILDKITE_SOURCE': 'schedule'
            }, clear=True):
            # get_buildkite_teams = MagicMock(return_value=get_teams)
            with mock.patch.object(SSMParameterStore, 'get', return_value='no_team'):
              assert(secrets.check_team_allowed() == None)

if __name__ == '__main__':
    unittest.main()