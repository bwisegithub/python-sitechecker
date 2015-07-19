#!/usr/bin/env python
""" Contain TestSiteChecker class
"""
from StringIO import StringIO
import sys
import unittest

from sitechecker import main


class TestSiteChecker(unittest.TestCase):
    """ Encapsulate the properties and tasks related to testing the sitechecker
    package.
    """
    __NO_ARGS_PROVIDED_MSG = 'Please provide --site or --file as argument'
    __INVALID_ARGS_PROVIDED_MSG = 'unrecognized arguments: '
    __SITE_INSUFF_ARGS_PROVIDED_MSG = \
        'argument -s/--site: expected one argument'
    __SITE_INVALID_URL_FORMAT_MSG = 'Expecting URL in format like'
    __SITE_OK_URL_BUT_INVAL_TLD_MSG = \
        'HTTP Error: 404 Client Error: Not Found'
    __SITE_OK_URL_BUT_NOT_REAL = \
        'HTTP Error: 400 Client Error: Bad Request'
    __FILE_INSUFF_ARGS_PROVIDED_MSG = \
        'argument -f/--file: expected one argument'
    __FILE_DOES_NOT_EXIST_MSG = 'No such file or directory'
    __WOT_EXPECTED_STR = 'Child safety'
    __SUCURI_EXPECTED_STR = 'System Details'
    __GOOGLE_EXPECTED_STR = 'Minify JavaScript'
    __W3_MARKUP_EXPECTED_STR = 'errorcount'
    __W3_CSS_EXPECTED_STR = 'warningcount'

    __saved_stdout = None
    __saved_stderr = None
    __out = None
    __outerr = None
    __output = None
    __outputerr = None

    def __redirect_std(self):
        """ Redirect standard output and error to supress normal screen output
        during testing.  Capture for later analysis.
        """
        self.__saved_stdout = sys.stdout
        self.__saved_stderr = sys.stderr
        self.__out = StringIO()
        sys.stdout = self.__out
        self.__outerr = StringIO()
        sys.stderr = self.__outerr

    def __restore_std(self):
        """ Restore standard output and error, retaining what was captured
        for later analysis.
        """
        sys.stdout = self.__saved_stdout
        sys.stderr = self.__saved_stderr
        self.__output = self.__out.getvalue().strip()
        self.__outputerr = self.__outerr.getvalue().strip()

    def __get_wot_match_cnt(self):
        """ Get and return count of expected string occurences for WOT results.
        """
        cnt = self.__output.count(self.__WOT_EXPECTED_STR)
        if cnt == 0:
            print 'Unexpected WOT Scorecard Output'
        return cnt

    def __get_sucuri_match_cnt(self):
        """ Get and return count of expected string occurences for Sucuri
        results.
        """
        cnt = self.__output.count(self.__SUCURI_EXPECTED_STR)
        if cnt == 0:
            print 'Unexpected Sucuri Sitecheck Output'
        return cnt

    def __get_google_match_cnt(self):
        """ Get and return count of expected string occurences for Google
        results.
        """
        cnt = self.__output.count(self.__GOOGLE_EXPECTED_STR)
        if cnt == 0:
            print 'Unexpected Google Pagespeed Insights Output'
        return cnt

    def __get_w3_markup_match_cnt(self):
        """ Get and return count of expected string occurences for W3 Markup
        results.
        """
        cnt = self.__output.count(self.__W3_MARKUP_EXPECTED_STR)
        if cnt == 0:
            print 'Unexpected W3 Markup Validation Output'
        return cnt

    def __get_w3_css_match_cnt(self):
        """ Get and return count of expected string occurences for W3 CSS3
        results.
        """
        cnt = self.__output.count(self.__W3_CSS_EXPECTED_STR)
        if cnt == 0:
            print 'Unexpected W3 CSS3 Validation Output'
        return cnt

    def __is_all_checker_output_ok(self, num_of_urls):
        """ Return True if all the expected string occurences in all results
        are as expected (else False) for the given num_of_urls.
        """
        # See github issue #3; the following line removed indefinitely:
        # self.__get_w3_markup_match_cnt() >= num_of_urls and \
        return self.__get_wot_match_cnt() >= num_of_urls and \
            self.__get_sucuri_match_cnt() >= num_of_urls and \
            self.__get_google_match_cnt() >= num_of_urls and \
            self.__get_w3_css_match_cnt() >= num_of_urls

    def test_no_args(self):
        """ Test input: no args to script.

        Example: pass [no arguments] as an option.
        """
        self.__redirect_std()
        sys.argv = ['main.py']
        try:
            main.main()
        except:
            pass
        finally:
            self.__restore_std()
            assert self.__outputerr.endswith(self.__NO_ARGS_PROVIDED_MSG), \
                self.__outputerr

    def test_invalid_args(self):
        """ Test input: invalid args for script.

        Example: pass -a as an option.
        """
        test_arg = '-a'
        self.__redirect_std()
        sys.argv = ['main.py', test_arg]
        try:
            main.main()
        except:
            pass
        finally:
            self.__restore_std()
            assert self.__outputerr.endswith(self.__INVALID_ARGS_PROVIDED_MSG \
                + test_arg), self.__outputerr

    def test_site_insufficient_args(self):
        """ Test input: insufficient args for -s(ite) option.

        Example: pass -s [but no URL] as an option.
        """
        test_arg = '-s'
        self.__redirect_std()
        sys.argv = ['main.py', test_arg]
        try:
            main.main()
        except:
            pass
        finally:
            self.__restore_std()
            assert self.__outputerr.endswith( \
                self.__SITE_INSUFF_ARGS_PROVIDED_MSG), self.__outputerr

    def test_site_invalid_url_format(self):
        """ Test input: invalid URL format for -s(ite) option.

        Example: pass -s not_a_url as an option.
        """
        test_args = ['-s', 'not_a_url']
        self.__redirect_std()
        sys.argv = ['main.py', test_args[0], test_args[1]]
        try:
            main.main()
        except:
            pass
        finally:
            self.__restore_std()
            assert self.__SITE_INVALID_URL_FORMAT_MSG in self.__output, \
                self.__output

    def test_site_unexpect_url_format(self):
        """ Test input: unexpected URL for -s(ite) option.

        Example: pass -s http://www.google.com as an option.
        """
        test_args = ['-s', 'http://www.google.com']
        self.__redirect_std()
        sys.argv = ['main.py', test_args[0], test_args[1]]
        try:
            main.main()
        except:
            pass
        finally:
            self.__restore_std()
            assert self.__SITE_INVALID_URL_FORMAT_MSG in self.__output, \
                self.__output

    def test_site_unexpect_url_format2(self):
        """ Test input: unexpected URL for -s(ite) option.

        Example: pass -s www.google.com/maps as an option.
        """
        test_args = ['-s', 'www.google.com/maps']
        self.__redirect_std()
        sys.argv = ['main.py', test_args[0], test_args[1]]
        try:
            main.main()
        except:
            pass
        finally:
            self.__restore_std()
            assert self.__SITE_INVALID_URL_FORMAT_MSG in self.__output, \
                self.__output

    def test_site_ok_url_but_inval_tld(self):
        """ Test input: valid URL syntax but invalid TLD for -s(ite) option.

        Example: pass -s abc.defg.hij as an option.
        """
        test_args = ['-s', 'abc.defg.hij']
        self.__redirect_std()
        sys.argv = ['main.py', test_args[0], test_args[1]]
        try:
            main.main()
        except:
            pass
        finally:
            self.__restore_std()
            assert self.__SITE_OK_URL_BUT_INVAL_TLD_MSG in \
                self.__output, self.__output

    def test_site_ok_url_but_not_real(self):
        """ Test input: valid URL syntax and TLD but not real domain for
        -s(ite) option.

        Example: pass -s adjflsdjdfjl.com as an option.
        """
        test_args = ['-s', 'adjflsdjdfjl.com']
        self.__redirect_std()
        sys.argv = ['main.py', test_args[0], test_args[1]]
        try:
            main.main()
        except:
            pass
        finally:
            self.__restore_std()
            assert self.__SITE_OK_URL_BUT_NOT_REAL \
                in self.__output, self.__output

    def test_file_insufficient_args(self):
        """ Test input: insufficient args for -f(ile) option.

        Example: pass -f [but no file path] as an option.
        """
        test_arg = '-f'
        self.__redirect_std()
        sys.argv = ['main.py', test_arg]
        try:
            main.main()
        except:
            pass
        finally:
            self.__restore_std()
            assert self.__outputerr.endswith( \
                self.__FILE_INSUFF_ARGS_PROVIDED_MSG), self.__outputerr

    def test_file_does_not_exist(self):
        """ Test input: file does not exist for -f(ile) option.

        Example: pass -f /I/do/not/exist as an option.
        """
        test_args = ['-f', '/I/do/not/exist']
        self.__redirect_std()
        sys.argv = ['main.py', test_args[0], test_args[1]]
        try:
            main.main()
        except:
            pass
        finally:
            self.__restore_std()
            assert self.__FILE_DOES_NOT_EXIST_MSG in self.__outputerr, \
                self.__outputerr

    def test_file_contents_invalid(self):
        """ Test input: file contents are invalid for -f(ile) option.

        Example: pass -f sample_input_url_list_bad.txt as an option.
        """
        test_args = ['-f', 'sample_input_url_list_bad.txt']
        self.__redirect_std()
        sys.argv = ['main.py', test_args[0], test_args[1]]
        try:
            main.main()
        except:
            pass
        finally:
            self.__restore_std()
            assert self.__SITE_INVALID_URL_FORMAT_MSG in self.__output, \
                self.__output

    def test_site_normal_one_url(self):
        """ Test normal response for one URL for -s(ite) option.

        Example: pass -s apple.com as an option.
        """
        num_of_urls = 1
        test_args = ['-s', 'apple.com']
        self.__redirect_std()
        sys.argv = ['main.py', test_args[0], test_args[1]]
        try:
            main.main()
        except:
            pass
        finally:
            self.__restore_std()
            assert self.__is_all_checker_output_ok(num_of_urls), self.__output

    def test_site_normal_one_url_w_www(self):
        """ Test normal response for one www. URL for -s(ite) option.

        Example: pass -s www.apple.com as an option.
        """
        num_of_urls = 1
        test_args = ['-s', 'www.apple.com']
        self.__redirect_std()
        sys.argv = ['main.py', test_args[0], test_args[1]]
        try:
            main.main()
        except:
            pass
        finally:
            self.__restore_std()
            assert self.__is_all_checker_output_ok(num_of_urls), self.__output

    def test_site_normal_multi_url(self):
        """ Test normal response for multiple URLs for -f(ile) option.

        Example: pass -f sample_input_url_list.txt as an option.
        """
        file_name = 'sample_input_url_list.txt'
        i = 0
        with open(file_name) as url_file:
            for i, line in enumerate(url_file):
                pass
        num_of_urls = i + 1
        test_args = ['-f', file_name]
        self.__redirect_std()
        sys.argv = ['main.py', test_args[0], test_args[1]]
        try:
            main.main()
        except:
            pass
        finally:
            self.__restore_std()
            assert self.__is_all_checker_output_ok(num_of_urls), self.__output


if __name__ == '__main__':
    unittest.main()

