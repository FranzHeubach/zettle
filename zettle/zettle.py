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
        'zettle_named_directory_paths',
        'zettle_references_file_path',
    ]

    for setting in required_settings:
        if not settings.has(setting):
            raise ValueError('The "{}" setting is required.'.format(setting))

def get_zettle_named_directory_paths():
    """
    Gets the zettle named directory paths.

    This function also performs validation on the setting.

    :returns:   The zettle named directory paths.
    :rtype:     dict

    :raises     ValueError:  If the setting does not exist or is not valid.
    """
    zettle_named_directory_paths = settings.get('zettle_named_directory_paths')
    if not zettle_named_directory_paths:
        raise ValueError('Setting "zettle_named_directory_paths" is not currently set.')
    for name, path in zettle_named_directory_paths.items():
        if not os.path.isdir(path):
            raise ValueError('Path in setting "zettle_named_directory_paths": {}: {} is not a valid directory.'.format(name, path))
    return zettle_named_directory_paths

class cd:
    """
    Context manager for changing the current working directory
    """
    def __init__(self, new_path):
        self.new_path = os.path.expanduser(new_path)

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)

def generate_chronological_id():
    """
    Generates a chronological ID, unique to the minute.
    
    :returns:   The chronological ID,
    :rtype:     str
    """
    date = datetime.now()
    return '{:04}{:02}{:02}{:02}{:02}{:02}'.format(date.year, date.month, date.day, date.hour, date.minute, date.second)   

class NewZettleCommand(sublime_plugin.WindowCommand):
    """
    Create a new zettle command for the side bar context menu.
    
    This is a manual way of adding a zettle to any directory  you choose in the
    side bar by right clicking the folder.
    """
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

class OpenZettleCommand(sublime_plugin.WindowCommand):
    """
    Open a zettle in one of the existing zettlekasten.
    
    If there is only one zettlekasten it skips the first menu. If there are none
    it displays the user a error message and completes.
    """
    def run(self):
        self.named_paths = get_zettle_named_directory_paths()
        self.names = list()
        self.paths = list()

        for name, path in self.named_paths.items():
            self.names.append(name)
            self.paths.append(path)

        if len(self.paths) == 1:
            self.on_select_directory_done(0)
        else:
            self.window.show_quick_panel(self.names, self.on_select_directory_done)

    def on_select_directory_done(self, index):
        if index == -1:
            # Was cancelled.
            return
        
        directory = self.paths[index]
        with cd(directory):
            files = glob.glob("[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]*.md")
        
        if not files:
            sublime.error_message("{} contains no zettle.".format(self.names[index]))
            return

        abs_paths = [os.path.join(directory, file) for file in files]
        self.window.show_quick_panel(
            files, 
            functools.partial(self.on_select_file_done, abs_paths), 
            sublime.MONOSPACE_FONT | sublime.KEEP_OPEN_ON_FOCUS_LOST,
            0,
            functools.partial(self.on_select_file_highlighted, abs_paths)
        )

    def on_select_file_highlighted(self, abs_paths, index):
        abs_file_path = abs_paths[index]
        self.window.open_file(abs_file_path, sublime.TRANSIENT)

    def on_select_file_done(self, abs_paths, index):
        if index == -1:
            # Was cancelled.
            return
        abs_file_path = abs_paths[index]
        self.window.open_file(abs_file_path)

class NewZettleInZettlekastenCommand(sublime_plugin.WindowCommand):
    """
    A command to create and open a new zettle in one of the available
    zettlekasten.
    
    When there are more than one available zettlekasten the command will create
    a selector panel so you can choose which one. It will then auto populate the
    input panel with a chronological id with the markdown extension. After you
    have renamed to file to the filename of you choice it will create this file
    within the chosen zettlekasten and open it in the current window.
    """
    def run(self):
        date_str = generate_chronological_id()
        self.named_paths = get_zettle_named_directory_paths()
        self.names = list()
        self.paths = list()

        for name, path in self.named_paths.items():
            self.names.append(name)
            self.paths.append(path)

        if len(self.paths) == 1:
            self.window.show_input_panel("Zettle Name:", "{}.md".format(date_str), functools.partial(self.on_input_panel_done, self.paths[0]), None, None)
        else:
            self.window.show_quick_panel(self.names, functools.partial(self.on_quick_panel_done, date_str))
    
    def on_quick_panel_done(self, date_str, index):
        if index == -1:
            # was cancelled
            return
        selected_path = self.paths[index]            
        self.window.show_input_panel("Zettle Name:", "{}.md".format(date_str), functools.partial(self.on_input_panel_done, selected_path), None, None)

    def on_input_panel_done(self, directory, name):
        zettle = os.path.join(directory, name)
        open(zettle, 'a').close()
        self.window.open_file(zettle)

class ZettlePath(sublime_plugin.EventListener):
    """
    Provides autocompletion for links to other zettles in the same zettlekasten.
    
    It supports the [[]] syntax and the normal markdown link syntax [](). For
    the syntax that some zettlekasten software support the filename is inserted
    with no extension. For the normal markdown link syntax spaces will be
    escaped to their valid escape code %20 and the file extension will be kept.
    """
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

        paths = get_zettle_named_directory_paths()

        file_name = view.file_name()
        parent_directory = os.path.dirname(file_name)
        if parent_directory not in paths.values():
            # The file we are editing is not in a zettlekasten directory
            return

        with cd(parent_directory):
            paths = glob.glob("[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]*.md")
            if identifier == '[[':
                completions = [(path, path[:-3]) for path in paths]
            else:
                completions = [(path, '{}'.format(path.replace(' ', r'%20'))) for path in paths]
            return completions

class CitationComplete(sublime_plugin.EventListener):
    """
    Provides auto-completion for reference IDs.
    
    Auto-completion is triggered on [@] syntax. The auto-completion uses the references file in CSL JSON format. Just type
    in a fuzzy search for the author and title, it will show this in the
    auto-complete selector. Once selected the corresponding ID will be inserted.
    This works well with Zettlr, which has support for rendering the references
    by ID. 
    """
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