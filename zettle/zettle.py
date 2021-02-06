import sublime
import sublime_plugin
import glob
import os
from datetime import datetime
import functools
import json
import re

global settings

def plugin_loaded():
    global settings
    FILENAME = 'Zettle.sublime-settings'
    settings = sublime.load_settings(FILENAME)

    required_settings = [
        'zettle_directory_path',
        'zettle_references_file_path',
    ]

    for setting in required_settings:
        if not settings.has(setting):
            raise ValueError('The "{}" setting is required.'.format(setting))

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, new_path):
        self.new_path = os.path.expanduser(new_path)

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)

def generate_chronological_id():
    date = datetime.now()
    return '{:04}{:02}{:02}{:02}{:02}{:02}'.format(date.year, date.month, date.day, date.hour, date.minute, date.second)   

class NewZettleCommand(sublime_plugin.WindowCommand):
    def run(self, dirs):
        date_str = generate_chronological_id()
        self.window.show_input_panel("Zettle Name:", "{}.md".format(date_str), functools.partial(self.on_done, dirs[0]), None, None)
    
    def on_done(self, dir, name):
        zettle = os.path.join(dir, name)
        open(zettle, 'a').close()
        self.window.open_file(zettle)

    def is_visible(self, dirs):
        if len(dirs) == 1:
            return True
        else:
            return False

class NewZettleInZettlekastenCommand(sublime_plugin.WindowCommand):
    def run(self):
        date_str = generate_chronological_id()
        self.window.show_input_panel("Zettle Name:", "{}.md".format(date_str), self.on_done, None, None)

    def on_done(self, name):
        try:
            self.zettle_directory_path
        except AttributeError:
            self.zettle_directory_path = settings.get('zettle_directory_path')
            if not self.zettle_directory_path:
                raise ValueError('Setting "zettle_directory_path" is not currently set.')
            if not os.path.isdir(self.zettle_directory_path):
                raise ValueError('Setting "zettle_directory_path": {} is not a valid directory.'.format(self.zettle_directory_path))

        zettle = os.path.join(self.zettle_directory_path, name)
        open(zettle, 'a').close()
        self.window.open_file(zettle)

class ZettlePath(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, points):
        point = points[0]
        if not view.score_selector(point, "text.html.markdown"):
            return

        # Check for [[ or ]( to start reference
        point_before_prefix = point - len(prefix)
        region = sublime.Region(point_before_prefix-2, point_before_prefix)
        identifier = view.substr(region)
        if identifier != r'[[' and identifier != r'](':
            return

        try:
            self.zettle_directory_path
        except AttributeError:
            self.zettle_directory_path = settings.get('zettle_directory_path')
            if not self.zettle_directory_path:
                raise ValueError('Setting "zettle_directory_path" is not currently set.')
            if not os.path.isdir(self.zettle_directory_path):
                raise ValueError('Setting "zettle_directory_path": {} is not a valid directory.'.format(self.zettle_directory_path))
        
        file_name = view.file_name()
        parent_directory = os.path.dirname(file_name)
        if parent_directory != self.zettle_directory_path:
            return

        with cd(self.zettle_directory_path):
            paths = glob.glob("[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]*.md")
            if identifier == '[[':
                completions = [(path, path[:-3]) for path in paths]
            else:
                completions = [(path, '{}'.format(path.replace(' ', r'%20'))) for path in paths]
            return completions

class CitationComplete(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, points):
        point = points[0]
        if not view.score_selector(point, "text.html.markdown"):
            return

        # Check for [@ to start reference
        point_before_prefix = point - len(prefix)
        region = sublime.Region(point_before_prefix-2, point_before_prefix)
        identifier = view.substr(region)
        if identifier != r'[@':
            return 

        try:
            self.reference_path
        except AttributeError:
            self.reference_path = settings.get('zettle_references_file_path')
            if not self.reference_path:
                raise ValueError('Setting "zettle_references_file_path" is not currently set.')

        try:
            self.references
        except AttributeError:
            with open(self.reference_path, 'r') as file:
                csl_json = json.load(file)
            self.references = list()
            for entry in csl_json:
                try:
                    first_author_last_name = entry['author'][0]['family']
                    self.references.append(('{}, {}'.format(first_author_last_name, entry['title']), entry['id']))
                except (KeyError, IndexError):
                    self.references.append((entry['title'], entry['id']))
        return self.references