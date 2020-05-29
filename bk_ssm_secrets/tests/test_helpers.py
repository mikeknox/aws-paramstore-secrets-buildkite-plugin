from unittest import TestCase, mock
import os
from .. import helpers

class TestHelpers(TestCase):
    def test_url_to_slug(self):
        assert(helpers.url_to_slug("https://github.com/a/b.git") == "github.com_a_b.git")
        assert(helpers.url_to_slug("https://github.com/a/b.git") == "github.com_a_b.git")
        assert(helpers.url_to_slug("git@github.com:a/b.git") == "github.com_a_b.git")
        assert(helpers.url_to_slug("user@github.com:a/b.git") == "github.com_a_b.git")
        assert(helpers.url_to_slug("https://git@github.com/a/b.git") == "github.com_a_b.git")
        assert(helpers.url_to_slug("ssh://git@github.com/a/b.git") == "github.com_a_b.git")
        assert(helpers.url_to_slug("ssh://git@github.com:22/a/b.git") == "github.com-22_a_b.git")
        assert(helpers.url_to_slug("https://github.com:8080/a/b.git") == "github.com-8080_a_b.git")
        assert(helpers.url_to_slug("https://github.com:8080/~a/b.git") == "github.com-8080__a_b.git")

    def test_get_buildkite_teams(self):
        with mock.patch.dict(os.environ, {'BUILDKITE_BUILD_CREATOR_TEAMS': 'team1:team2'}, clear=True):
          assert(helpers.get_buildkite_teams() == {'team1', 'team2'})
        with mock.patch.dict(os.environ, {'BUILDKITE_UNBLOCKER_TEAMS': 'team3:team4'}, clear=True):
          assert(helpers.get_buildkite_teams() == {'team3', 'team4'})
        with mock.patch.dict(os.environ, {
            'BUILDKITE_BUILD_CREATOR_TEAMS': 'team1:team2',
            'BUILDKITE_UNBLOCKER_TEAMS': 'team3:team4'
          }, clear=True):
          assert(helpers.get_buildkite_teams() == {'team1', 'team2', 'team3', 'team4'})
        with mock.patch.dict(os.environ, {
            'BUILDKITE_BUILD_CREATOR_TEAMS': 'team1:team2',
            'BUILDKITE_UNBLOCKER_TEAMS': 'team1:team2'
          }, clear=True):
            assert(helpers.get_buildkite_teams() == {'team1', 'team2'})
        with mock.patch.dict(os.environ, {
            'BUILDKITE_BUILD_CREATOR_TEAMS': '',
            'BUILDKITE_UNBLOCKER_TEAMS': ''
          }, clear=True):
            assert(helpers.get_buildkite_teams() == set())

if __name__ == '__main__':
    unittest.main()
