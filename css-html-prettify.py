#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""CSS-HTML-Prettify.

StandAlone Async single-file cross-platform no-dependencies
Unicode-ready Python3-ready Prettifier Beautifier for the Web.
"""


import functools
import itertools
import logging as log
import os
import re
import socket
import sys
from argparse import ArgumentParser
from copy import copy
from ctypes import byref, cdll, create_string_buffer
from datetime import datetime
from getpass import getuser
from multiprocessing import Pool, cpu_count
from platform import platform, python_version
from tempfile import gettempdir
from time import sleep

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("BeautifulSoup4 Not Found!, use:  sudo apt-get install python3-bs4")

try:
    from urllib import request
    from subprocess import getoutput
    import resource  # windows dont have resource
except ImportError:
    request = getoutput = resource = None


__version__ = "1.0.0"
__license__ = "GPLv3+ LGPLv3+"
__author__ = "Juan Carlos"
__email__ = "juancarlospaco@gmail.com"
__url__ = "https://github.com/juancarlospaco/css-html-prettify"
__source__ = ("https://raw.githubusercontent.com/juancarlospaco/"
              "css-html-prettify/master/css-html-prettify.py")


start_time = datetime.now()
CSS_PROPS_TEXT = '''

alignment-adjust alignment-baseline animation animation-delay
animation-direction animation-duration animation-iteration-count
animation-name animation-play-state animation-timing-function appearance
azimuth

backface-visibility background background-attachment background-clip
background-color background-image background-origin background-position
background-repeat background-size baseline-shift bikeshedding bookmark-label
bookmark-level bookmark-state bookmark-target border border-bottom
border-bottom-color border-bottom-left-radius border-bottom-right-radius
border-bottom-style border-bottom-width border-collapse border-color
border-image border-image-outset border-image-repeat border-image-slice
border-image-source border-image-width border-left border-left-color
border-left-style border-left-width border-radius border-right
border-right-color border-right-style border-right-width border-spacing
border-style border-top border-top-color border-top-left-radius
border-top-right-radius border-top-style border-top-width border-width bottom
box-decoration-break box-shadow box-sizing

caption-side clear clip color column-count column-fill column-gap column-rule
column-rule-color column-rule-style column-rule-width column-span column-width
columns content counter-increment counter-reset cue cue-after cue-before
cursor

direction display drop-initial-after-adjust drop-initial-after-align
drop-initial-before-adjust drop-initial-before-align drop-initial-size
drop-initial-value

elevation empty-cells

fit fit-position float font font-family font-size font-size-adjust
font-stretch font-style font-variant font-weight

grid-columns grid-rows

hanging-punctuation height hyphenate-character hyphenate-resource hyphens

icon image-orientation image-resolution inline-box-align

left letter-spacing line-height line-stacking line-stacking-ruby
line-stacking-shift line-stacking-strategy linear-gradient list-style
list-style-image list-style-position list-style-type

margin margin-bottom margin-left margin-right margin-top marquee-direction
marquee-loop marquee-speed marquee-style max-height max-width min-height
min-width

nav-index

opacity orphans outline outline-color outline-offset outline-style
outline-width overflow overflow-style overflow-x overflow-y

padding padding-bottom padding-left padding-right padding-top page
page-break-after page-break-before page-break-inside pause pause-after
pause-before perspective perspective-origin pitch pitch-range play-during
position presentation-level

quotes

resize rest rest-after rest-before richness right rotation rotation-point
ruby-align ruby-overhang ruby-position ruby-span

size speak speak-header speak-numeral speak-punctuation speech-rate src
stress string-set

table-layout target target-name target-new target-position text-align
text-align-last text-decoration text-emphasis text-indent text-justify
text-outline text-shadow text-transform text-wrap top transform
transform-origin transition transition-delay transition-duration
transition-property transition-timing-function

unicode-bidi unicode-range

vertical-align visibility voice-balance voice-duration voice-family
voice-pitch voice-range voice-rate voice-stress voice-volume volume

white-space widows width word-break word-spacing word-wrap

z-index

'''


###############################################################################


def typecheck(f):
    """Decorator for Python3 annotations to type-check inputs and outputs."""
    def __check_annotations(tipe):
        _type, is_ok = None, isinstance(tipe, (type, tuple, type(None)))
        if is_ok:  # Annotations can be Type or Tuple or None
            _type = tipe if isinstance(tipe, tuple) else tuple((tipe, ))
            if None in _type:  # if None on tuple replace with type(None)
                _type = tuple([_ if _ is not None else type(_) for _ in _type])
        return _type, is_ok

    @functools.wraps(f)  # wrap a function or method to Type Check it.
    def decorated(*args, **kwargs):
        msg = "Type check error: {0} must be {1} but is {2} on function {3}()."
        notations, f_name = tuple(f.__annotations__.keys()), f.__code__.co_name
        for i, name in enumerate(f.__code__.co_varnames):
            if name not in notations:
                continue  # this arg name has no annotation then skip it.
            _type, is_ok = __check_annotations(f.__annotations__.get(name))
            if is_ok:  # Force to tuple
                if i < len(args) and not isinstance(args[i], _type):
                    log.critical(msg.format(repr(args[i])[:50], _type,
                                            type(args[i]), f_name))
                elif name in kwargs and not isinstance(kwargs[name], _type):
                    log.critical(msg.format(repr(kwargs[name])[:50], _type,
                                            type(kwargs[name]), f_name))
        out = f(*args, **kwargs)
        _type, is_ok = __check_annotations(f.__annotations__.get("return"))
        if is_ok and not isinstance(out, _type) and "return" in notations:
            log.critical(msg.format(repr(out)[:50], _type, type(out), f_name))
        return out    # The output result of function or method.
    return decorated  # The decorated function or method.


###############################################################################
# CSS prettify


@typecheck
def _compile_props(props_text: str, grouped: bool=False) -> tuple:
    """Take a list of props and prepare them."""
    props = []
    for line_of_props in props_text.strip().lower().splitlines():
        props += line_of_props.split(" ")
    props = filter(lambda line: not line.startswith('#'), props)
    if not grouped:
        props = list(filter(None, props))
        return props, [0]*len(props)
    final_props, groups, g_id = [], [], 0
    for prop in props:
        if prop.strip():
            final_props.append(prop)
            groups.append(g_id)
        else:
            g_id += 1
    return (final_props, groups)


@typecheck
def _prioritify(line_of_css: str, css_props_text_as_list: tuple) -> tuple:
    """Return args priority, priority is integer and smaller means higher."""
    sorted_css_properties, groups_by_alphabetic_order = css_props_text_as_list
    priority_integer, group_integer = 9999, 0
    for css_property in sorted_css_properties:
        if css_property.lower() == line_of_css.split(":")[0].lower().strip():
            priority_integer = sorted_css_properties.index(css_property)
            group_integer = groups_by_alphabetic_order[priority_integer]
            log.debug("Line of CSS: '{0}', Priority for Sorting: #{1}.".format(
                line_of_css[:80].strip(), priority_integer))
            break
    return (priority_integer, group_integer)


def _props_grouper(props, pgs):
    """Return groups for properties."""
    log.debug("Grouping all CSS / SCSS Properties.")
    if not props:
        return props
    #props = sorted([
        #_ if _.strip().endswith(";") and
        #not _.strip().endswith("*/") and not _.strip().endswith("/*")
        #else _.rstrip() + ";\n" for _ in props])
    props_pg = zip(map(lambda prop: _prioritify(prop, pgs), props), props)
    props_pg = sorted(props_pg, key=lambda item: item[0][1])
    props_by_groups = map(
        lambda item: list(item[1]),
        itertools.groupby(props_pg, key=lambda item: item[0][1]))
    props_by_groups = map(lambda item: sorted(
        item, key=lambda item: item[0][0]), props_by_groups)
    props = []
    for group in props_by_groups:
        group = map(lambda item: item[1], group)
        props += group
        props += ['\n']
    props.pop()
    return props


@typecheck
def sort_properties(css_unsorted_string: str) -> str:
    """CSS Property Sorter Function.

    This function will read buffer argument, split it to a list by lines,
    sort it by defined rule, and return sorted buffer if it's CSS property.
    This function depends on '_prioritify' function.
    """
    log.debug("Alphabetically Sorting all CSS / SCSS Properties.")
    css_pgs = _compile_props(CSS_PROPS_TEXT, grouped=bool(args.group))
    pattern = re.compile(r'(.*?{\r?\n?)(.*?)(}.*?)|(.*)',
                         re.DOTALL + re.MULTILINE)
    matched_patterns = pattern.findall(css_unsorted_string)
    sorted_patterns, sorted_buffer = [], css_unsorted_string
    RE_prop = re.compile(r'((?:.*?)(?:;)(?:.*?\n)|(?:.*))',
                         re.DOTALL + re.MULTILINE)
    if len(matched_patterns) != 0:
        for matched_groups in matched_patterns:
            sorted_patterns += matched_groups[0].splitlines(True)
            props = map(lambda line: line.lstrip('\n'),
                        RE_prop.findall(matched_groups[1]))
            props = list(filter(lambda line: line.strip('\n '), props))
            props = _props_grouper(props, css_pgs)
            sorted_patterns += props
            sorted_patterns += matched_groups[2].splitlines(True)
            sorted_patterns += matched_groups[3].splitlines(True)
        sorted_buffer = ''.join(sorted_patterns)
    return sorted_buffer


@typecheck
def remove_empty_rules(css: str) -> str:
    """Remove empty rules."""
    log.debug("Removing all unnecessary empty rules.")
    return re.sub(r"[^\}\{]+\{\}", "", css)


@typecheck
def condense_zero_units(css: str) -> str:
    """Replace `0(px, em, %, etc)` with `0`."""
    log.debug("Condensing all zeroes on values.")
    return re.sub(r"([\s:])(0)(px|em|rem|%|in|cm|mm|pc|pt|ex)", r"\1\2", css)


@typecheck
def condense_semicolons(css: str) -> str:
    """Condense multiple adjacent semicolon characters into one."""
    log.debug("Condensing all unnecessary multiple adjacent semicolons.")
    return re.sub(r";;+", ";", css)


@typecheck
def wrap_css_lines(css: str, line_length: int=80) -> str:
    """Wrap the lines of the given CSS to an approximate length."""
    log.debug("Wrapping lines to ~{} max line lenght.".format(line_length))
    lines, line_start = [], 0
    for i, char in enumerate(css):
        # Its safe to break after } characters.
        if char == '}' and (i - line_start >= line_length):
            lines.append(css[line_start:i + 1])
            line_start = i + 1
    if line_start < len(css):
        lines.append(css[line_start:])
    return "\n".join(lines)


@typecheck
def add_encoding(css: str) -> str:
    """Add @charset 'UTF-8'; if missing."""
    log.debug("Adding encoding declaration if needed.")
    return "@charset utf-8;\n\n\n" + css if "@charset" not in css else css


@typecheck
def normalize_whitespace(css: str) -> str:
    """Normalize css string white spaces."""
    log.debug("Starting to Normalize white spaces on CSS if needed.")
    css_no_trailing_whitespace = ""
    for line_of_css in css.splitlines():  # remove all trailing white spaces
        css_no_trailing_whitespace += line_of_css.rstrip() + "\n"
    css = css_no_trailing_whitespace
    css = re.sub(r"\n{3}", "\n\n\n", css)  # if 3 new lines,make them 2
    css = re.sub(r"\n{5}", "\n\n\n\n\n", css)  # if 5 new lines, make them 4
    h_line = "/* {} */".format("-" * 72)  # if >6 new lines, horizontal line
    css = re.sub(r"\n{6,}", "\n\n\n{}\n\n\n".format(h_line), css)
    css = css.replace(" ;\n", ";\n").replace("{\n", " {\n")
    css = re.sub("\s{2,}{\n", " {\n", css)
    log.debug("Finished Normalize white spaces on CSS.")
    return css.replace("\t", "    ").rstrip() + "\n"


@typecheck
def justify_right(css: str) -> str:
    """Justify to the Right all CSS properties on the argument css string."""
    log.debug("Starting Justify to the Right all CSS / SCSS Property values.")
    max_indent, right_justified_css = 1, ""
    for css_line in css.splitlines():
        c_1 = len(css_line.split(":")) == 2 and css_line.strip().endswith(";")
        c_2 = "{" not in css_line and "}" not in css_line and len(css_line)
        c_4 = not css_line.lstrip().lower().startswith("@import ")
        if c_1 and c_2 and c_4:
            lenght = len(css_line.split(":")[0].rstrip()) + 1
            max_indent = lenght if lenght > max_indent else max_indent
    for line_of_css in css.splitlines():
        c_1 = "{" not in line_of_css and "}" not in line_of_css
        c_2 = max_indent > 1 and len(line_of_css.split(":")) == 2
        c_3 = line_of_css.strip().endswith(";") and len(line_of_css)
        c_4 = "@import " not in line_of_css
        if c_1 and c_2 and c_3 and c_4:
            propert_len = len(line_of_css.split(":")[0].rstrip()) + 1
            xtra_spaces = " " * (max_indent + 1 - propert_len)
            xtra_spaces = ":" + xtra_spaces
            justified_line_of_css = ""
            justified_line_of_css = line_of_css.split(":")[0].rstrip()
            justified_line_of_css += xtra_spaces
            justified_line_of_css += line_of_css.split(":")[1].lstrip()
            right_justified_css += justified_line_of_css + "\n"
        else:
            right_justified_css += line_of_css + "\n"
    log.debug("Finished Justify to the Right all CSS / SCSS Property values.")
    return right_justified_css if max_indent > 1 else css


@typecheck
def split_long_selectors(css: str) -> str:
    """Split too large CSS Selectors chained with commas if > 80 chars."""
    log.debug("Splitting too long chained selectors on CSS / SCSS.")
    result = ""
    for line in css.splitlines():
        cond_1 = len(line) > 80 and "," in line and line.strip().endswith("{")
        cond_2 = line.startswith(("*", ".", "#"))
        if cond_1 and cond_2:
            result += line.replace(", ", ",").replace(",", ",\n").replace(
                "{", "{\n")
        else:
            result += line + "\n"
    return result


@typecheck
def simple_replace(css: str) -> str:
    """dumb simple replacements on CSS."""
    return css.replace("}\n#", "}\n\n#").replace(
        "}\n.", "}\n\n.").replace("}\n*", "}\n\n*")


@typecheck
def css_prettify(css: str, justify: bool=False) -> str:
    """Prettify CSS main function."""
    log.info("Prettify CSS / SCSS...")
    css = sort_properties(css)
    css = condense_zero_units(css)
    css = wrap_css_lines(css, 80)
    css = split_long_selectors(css)
    css = condense_semicolons(css)
    css = normalize_whitespace(css)
    css = justify_right(css) if justify else css
    css = add_encoding(css)
    css = simple_replace(css)
    log.info("Finished Prettify CSS / SCSS !.")
    return css


##############################################################################
# HTML Prettify


# http://stackoverflow.com/a/15513483
orig_prettify = BeautifulSoup.prettify
regez = re.compile(r'^(\s*)', re.MULTILINE)


def prettify(self, encoding=None, formatter="minimal", indent_width=4):
    """Monkey Patch the BS4 prettify to allow custom indentations."""
    log.debug("Monkey Patching BeautifulSoup on-the-fly to process HTML...")
    return regez.sub(r'\1' * indent_width,
                     orig_prettify(self, encoding, formatter))

BeautifulSoup.prettify = prettify


@typecheck
def html_prettify(html: str) -> str:
    """Prettify HTML main function."""
    log.info("Prettify HTML...")
    html = BeautifulSoup(html).prettify()
    html = html.replace("\t", "    ").strip() + "\n"
    log.info("Finished prettify HTML !.")
    return html


##############################################################################


def walkdir_to_filelist(where, target, omit):
    """Perform full walk of where, gather full path of all files."""
    log.debug("""Recursively Scanning {}, searching for {}, and ignoring {}.
    """.format(where, target, omit))
    return tuple([os.path.join(root, f) for root, d, files in os.walk(where)
                  for f in files if not f.startswith('.') and  # ignore hidden
                  not f.endswith(omit) and  # not process processed file
                  f.endswith(target)])  # only process target files


def process_multiple_files(file_path):
    """Process multiple CSS, HTML files with multiprocessing."""
    log.debug("Process {} is Compressing {0}.".format(os.getpid(), file_path))
    if args.watch:
        previous = int(os.stat(file_path).st_mtime)
        log.info("Process {} is Watching {0}.".format(os.getpid(), file_path))
        while True:
            actual = int(os.stat(file_path).st_mtime)
            if previous == actual:
                sleep(60)
            else:
                previous = actual
                log.debug("Modification detected on {0}.".format(file_path))
                if file_path.endswith((".css", ".scss")):
                    process_single_css_file(file_path)
                else:
                    process_single_html_file(file_path)
    else:
        if file_path.endswith((".css", ".scss")):
            process_single_css_file(file_path)
        else:
            process_single_html_file(file_path)


@typecheck
def prefixer_extensioner(file_path: str) -> str:
    """Take a file path and safely prepend a prefix and change extension.

    This is needed because filepath.replace('.foo', '.bar') sometimes may
    replace '/folder.foo/file.foo' into '/folder.bar/file.bar' wrong!.
    """
    log.debug("Prepending '{}' Prefix to {}.".format(args.prefix, file_path))
    extension = os.path.splitext(file_path)[1].lower()
    filenames = os.path.splitext(os.path.basename(file_path))[0]
    filenames = args.prefix + filenames if args.prefix else filenames
    dir_names = os.path.dirname(file_path)
    file_path = os.path.join(dir_names, filenames + extension)
    return file_path


@typecheck
def process_single_css_file(css_file_path: str) -> str:
    """Process a single CSS file."""
    log.info("Processing CSS / SCSS file: {0}".format(css_file_path))
    global args
    with open(css_file_path, encoding="utf-8-sig") as css_file:
        original_css = css_file.read()
    log.debug("INPUT: Reading CSS file {0}.".format(css_file_path))
    pretty_css = css_prettify(original_css, justify=args.justify)
    if args.timestamp:
        taim = "/* {0} */ ".format(datetime.now().isoformat()[:-7].lower())
        pretty_css = taim + pretty_css
    min_css_file_path = prefixer_extensioner(css_file_path)
    with open(min_css_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(pretty_css)
    log.debug("OUTPUT: Writing CSS Minified {0}.".format(min_css_file_path))
    return pretty_css


@typecheck
def process_single_html_file(html_file_path: str) -> str:
    """Process a single HTML file."""
    log.info("Processing HTML file: {0}".format(html_file_path))
    with open(html_file_path, encoding="utf-8-sig") as html_file:
        pretty_html = html_prettify(html_file.read())
    log.debug("INPUT: Reading HTML file {0}.".format(html_file_path))
    html_file_path = prefixer_extensioner(html_file_path)
    with open(html_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(pretty_html)
    log.debug("OUTPUT: Writing HTML Minified {0}.".format(html_file_path))
    return pretty_html


def check_for_updates():
    """Method to check for updates from Git repo versus this version."""
    this_version = str(open(__file__).read())
    last_version = str(request.urlopen(__source__).read().decode("utf8"))
    if this_version != last_version:
        log.warning("Theres new Version available!,Update from " + __source__)
    else:
        log.info("No new updates!,You have the lastest version of this app.")


def make_root_check_and_encoding_debug():
    """Debug and Log Encodings and Check for root/administrator,return Boolean.

    >>> make_root_check_and_encoding_debug()
    True
    """
    log.info(__doc__)
    log.debug("Python {0} on {1}.".format(python_version(), platform()))
    log.debug("STDIN Encoding: {0}.".format(sys.stdin.encoding))
    log.debug("STDERR Encoding: {0}.".format(sys.stderr.encoding))
    log.debug("STDOUT Encoding:{}".format(getattr(sys.stdout, "encoding", "")))
    log.debug("Default Encoding: {0}.".format(sys.getdefaultencoding()))
    log.debug("FileSystem Encoding: {0}.".format(sys.getfilesystemencoding()))
    log.debug("PYTHONIOENCODING Encoding: {0}.".format(
        os.environ.get("PYTHONIOENCODING", None)))
    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.dont_write_bytecode = True
    if not sys.platform.startswith("win"):  # root check
        if not os.geteuid():
            log.critical("Runing as root is not Recommended,NOT Run as root!.")
            return False
    elif sys.platform.startswith("win"):  # administrator check
        if getuser().lower().startswith("admin"):
            log.critical("Runing as Administrator is not Recommended!.")
            return False
    return True


@typecheck
def set_process_name_and_cpu_priority(name: str) -> bool:
    """Set process name and cpu priority.

    >>> set_process_name_and_cpu_priority("test_test")
    True
    """
    try:
        os.nice(19)  # smooth cpu priority
        libc = cdll.LoadLibrary("libc.so.6")  # set process name
        buff = create_string_buffer(len(name.lower().strip()) + 1)
        buff.value = bytes(name.lower().strip().encode("utf-8"))
        libc.prctl(15, byref(buff), 0, 0, 0)
    except Exception:
        return False  # this may fail on windows and its normal, so be silent.
    else:
        log.debug("Process Name set to: {0}.".format(name))
        return True


def set_single_instance(name, single_instance=True, port=8888):
    """Set process name and cpu priority, return socket.socket object or None.

    >>> isinstance(set_single_instance("test"), socket.socket)
    True
    """
    __lock = None
    if single_instance:
        try:  # Single instance app ~crossplatform, uses udp socket.
            log.info("Creating Abstract UDP Socket Lock for Single Instance.")
            __lock = socket.socket(
                socket.AF_UNIX if sys.platform.startswith("linux")
                else socket.AF_INET, socket.SOCK_STREAM)
            __lock.bind(
                "\0_{name}__lock".format(name=str(name).lower().strip())
                if sys.platform.startswith("linux") else ("127.0.0.1", port))
        except socket.error as e:
            log.warning(e)
        else:
            log.info("Socket Lock for Single Instance: {0}.".format(__lock))
    else:  # if multiple instance want to touch same file bad things can happen
        log.warning("Multiple instance on same file can cause Race Condition.")
    return __lock


def make_logger(name=str(os.getpid())):
    """Build and return a Logging Logger."""
    if not sys.platform.startswith("win") and sys.stderr.isatty():
        def add_color_emit_ansi(fn):
            """Add methods we need to the class."""
            def new(*args):
                """Method overload."""
                if len(args) == 2:
                    new_args = (args[0], copy(args[1]))
                else:
                    new_args = (args[0], copy(args[1]), args[2:])
                if hasattr(args[0], 'baseFilename'):
                    return fn(*args)
                levelno = new_args[1].levelno
                if levelno >= 50:
                    color = '\x1b[31;5;7m\n '  # blinking red with black
                elif levelno >= 40:
                    color = '\x1b[31m'  # red
                elif levelno >= 30:
                    color = '\x1b[33m'  # yellow
                elif levelno >= 20:
                    color = '\x1b[32m'  # green
                elif levelno >= 10:
                    color = '\x1b[35m'  # pink
                else:
                    color = '\x1b[0m'  # normal
                try:
                    new_args[1].msg = color + str(new_args[1].msg) + ' \x1b[0m'
                except Exception as reason:
                    print(reason)  # Do not use log here.
                return fn(*new_args)
            return new
        # all non-Windows platforms support ANSI Colors so we use them
        log.StreamHandler.emit = add_color_emit_ansi(log.StreamHandler.emit)
    else:
        log.debug("Colored Logs not supported on {0}.".format(sys.platform))
    log_file = os.path.join(gettempdir(), str(name).lower().strip() + ".log")
    log.basicConfig(level=-1, filemode="w", filename=log_file,
                    format="%(levelname)s:%(asctime)s %(message)s %(lineno)s")
    log.getLogger().addHandler(log.StreamHandler(sys.stderr))
    adrs = "/dev/log" if sys.platform.startswith("lin") else "/var/run/syslog"
    try:
        handler = log.handlers.SysLogHandler(address=adrs)
    except:
        log.debug("Unix SysLog Server not found,ignored Logging to SysLog.")
    else:
        log.addHandler(handler)
    log.debug("Logger created with Log file at: {0}.".format(log_file))
    return log


@typecheck
def make_post_execution_message(app: str=__doc__.splitlines()[0]) -> str:
    """Simple Post-Execution Message with information about RAM and Time.

    >>> make_post_execution_message() >= 0
    True
    """
    ram_use, ram_all = 0, 0
    if sys.platform.startswith("linux"):
        ram_use = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss *
                      resource.getpagesize() / 1024 / 1024 if resource else 0)
        ram_all = int(
            os.sysconf('SC_PAGE_SIZE') *
            os.sysconf('SC_PHYS_PAGES') / 1024 / 1024
            if hasattr(os, "sysconf") else 0)
    msg = "Total Maximum RAM Memory used: ~{0} of {1} MegaBytes.".format(
        ram_use, ram_all)
    log.info(msg)
    if start_time and datetime:
        log.info("Total Working Time: {0}".format(datetime.now() - start_time))
    print("Thanks for using this App,share your experience!{0}".format("""
    Twitter: https://twitter.com/home?status=I%20Like%20{n}!:%20{u}
    Facebook: https://www.facebook.com/share.php?u={u}&t=I%20Like%20{n}
    G+: https://plus.google.com/share?url={u}""".format(u=__url__, n=app)))
    return msg


def make_arguments_parser():
    """Build and return a command line agument parser."""
    # Parse command line arguments.
    parser = ArgumentParser(description=__doc__, epilog="""CSS-HTML-Prettify:
    Takes file or folder full path string and process all CSS/SCSS/HTML found.
    If argument is not file/folder will fail. Check Updates works on Python3.
    StdIn to StdOut is deprecated since may fail with unicode characters.
    CSS Properties are AlphaSorted,to help spot cloned ones,Selectors not.
    Watch works for whole folders, with minimum of ~60 Secs between runs.""")
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('fullpath', metavar='fullpath', type=str,
                        help='Full path to local file or folder.')
    parser.add_argument('--prefix', type=str,
                        help="Prefix string to prepend on output filenames.")
    parser.add_argument('--timestamp', action='store_true',
                        help="Add a Time Stamp on all CSS/SCSS output files.")
    parser.add_argument('--quiet', action='store_true',
                        help="Quiet, Silent, force disable all Logging.")
    parser.add_argument('--checkupdates', action='store_true',
                        help="Check for Updates from Internet while running.")
    parser.add_argument('--after', type=str,
                        help="Command to execute after run (Experimental).")
    parser.add_argument('--before', type=str,
                        help="Command to execute before run (Experimental).")
    parser.add_argument('--watch', action='store_true',
                        help="Re-Compress if file changes (Experimental).")
    parser.add_argument('--group', action='store_true',
                        help="Group Alphabetically CSS Poperties by name.")
    parser.add_argument('--justify', action='store_true',
                        help="Right Justify CSS Properties (Experimental).")
    global args
    args = parser.parse_args()


def main():
    """Main Loop."""
    make_arguments_parser()
    make_logger("css-html-prettify")
    make_root_check_and_encoding_debug()
    set_process_name_and_cpu_priority("css-html-prettify")
    set_single_instance("css-html-prettify")
    if args.checkupdates:
        check_for_updates()
    if args.quiet:
        log.disable(log.CRITICAL)
    log.info(__doc__ + __version__)
    if args.before and getoutput:
        log.info(getoutput(str(args.before)))
    # Work based on if argument is file or folder, folder is slower.
    if os.path.isfile(args.fullpath
                      ) and args.fullpath.endswith((".css", ".scss")):
        log.info("Target is a CSS / SCSS File.")
        list_of_files = str(args.fullpath)
        process_single_css_file(args.fullpath)
    elif os.path.isfile(args.fullpath
                        ) and args.fullpath.endswith((".htm", ".html")):
        log.info("Target is a HTML File.")
        list_of_files = str(args.fullpath)
        process_single_html_file(args.fullpath)
    elif os.path.isdir(args.fullpath):
        log.info("Target is a Folder with CSS / SCSS, HTML, JS.")
        log.warning("Processing a whole Folder may take some time...")
        list_of_files = walkdir_to_filelist(
            args.fullpath, (".css", ".scss", ".html", ".htm"), ".min.css")
        pool = Pool(cpu_count())  # Multiprocessing Async
        pool.map_async(process_multiple_files, list_of_files)
        pool.close()
        pool.join()
    else:
        log.critical("File or folder not found,or cant be read,or I/O Error.")
        sys.exit(1)
    if args.after and getoutput:
        log.info(getoutput(str(args.after)))
    log.info('-' * 80)
    log.info('Files Processed: {0}.'.format(list_of_files))
    log.info('Number of Files Processed: {0}'.format(
        len(list_of_files) if isinstance(list_of_files, tuple) else 1))
    make_post_execution_message()


if __name__ in '__main__':
    main()
