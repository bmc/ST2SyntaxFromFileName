import sublime, sublime_plugin
import re
import os
import json

PREF_FILE_NAME = 'SyntaxFromFile.sublime-settings'
PACKAGE_NAME   = 'SyntaxFromFile'

class SettingFileInfo(object):
    def __init__(self, path):
        self.path = path
        self._mtime = self._get_mtime(path)

    def changed(self):
        new_mtime = self._get_mtime(self.path)
        return new_mtime != self._mtime

    def _get_mtime(self, path):
        return os.stat(path).st_mtime if os.path.exists(path) else 0

class SyntaxFromFile(sublime_plugin.EventListener):
    '''
    SyntaxFromFile sets a buffer's syntax from its file name, based on
    configured set of regular expressions.
    '''
    def __init__(self):
        self._syntaxes = self._load_syntaxes()

        # Load the preferences files into an array of [regex, syntaxname] pairs.
        self.reload_settings()

    def on_load(self, view):
        '''
        Called when a view is first loaded. Check the syntax setting then.
        '''
        self._check_syntax(view)

    def on_post_save(self, view):
        '''
        Called right after a save. Check the syntax then, in case it changed.
        '''
        self._check_syntax(view)

        filename = view.file_name()
        if filename is not None:
            if os.path.basename(filename) == PREF_FILE_NAME:
                # A preference file changed. Recheck.
                self._recheck_settings()

    def reload_settings(self):
        self._settings, self._settings_files = self._load_settings(self._syntaxes)

    def _recheck_settings(self):
        for i in range(0, len(self._settings_files)):
            fi = self._settings_files[i]
            if fi.changed():
                self._message("%s changed. Reloading settings." % fi.path)
                self.reload_settings()
                break

    def _check_syntax(self, view):
        '''
        Does the actual work of checking the syntax setting and changing it,
        if necessary.
        '''
        filename = view.file_name()
        syntax = None
        if filename is not None:
            # Scan the settings for a match. First one wins. The settings
            # are [regex, syntax] tuples.
            for i in range(0, len(self._settings)):
                setting = self._settings[i]
                if setting[0].search(filename):
                    syntax = setting[1]
                    break

        if syntax is not None:
            if view.settings().get('syntax') != syntax:
                self._message(
                    "Syntax %s for %s" % (syntax, os.path.basename(filename))
                )
                view.set_syntax_file(syntax)

    def _load_syntaxes(self):
        syntaxes = {}

        # Construct a regular expression that will take a full path and
        # extract everything from "Packages/" to the end. This expression
        # will be use to map paths like /path/to/Packages/C/C.tmLanguage
        # to just Packages/C/C.tmLanguage, which is what Sublime wants
        # as a syntax setting.
        sep = r'\\' if os.sep == "\\" else os.sep
        package_pattern = '^.*%s(Packages%s.*)$' % (sep, sep)
        package_re = re.compile(package_pattern)  

        # Recursively walk the Sublime Packages directory, looking for
        # '.tmLanguage' files. Convert each one to a short language name
        # (used as a dictionary key) and the full name that Sublime wants.
        for root, dirs, files in os.walk(sublime.packages_path()):
            # Filter out files that don't end in .tmLanguage
            lang_files = [f for f in files if f.endswith('.tmLanguage')]

            # Map to a full path...
            full_paths = [os.path.join(root, l) for l in lang_files]

            # ... and strip off everything prior to "Packages"
            for p in full_paths:
                # Store the short name.
                short_syntax_name = os.path.splitext(os.path.basename(p))[0]

                # The Sublime name is as described above.
                sublime_syntax_name = package_re.search(p).group(1)

                # Store in the hash.
                syntaxes[short_syntax_name.lower()] = sublime_syntax_name

        return syntaxes

    def _load_settings(self, syntaxes):
        package_path = sublime.packages_path()
        settings = []
        files = []
        for subdir in ['User', PACKAGE_NAME]:
            f = os.path.join(package_path, subdir, PREF_FILE_NAME)
            files.append(SettingFileInfo(f))
            if os.path.exists(f):
                try:
                    lines = [i for i in open(f).readlines
                               if not i.strip().startswith("//")]
                    settings = json.load(''.join(lines))
                    settings.append(self._process_settings(settings))
                except Exception as ex:
                    self._error("Failed to load %s: %s" % (f, ex))

        # Flatten the result.
        return ([i for sublist in settings for i in sublist], files)

    def _process_settings(self, settings, syntaxes):
        # The JSON file is a series of arrays. Each array has 2 or 3 elements,
        # consisting of:
        #
        # 1 - a regular expression pattern to match the file name
        # 2 - a short syntax name
        # 3 - optional regex flags. Supported: 'i'
        result = []
        for i in range(0, len(settings)):
            setting = settings[i]
            s_setting = ', '.join(setting)
            if not len(setting) in [2, 3]:
                self._error("Wrong field count in: [%s]" % s_setting)
                continue

            pattern = setting[0]
            syntax_name = setting[1].strip().lower()

            error = False

            syntax_file = syntaxes.get(syntax_name)
            if syntax_file is None:
                self._error(
                    "Unknown syntax '%s' in [%s]" % (syntax_name, s_setting)
                )
                error = True

            opts = 0
            if len(setting) == 3:
                if setting[2].find('i') != -1:
                    opts |= re.IGNORECASE

            try:
                regex = re.compile(pattern, opts)
            except Exception as ex:
                self.error(
                    "Bad file pattern '%s' in [%s]" % (syntax_name, s_setting)
                )
                error = True

            if not error:
                result.append([regex, syntax_file])

        return result

    def _error(self, msg):
        self._message("(ERROR) %s" % msg)

    def _message(self, msg):
        print("SyntaxFromFile: %s" % msg)