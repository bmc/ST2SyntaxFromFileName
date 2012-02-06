import sublime, sublime_plugin
import re
import os
import json

class SyntaxFromFileName(sublime_plugin.EventListener):
    '''
    SyntaxFromFileFile sets a buffer's syntax from its file name, based on
    configured set of regular expressions. See
    http://software.clapper.org/ST2SyntaxFromFileName/ for details.
    '''
    def __init__(self):
        self._syntaxes = self._load_syntaxes()

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

    def _check_syntax(self, view):
        '''
        Does the actual work of checking the syntax setting and changing it,
        if necessary.
        '''
        filename = view.file_name()
        syntax = None
        settings = view.settings().get('filename_syntax_settings', None)
        if (filename is None) or (settings is None):
            return

        for i in range(0, len(settings)):
            setting = settings[i]
            s_setting = ', '.join(setting)
            if not len(setting) in [2, 3]:
                self._error("Wrong field count in: [%s]" % s_setting)
                continue

            pattern = setting[0]
            syntax_name = setting[1].strip().lower()

            error = False

            syntax_file = self._syntaxes.get(syntax_name)
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
                if regex.search(filename):
                    syntax = syntax_file
                    if view.settings().get('syntax') != syntax:
                        # Honor 'sticky-syntax'. The EmacsLikeSyntaxSetter
                        # plugin (mine) uses this setting to indicate a buffer-
                        # specific syntax override. That override should have
                        # higher priority than this value.
                        name = view.name()
                        if name is None or name.strip() == '':
                            name = os.path.basename(view.file_name())
                        if view.settings().get('sticky-syntax', False):
                            self._message('Syntax for %s is sticky.' % name)
                        else:
                            self._message('Syntax "%s" for %s' % (syntax, name))
                            view.set_syntax_file(syntax)
                            view.settings().set('sticky-syntax', False)

            except Exception as ex:
                self.error(
                    "Bad file pattern '%s' in [%s]" % (syntax_name, s_setting)
                )
                error = True

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

    def _error(self, msg):
        self._message("(ERROR) %s" % msg)

    def _message(self, msg):
        print("SyntaxFromFileName: %s" % msg)