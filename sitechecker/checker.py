""" Contains SiteChecker class
"""
import abc
import json
import re

import bs4
import requests

from sitechecker import utils


class SiteChecker:
    """ Encapsulate the properties and tasks related to a URL checker.

    A site checker is a web site that takes a URL (i.e. domain or web site
    name) and returns some type of insight into the security, performance, etc.
    of the URL.

    Example: Google PageSpeed Insights is a type of site checker that provides
    a score and information on the load time for the landing page of a URL, and
    analysis on what negatively impacts that load time.
    """
    __metaclass__ = abc.ABCMeta

    _PAGE_WIDTH = 80
    _MAX_MSG_LENGTH = 60
    _MAX_RESULTS_TO_DISPLAY = 10

    def __init__(self, name, base_url, get_or_post):
        """  Initialize an instance of the class.

        :param name:  A user-friendly name to represent the type of checker
            (example: GOOGLE PAGESPEED INSIGHTS)
        :param base_url:  The base URL for the checker (example:
            http://checkyoursiteforbadstuff.com/uri=)
        :param get_or_post: The type of HTTP request for the checker
            (examples: GET or POST)
        """
        self.name = name
        self.base_url = base_url
        self.get_or_post = get_or_post

    @classmethod
    def is_valid_url(cls, url_to_check):
        """ Validate string for URL syntax.

        Assumes Top Level Domain (TLD) max length of 6 and nothing after TLD.

        :param url_to_check: URL from user input
        :return bool:  True if valid, False if not
        """
        if utils.is_non_empty_str(url_to_check):
            # if re.match(r'[-a-zA-Z0-9@:%._\+~#=]{2,256}\.
            #   [a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)', url_to_check):
            # Above URL regex too permissive for my use but others may want to
            # allow for multisite etc (if so additional testing needed).
            if re.match(r'[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}$',\
                url_to_check):
                # OK
                return True
            else:
                print
                print 'Expecting URL in format like www.google.com'
                print 'Received: {}'.format(url_to_check)
                return False

    @classmethod
    def _display_max_results_exceeded(cls):
        """ Print informational message indicating that the maximum number
        of results has been exceeded and how many results were displayed.
        """
        print '(More than {} results.  Displayed first {}.)'.\
            format(SiteChecker._MAX_RESULTS_TO_DISPLAY, SiteChecker.\
                _MAX_RESULTS_TO_DISPLAY)

    def process_url(self, url_to_check):
        """ Process URL by:
        - Passing url_to_check as URL parameter to checker site
        (example: Google Page Insights).
        - Displaying parsed results.

        :param url_to_check: URL from user input
        """
        if utils.is_non_empty_str(url_to_check):
            url_read_soup = self.__request_checker_url(self.base_url +\
                url_to_check)

            # Call child's implementation
            self.display_results(url_read_soup, url_to_check)

    def __request_checker_url(self, checker_url):
        """ HTTP Request the checker_url which includes the appended
        url_to_check from the user input and return the response as a
        bs4.BeautifulSoup object
        """
        if utils.is_non_empty_str(checker_url):
            header_dict = {
                'user-agent': 'Mozilla'
            }
            try:
                if self.get_or_post == 'POST':
                    response = requests.post(checker_url, timeout=60,\
                        headers=header_dict)
                else:
                    response = requests.get(checker_url, timeout=60,\
                        headers=header_dict)

                response.raise_for_status()
                return bs4.BeautifulSoup(response.text)
            except:
                utils.display_exception(opt_prepend='URL: ' + checker_url)
                # Not reachable, so no return

    def _display_type_of_check_header(self):
        """ Print the user-friendly name of the checker (example: GOOGLE
        PAGESPEED INSIGHTS).
        """
        print
        # Center the heading
        print '{}{} RESULTS'.format((SiteChecker._PAGE_WIDTH/2-len(self.name)\
            /2) * ' ', self.name)
        print

    @abc.abstractmethod
    def display_results(self, url_read_soup, url_to_check):
        """ Override with checker-specific HTTP response parsing.

        Print parsed results from checker site.

        :param url_read_soup: bs4.BeautifulSoup object created by requesting
            checker site URL
        :param url_to_check: (Optional) URL from user input that was passed
            checker site for checking
        """
        pass


class WotChecker(SiteChecker):
    """ Extend SiteChecker for WOT-specific processing.
    """

    def display_results(self, url_read_soup, url_to_check=None):
        """ Override SiteChecker.display_results() with WOT-specific HTTP
        response parsing.

        Print parsed WOT results.

        :param url_read_soup: bs4.BeautifulSoup object created by requesting
            WOT scorecard URL
        :param url_to_check: None (not needed here)
        """
        self._display_type_of_check_header()
        if url_read_soup is not None:
            try:
                country = url_read_soup.find(id='country')
                print 'Server location: {}'.format(country['alt'])

                for items in url_read_soup('div', {'class': 'rep-comp'}):
                    print items.get_text(': ', strip=True)
            except:
                utils.display_exception()
        print


class SucuriChecker(SiteChecker):
    """ Extend SiteChecker for Sucuri-specific processing.
    """

    def display_results(self, url_read_soup, url_to_check):
        """ Override SiteChecker.display_results() with Sucuri site
        check-specific HTTP response parsing.

        Prints parsed Sucuri results.

        :param url_read_soup: bs4.BeautifulSoup object created by requesting
            Sucuri SiteChecker URL
        :param url_to_check: URL from user input that was passed to Sucuri for
            checking
        """
        self._display_type_of_check_header()
        if url_read_soup is not None:
            try:
                print 'Scan Results:'
                for trs in url_read_soup('table',\
                    {'class': 'table scan-findings'})[0].tbody('tr'):
                    tds = trs('td')
                    print '{}: {} ({})'.format(tds[0].string,\
                        tds[1].string, tds[2].string)

                print
                print 'Blacklist Results:'
                for trs in url_read_soup('table',\
                    {'class': 'table scan-findings'})[1].tbody('tr'):
                    tds = trs('td')
                    print '{}'.format(tds[0].string)

                print
                print 'Website Details:'
                details_panel = url_read_soup.find(id='sitecheck-details')
                collapse_one = details_panel.find(id='collapseOne')
                # It is not sufficient to .strip collapse_one get_text, so will
                # split on the new lines and strip individually, and then omit
                # anything left that is empty.  Troublemakers.
                collapse_one_lines = \
                    collapse_one.get_text().strip().splitlines()
                for line in collapse_one_lines:
                    if line.strip() != '':
                        print line.strip()

                print
                print 'List of Links Found to Other Domains or Sub Domains:'
                collapse_two = details_panel.find(id='collapseTwo')
                if collapse_two is not None:
                    collapse_two_lines = \
                        collapse_two.get_text().strip().splitlines()
                    line_cnt = 0
                    for line in collapse_two_lines:
                        if line.startswith('http')\
                            and not line.replace('http://', '').\
                                replace('https://', '').\
                                replace('www.', '').\
                                startswith(url_to_check.replace('www.', '')):
                            line_cnt += 1
                            if line_cnt < SiteChecker._MAX_RESULTS_TO_DISPLAY:
                                print line
                            else:
                                SiteChecker._display_max_results_exceeded()
                                break

                print
                print 'List of Scripts Included:'
                collapse_three = details_panel.find(id='collapseThree')
                if collapse_three is not None:
                    collapse_three_lines = collapse_three.get_text().strip().\
                        splitlines()
                    line_cnt = 0
                    for line in collapse_three_lines:
                        line_cnt += 1
                        if line_cnt < SiteChecker._MAX_RESULTS_TO_DISPLAY:
                            print line
                        else:
                            SiteChecker._display_max_results_exceeded()
                            break
            except:
                utils.display_exception()
        print


class GoogleChecker(SiteChecker):
    """ Extend SiteChecker for Google-specific processing.
    """

    def display_results(self, url_read_soup, url_to_check=None):
        """ Override SiteChecker.display_results() with Google-specific
        HTTP response parsing.

        Print parsed Google results.

        :param url_read_soup: bs4.BeautifulSoup object created by requesting
            Google PageSpeed Insights URL
        :param url_to_check: None (not needed here)
        """
        self._display_type_of_check_header()
        if url_read_soup is not None:
            try:
                soup_dict = json.loads(str(url_read_soup))
            except:
                utils.display_exception(opt_prepend='Unexpected response '\
                    'or invalid JSON response.')

            try:
                print 'PageSpeed score: {} / 100'.format(soup_dict['score'])

                print
                print 'Page stats:'
                for key, value in soup_dict['pageStats'].items():
                    print '{}: {}'.format(key, value)

                print
                print 'Rules negatively impacting score:'
                for i in soup_dict['formattedResults']['ruleResults']:
                    print '{}: {}'.format(soup_dict['formattedResults']\
                        ['ruleResults'][i]['localizedRuleName'],\
                        soup_dict['formattedResults']['ruleResults'][i]\
                        ['ruleImpact'])
            except:
                utils.display_exception()
        print


class W3MarkupChecker(SiteChecker):
    """ Extend SiteChecker for W3 Markup Validation-specific processing.
    """

    def display_results(self, url_read_soup, url_to_check=None):
        """ Override SiteChecker.display_results() with W3 Markup
        Validation-specific HTTP response parsing.

        Print parsed W3 Markup Validation results.

        :param url_read_soup: bs4.BeautifulSoup object created by requesting W3
            Markup Validation URL
        :param url_to_check: None (not needed here)
        """
        self._display_type_of_check_header()
        if url_read_soup is not None:
            # Strip the "explanation" key/value, which we don't need and often
            # causes the JSON to be invalid and thus unable to be loaded
            url_read_soup_str = str(url_read_soup)
            url_read_soup_str = re.sub('"explanation":.+', '',\
                url_read_soup_str)

            soup_dict = {}
            try:
                soup_dict = json.loads(url_read_soup_str)
            except:
                utils.display_exception(opt_prepend='Unexpected response '\
                    'or invalid JSON response.')

            try:
                # The first markup error is a generic one so don't count it if
                # presented
                print 'errorcount: {}'.format(len(soup_dict['messages'])-1 \
                    if len(soup_dict['messages']) > 0 else 0)
                print

                err_cnt = 0
                message = ''
                last_line = ''
                last_column = ''
                for i in soup_dict['messages']:
                    message = i['message']
                    if len(message) > SiteChecker._MAX_MSG_LENGTH:
                        message = '{} ...'.format(message[:SiteChecker.\
                            _MAX_MSG_LENGTH])
                    if message != 'This interface to HTML5 document checking '\
                            'is deprecated.':
                        err_cnt += 1
                        if err_cnt <= SiteChecker._MAX_RESULTS_TO_DISPLAY:
                            last_line = i['lastLine'] if 'lastLine' in \
                                i.keys() else ''
                            last_column = i['lastLine'] if 'lastColumn' in \
                                i.keys() else ''
                            print '({}) Line {}: Column {}.  {}'.\
                                format(i['type'], last_line, last_column, \
                                    message)
                        else:
                            SiteChecker._display_max_results_exceeded()
                            break
            except:
                utils.display_exception()
        print


class W3CssChecker(SiteChecker):
    """ Extend SiteChecker for W3 CSS Validation-specific processing.
    """

    def display_results(self, url_read_soup, url_to_check=None):
        """ Override SiteChecker.display_results() with W3 CSS
        Validation-specific HTTP response parsing.

        Print parsed W3 CSS Validation results

        :param url_read_soup: bs4.BeautifulSoup object created by requesting W3
            CSS Validation URL
        :param url_to_check: None (not needed here)
        """
        self._display_type_of_check_header()
        if url_read_soup is not None:
            soup_dict = {}
            try:
                soup_dict = json.loads(str(url_read_soup))
            except:
                utils.display_exception(opt_prepend='Unexpected response '\
                    'or invalid JSON response.')

            try:
                err_or_warning = False
                print
                for key, value in soup_dict['cssvalidation']['result'].items():
                    if value > 0:
                        err_or_warning = True
                    print '{}: {}'.format(key, value)
                print

                if err_or_warning:
                    err_cnt = 0
                    source = ''
                    message = ''
                    line = ''
                    last_source = ''
                    source = ''
                    for i in soup_dict['cssvalidation']['errors']:
                        err_cnt += 1
                        if err_cnt <= SiteChecker._MAX_RESULTS_TO_DISPLAY:
                            source = i['source']
                            if source != last_source:
                                if err_cnt != 1:
                                    print
                                print 'Source: {}'.format(source)

                            message = i['message']
                            if len(message) > SiteChecker._MAX_MSG_LENGTH:
                                message = '{} ...'.\
                                    format(message[:SiteChecker.\
                                        _MAX_MSG_LENGTH])

                            line = i['line'] if 'line' in i.keys() else ''
                            print '(error) Line {}.  {}'.format(line, message)
                            last_source = source
                        else:
                            SiteChecker._display_max_results_exceeded()
                            break
            except:
                utils.display_exception()
        print


