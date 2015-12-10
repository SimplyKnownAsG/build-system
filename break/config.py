
import os
import argparse

import yaml

items = []
_by_name = {}

CONFIG_NAME = '.break.yaml'

def save():
    config_as_dict = { item.name : item.value for item in items if item.non_default }
    with open(CONFIG_NAME, 'w') as config_file:
        config_file.write('# BREAK generated configuration file\n')
        config_file.write('# feel free to update values here, it could be fun!\n')
        config_file.write('# if things break, then you are doing great!\n')
        config_file.write(yaml.dump(config_as_dict, default_flow_style=False))

def load():
    if os.path.exists(CONFIG_NAME):
        conf = {}
        with open(CONFIG_NAME, 'r') as config_file:
            conf = yaml.load(config_file)
        for kk, vv in conf.items():
            _by_name[kk].value = vv


class ConfigItemAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        global _by_name
        setattr(namespace, self.dest, values)
        _by_name[option_string].value = values


def add_command_line_args(parser):
    global items
    for item in items:
        parser.add_argument(item.name,
                action=ConfigItemAction,
                help=item.description,
                default=item.default_value)


def print_config():
    global items
    item_width = max(len(item.name) for item in items)
    fmt = '{{:<{}}}  {{}}'.format(item_width)
    for item in items:
        print fmt.format(item.name, item)


class ConfigItem(object):
    
    def __init__(self, name, default_value, description):
        self.name = name
        self.default_value = default_value
        self.description = description
        self._value = None
        global items, _by_name
        items.append(self)
        _by_name[self.name] = self

    @property
    def value(self):
        return self._value if self._value != None else self.default_value

    @value.setter
    def value(self, val):
        self._value = val

    @property
    def non_default(self):
        return self._value is not None

    def __str__(self):
        return self.value

    def __repr__(self):
        return '<ConfigItem {}={}>'.format(self.name, self.value)


