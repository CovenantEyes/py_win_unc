from unittest import TestCase

from win_unc import unc_directory as U
from win_unc.unc_directory import UncDirectory, UncCredentials


class TestUncDirectory(TestCase):
    def test_eq_and_ne(self):
        self.assertEqual(UncDirectory(r'\\path'), UncDirectory(r'\\path'))
        self.assertEqual(UncDirectory(r'\\path'), UncDirectory(r'\\PATH'))

        self.assertEqual(UncDirectory(r'\\path', 'username'), UncDirectory(r'\\path', 'username'))
        self.assertEqual(UncDirectory(r'\\path', 'username'), UncDirectory(r'\\PATH', 'username'))
        self.assertNotEqual(UncDirectory(r'\\path', 'username'), UncDirectory(r'\\path', 'USERNAME'))

        self.assertEqual(UncDirectory(r'\\path', 'username', 'password'),
                         UncDirectory(r'\\path', 'username', 'password'))
        self.assertEqual(UncDirectory(r'\\path', 'username', 'password'),
                         UncDirectory(r'\\PATH', 'username', 'password'))
        self.assertNotEqual(UncDirectory(r'\\path', 'username', 'password'),
                            UncDirectory(r'\\path', 'username', 'PASSWORD'))

        self.assertNotEqual(UncDirectory(r'\\path'), None)
        self.assertNotEqual(UncDirectory(r'\\path'), 'somestring')

    def test_get_normalized_path(self):
        self.assertEqual(UncDirectory(r'\\abc').get_normalized_path(), r'\\abc')
        self.assertEqual(UncDirectory(r'\\ABC').get_normalized_path(), r'\\abc')
        self.assertEqual(UncDirectory(r'\\abc\def').get_normalized_path(), r'\\abc\def')
        self.assertEqual(UncDirectory(r'\\abc\DEF').get_normalized_path(), r'\\abc\def')
        self.assertEqual(UncDirectory(r'\\abc\def\\').get_normalized_path(), r'\\abc\def')
        self.assertEqual(UncDirectory(r'\\abc\IPC$').get_normalized_path(), r'\\abc')
        self.assertEqual(UncDirectory(r'\\abc\ipc$').get_normalized_path(), r'\\abc')

    def test_str(self):
        self.assertEqual(str(UncDirectory(r'\\path')), r'\\path')
        self.assertEqual(str(UncDirectory(r'\\path', 'user')), r'user@\\path')
        self.assertEqual(str(UncDirectory(r'\\path', 'user', 'pass')), r'user:pass@\\path')

    def test_stringlike(self):
        self.assertEqual(UncDirectory(r'\\path'), r'\\path')
        self.assertEqual(r'\\path', UncDirectory(r'\\path'))


class TestUncCredentials(TestCase):
    def test_get_auth_string(self):
        self.assertEqual(UncCredentials(None, None).get_auth_string(), '')
        self.assertEqual(UncCredentials('', None).get_auth_string(), '')
        self.assertEqual(UncCredentials(None, '').get_auth_string(), ':')
        self.assertEqual(UncCredentials('', '').get_auth_string(), ':')

        self.assertEqual(UncCredentials('user', None).get_auth_string(), 'user')
        self.assertEqual(UncCredentials('user', '').get_auth_string(), 'user:')

        self.assertEqual(UncCredentials('', 'pass').get_auth_string(), ':pass')
        self.assertEqual(UncCredentials('user', ':').get_auth_string(), 'user::')
        self.assertEqual(UncCredentials('user', 'pass').get_auth_string(), 'user:pass')


class TestUncParsingFunctions(TestCase):
    def test_get_creds_from_string(self):
        self.assertEqual(U.get_creds_from_string(''), UncCredentials(None, None))
        self.assertEqual(U.get_creds_from_string('user'), UncCredentials('user', None))
        self.assertEqual(U.get_creds_from_string('user'), UncCredentials('user', None))

        self.assertEqual(U.get_creds_from_string(':""'), UncCredentials(None, '""'))
        self.assertEqual(U.get_creds_from_string('::'), UncCredentials(None, ':'))
        self.assertEqual(U.get_creds_from_string(':pass'), UncCredentials(None, 'pass'))

        self.assertEqual(U.get_creds_from_string('user:'), UncCredentials('user', ''))
        self.assertEqual(U.get_creds_from_string('user:pass'), UncCredentials('user', 'pass'))
        self.assertEqual(U.get_creds_from_string('user::'), UncCredentials('user', ':'))

    def test_get_unc_directory_from_string(self):
        self.assertEqual(U.get_unc_directory_from_string(r'\\path'), UncDirectory(r'\\path'))
        self.assertEqual(U.get_unc_directory_from_string(r'\\path\sub'),
                         UncDirectory(r'\\path\sub'))
        self.assertEqual(U.get_unc_directory_from_string(r'user@\\path'),
                         UncDirectory(r'\\path', 'user'))
        self.assertEqual(U.get_unc_directory_from_string(r':pass@\\path'),
                         UncDirectory(r'\\path', None, 'pass'))
        self.assertEqual(U.get_unc_directory_from_string(r'::@\\@\\path'),
                         UncDirectory(r'\\path', None, r':@\\'))
        self.assertEqual(U.get_unc_directory_from_string(r'user:pass@\\path'),
                         UncDirectory(r'\\path', 'user', 'pass'))
        self.assertEqual(U.get_unc_directory_from_string(r'user::@\\@\\path'),
                         UncDirectory(r'\\path', 'user', r':@\\'))
