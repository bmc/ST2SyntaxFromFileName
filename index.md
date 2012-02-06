---
title: Sublime Text 2 Syntax From File Name Plugin
layout: withTOC
---

## Introduction

The [ST2SyntaxFromFileName][] plugin provides a means to map a Sublime Text 2
buffer to a syntax (for highlighting, completion and snippets), by matching
against the buffer's file name.

[GNU Emacs]: http://www.gnu.org/s/emacs/
[Sublime Text 2]: http://www.sublimetext.com/2
[ST2SyntaxFromFileName]: https://github.com/bmc/ST2SyntaxFromFileName

## Warning

I use this plug-in myself, but *caveat user*. If you use it, and they screw
you all to hell, it's not my fault.

## Installation

There are several ways to install these plugins.

### Via Package Control

If you're using Will Bond's [Package Control][] (and you should be),
installation is straightfoward.

Pull up the *Preferences > Package Control* menu, select *Package Control:
Install Package*, and search for "Syntax From File".  Install the package from
there, and Package Control takes care of the rest.

#### Upgrading

To upgrade the package, just use the Package Control package upgrade 
capability.

[Package Control]: http://wbond.net/sublime_packages/package_control

### Manually


Go to your Sublime Text 2 `Packages` directory and clone the repository.
For instance, on Linux:

    $ cd ~/.config/sublime-text-2/Packages
    $ git clone https://github.com/bmc/ST2SyntaxFromFileName

On Mac OS X:

    $ cd "$HOME/Library/Application Support/Sublime Text 2/Packages"
    $ git clone https://github.com/bmc/ST2SyntaxFromFileName

To upgrade, just do a `git pull` within that directory.

## Plugin Documentation

The plugin is configured the "filename_syntax_settings" value in your user
settings. That value is an array of arrays, with each inner array element
defining a mapping from a regular expression to a syntax name. For instance,
here's a portion of my settings file:


    {

      "filename_syntax_settings":
      [
        ["\\.scss", "Ruby Sass", "i"],
        ["\\.sass", "Ruby Sass", "i"]
      ],

That setting maps files ending in ".scss" and ".sass" to the "Ruby Sass" syntax
value.

Each entry has two or two fields. The first two are mandatory. They are:

1. A regular expression pattern against which to match the filename.
   Note that backslashes must be double-escaped, because of the way the JSON
   parser works. **REQUIRED**
2. The syntax value to apply to matching files. The name must match the name
   of a `.tmLanguage` file somewhere underneath your Sublime Text 2 `Packages`
   directory. The name is matched in a case-blind manner; thus, "Scala" and
   "scala" mean the same thing. **REQUIRED**
3. Optional flags for the regular expression parser. Currently, only "i",
   for case-blind comparison, is honored. Anything else is ignored.
   **OPTIONAL**

The settings examined applied _in order_, and the first match wins.

If the plugin fails to honor your syntax setting, see the Python console
(normally accessible via *Ctrl-\`*). There may be a warning that's helpful.

**Notes**

1. This plugin isn't a command; it's an event listener. Installing these
   plugins automatically enables the Syntax Setter capability.
2. This plugin's syntax settings will override any settings created by
   Sublime Text 2. However, it will _not_ override any buffer-specific syntax 
   value set by my [Emacs-like Syntax Setter][] plugin.

[Emacs-like Syntax Setter]: http://software.clapper.org/ST2EmacsMiscellanea

## Author

Brian M. Clapper, [bmc@clapper.org][]

## Copyright and License

This software is copyright &copy; 2012 Brian M. Clapper
and is released under a [BSD License][].

## Patches

I gladly accept patches from their original authors. Feel free to email
patches to me or to fork the [GitHub repository][] and send me a pull
request. Along with any patch you send:

* Please state that the patch is your original work.
* Please indicate that you license the work to the PROJECT project
  under a [BSD License][].

[BSD License]: license.html
[GitHub repository]: http://github.com/bmc/sublime-text-hacks
[GitHub]: http://github.com/bmc/
[downloads area]: http://github.com/bmc/sublime-text-hacks/downloads
[bmc@clapper.org]: mailto:bmc@clapper.org
