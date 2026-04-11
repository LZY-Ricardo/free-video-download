import unittest

from app.main import should_enable_reload


class AppMainTestCase(unittest.TestCase):
    def test_windows_defaults_to_reload_disabled(self):
        self.assertFalse(should_enable_reload(platform_name="nt", env_value=""))

    def test_non_windows_defaults_to_reload_enabled(self):
        self.assertTrue(should_enable_reload(platform_name="posix", env_value=""))

    def test_env_can_force_reload_enabled(self):
        self.assertTrue(should_enable_reload(platform_name="nt", env_value="true"))

    def test_env_can_force_reload_disabled(self):
        self.assertFalse(should_enable_reload(platform_name="posix", env_value="false"))


if __name__ == "__main__":
    unittest.main()
