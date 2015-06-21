#!/usr/bin/env python
"""
------------
SITE CHECKER
------------
Input:
 - A URL to check OR a path to file containing 1 or more URLs to check
Output (per URL):
 - WOT SCORECARD
 - SUCURI SECURITY SITE CHECK
 - GOOGLE PAGESPEED INSIGHTS
 - W3 MARKUP VALIDATION
 - W3 CSS3 VALIDATION

optional arguments:
  -h,      --help       show this help message and exit
  -s site, --site site  Url of site to check.  Example: www.google.com
  -f file, --file file  Absolute path to file containing 1 or more urls to
                        check. (URLs in file should be 1 per line in format
                        www.google.com)
"""


import argparse
import time

from sitechecker import checker, utils


SECONDS_TO_SLEEP = 3

INPUT_TYPE_URL = 'URL'
INPUT_TYPE_PATH = 'PATH'


CHECKER_DICT = {
    1: [checker.WotChecker, 'WOT SCORECARD',
        'https://www.mywot.com/en/scorecard/', 'GET'],
    2: [checker.SucuriChecker, 'SUCURI SECURITY SITE CHECK',
        'https://sitecheck.sucuri.net/results/', 'POST'],
    3: [checker.GoogleChecker, 'GOOGLE PAGESPEED INSIGHTS',
        'https://www.googleapis.com/pagespeedonline/v1/runPagespeed?url='\
        'http://', 'GET'],
    4: [checker.W3MarkupChecker, 'W3 MARKUP VALIDATION',
        'http://validator.w3.org/check?output=json&uri=http%3A%2F%2F', 'GET'],
    5: [checker.W3CssChecker, 'W3 CSS3 VALIDATION',
        'http://jigsaw.w3.org/css-validator/validator?output=json&uri=', 'GET']
}


def main():
    """ Perform main script tasks:
    - Parse arguments to script.
    - Process user command line input (either a URL or a file containing URLs).
    - If user input was a path to a file, extract URLs from the file.
    - For every URL, perform each check for the URL (example: Google PageSpeed
      Insights, Sucuri SiteChecker, etc).
    """
    (user_input, input_type) = __parse_script_args()
    urls_to_check = []

    if input_type == INPUT_TYPE_URL:
        urls_to_check.append(user_input)
    elif input_type == INPUT_TYPE_PATH:
        urls_to_check = __get_urls_from_file(user_input)

    url_item_cnt = 0
    temp_checker = None

    for url_item in urls_to_check:
        url_item_cnt += 1

        if not checker.SiteChecker.is_valid_url(url_item):
            utils.exit_script()

        __display_url_header(url_item)

        if url_item_cnt != 1:
            # Don't beat up the kindly web sites that provide you with data
            time.sleep(SECONDS_TO_SLEEP)

        for i in CHECKER_DICT.keys():
            # Instatiate the appropriate checker.SiteChecker child class
            # with attributes
            temp_checker = CHECKER_DICT[i][0](CHECKER_DICT[i][1],\
                CHECKER_DICT[i][2], CHECKER_DICT[i][3])
            # Invoke the process_url function for that child class
            temp_checker.process_url(url_item)


def __parse_script_args():
    """ Parse command-line arguments to this script
    """
    arg_desc = '------------\n' \
        'SITE CHECKER\n' \
        '------------\n' \
        'Input:\n' \
        ' - A URL to check OR a path to file containing 1 or more URLs to '\
            'check\n' \
        'Output (per URL):\n'

    for i in CHECKER_DICT.keys():
        arg_desc += ' - ' + CHECKER_DICT[i][1] + '\n'

    parser = argparse.ArgumentParser(description=arg_desc,\
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-s', '--site', metavar='site', type=str,\
        help='Url of site to check.  Example: www.google.com')
    parser.add_argument('-f', '--file', metavar='file',\
        type=argparse.FileType('r'),\
        help='Absolute path to file containing 1 or more urls to\n'\
            'check.  (URLs in file should be 1 per line in format\n'\
            'www.google.com)')
    args = parser.parse_args()
    if not (args.site or args.file):
        parser.error('Please provide --site or --file as argument')
        # Not reachable, so no return
    elif args.site and args.file:
        parser.error('Please provide either --site or --file as argument '\
            '(only one)')
        # Not reachable, so no return
    else:
        return (args.site, INPUT_TYPE_URL) if args.site else (args.file,\
            INPUT_TYPE_PATH)


def __get_urls_from_file(user_input):
    """ Parse individual URLs listed in file into a list and return the list.
    """
    urls_to_check = []
    temp_line = ''
    try:
        # Input already validated as valid file by args parser
        with user_input as url_file:
            for line in url_file:
                temp_line = line.strip('\n').strip(' ')
                if utils.is_non_empty_str(temp_line):
                    urls_to_check.append(temp_line)
        return urls_to_check
    except:
        utils.display_exception()
        # Not reachable, so no return


def __display_url_header(url_to_check):
    """ Print the formatted URL from user input.
    """
    if utils.is_non_empty_str(url_to_check):
        print
        print url_to_check
        print len(url_to_check) * '_'


if __name__ == "__main__":
    main()
else:
    pass

