
import traceback

def _format_message(prefix, msg_fmt, *args):
    msg = msg_fmt
    if len(args) > 0:
        msg = msg_fmt.format(*args)
    first = False
    lines = msg.split('\n')
    print('{}: {}'.format(prefix, lines[0]))
    for line in lines[1:]:
        print('{}  {}'.format(' ' * len(prefix), line))

def trace(start, end):
    tb = traceback.extract_stack()
    for file_name, line, _module, statement in tb[start:end]:
        print('{}:{}  {}'.format(file_name, line, statement))


def error(msg_fmt, *args):
    '''Issue a message and terminate the program.
    '''
    _format_message('ERROR', msg_fmt, *args)
    exit(1)


def warning(msg_fmt, *args):
    '''Issue a warning message, and continue on with life.'''
    _format_message('WARNING', msg_fmt, *args)


def info(msg_fmt, *args):
    '''Issue a warning message, and continue on with life.'''
    _format_message('INFO', msg_fmt, *args)


def internal_error(msg_fmt, *args):
    '''Issue a message caused by a programming error, and terminate the program.'''
    _format_message('INTERNAL ERROR', msg_fmt, *args)
    _format_message('INTERNAL ERROR', 'The above message resulted from an internal programming error\n'
            'If this was caused by something you did, keep at it!\n'
            'If this was caused by simply using build-system, please create a ticket in github.')
    exit(1)

