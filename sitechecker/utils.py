""" Provides various reusable utility functions.
"""
import sys

import linecache


def is_non_empty_str(p_obj):
    """ Determine if object passed in is a str with a length > 0.

    :param p_obj: An object to be evaluated
    """
    if str(type(p_obj)) == "<type 'str'>" and len(p_obj) > 0:
        return True
    else:
        return False


def display_exception(opt_prepend=None):
    """ Parse and print details about the exception that is currently being
    handled.

    :param opt_prepend: (Optional) A message to prepend before the exception
        details are printed.
    """
    # Following parsing logic adapted from
    # http://stackoverflow.com/questions/14519177/
    #   python-exception-handling-line-number?lq=1
    exc_type, exc_obj, exc_tb = sys.exc_info()
    tb_frame = exc_tb.tb_frame
    lineno = exc_tb.tb_lineno
    filename = tb_frame.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, tb_frame.f_globals)

    print
    if opt_prepend:
        print opt_prepend
        print
    if str(exc_type) == "<class 'requests.exceptions.ConnectionError'>":
        print 'Connection Error: {}'.format(exc_obj)
        print 'Please check your internet connection.'
    elif str(exc_type) == "<class 'requests.exceptions.HTTPError'>":
        print 'HTTP Error: {}'.format(exc_obj)
    else:
        print 'Error in {} line {}:\n{}{}\n{}{}: {}'.format(
            filename, lineno, ' ' * 4, line.strip(), ' ' * 8, exc_type,
            exc_obj)
    print
    exit_script()


def exit_script():
    """ Print an exit message and then perform a sys.exit
    """
    print 'Exiting script'
    print
    sys.exit()


