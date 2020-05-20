import unittest
from . import helpers

class TestHelpers(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
