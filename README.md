# css-html-prettify
Async single-file cross-platform Unicode-ready Python3-ready Prettifier Beautifier for the Web.


[![GPL License](http://img.shields.io/badge/license-GPL-blue.svg?style=plastic)](http://opensource.org/licenses/GPL-3.0) [![LGPL License](http://img.shields.io/badge/license-LGPL-blue.svg?style=plastic)](http://opensource.org/licenses/LGPL-3.0) [![Python Version](https://img.shields.io/badge/Python-3-brightgreen.svg?style=plastic)](http://python.org) [![Join the chat at https://gitter.im/juancarlospaco/css-html-js-minify](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/juancarlospaco/css-html-js-minify?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge "Chat with Users and Developers, Get Solutions, Offer Help")


[![Donate BitCoins](https://www.coinbase.com/assets/buttons/donation_large-5cf4f17cc2d2ae2f45b6b021ee498297409c94dcf0ba1bbf76fd5668e80b0d02.png)](https://www.coinbase.com/checkouts/c3538d335faee0c30c81672ea0223877 "Donate Bitcoins") [![Subscribe with BitCoins](https://www.coinbase.com/assets/buttons/subscription_large-11d991f628216af05156fae88a48ce25c0cb36447a265421a43a62e572af3853.png)](https://www.coinbase.com/checkouts/c3538d335faee0c30c81672ea0223877 "Subscribe with BitCoins") [![Pay with BitCoins](https://www.coinbase.com/assets/buttons/buy_now_large-6f15fa5979d25404827a7329e8a5ec332a42cf4fd73e27a2c3ccda017034e1b0.png)](https://www.coinbase.com/checkouts/c3538d335faee0c30c81672ea0223877 "Pay with BitCoins") [![Donate](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif "Donate with or without Credit Card")](http://goo.gl/cB7PR)

https://pypi.python.org/pypi/css-html-prettify

```bash
css-html-prettify.py --help

usage: css-html-prettify.py [-h] [--version] [--prefix PREFIX] [--timestamp]
[--quiet] [--checkupdates] [--after AFTER]
[--before BEFORE] [--watch] [--group] [--justify]
fullpath

CSS-HTML-Prettify. StandAlone Async single-file cross-platform no-dependencies
Unicode-ready Python3-ready Prettifier Beautifier for the Web.

positional arguments:
    fullpath         Full path to local file or folder.

optional arguments:
    -h, --help       show this help message and exit
    --version        show programs version number and exit
    --prefix PREFIX  Prefix string to prepend on output filenames.
    --timestamp      Add a Time Stamp on all CSS/SCSS output files.
    --quiet          Quiet, Silent, force disable all Logging.
    --checkupdates   Check for Updates from Internet while running.
    --after AFTER    Command to execute after run (Experimental).
    --before BEFORE  Command to execute before run (Experimental).
    --watch          Re-Compress if file changes (Experimental).
    --group          Group Alphabetically CSS Poperties by name.
    --justify        Right Justify CSS Properties (Experimental).
    --extraline      Add 1 New Line for each New Line (Experimental)
    --beep           Beep sound will be played when it ends at exit.

CSS-HTML-Prettify: Takes file or folder full path string and process all
CSS/SCSS/HTML found. If argument is not file/folder will fail. Check Updates
works on Python3. StdIn to StdOut is deprecated since may fail with unicode
characters. CSS Properties are AlphaSorted,to help spot cloned ones,Selectors
not. Watch works for whole folders, with minimum of ~60 Secs between runs.
```

- Takes a full path to anything, a file or a folder, then parse, Prettify and Beautify for Human Development.
- If full path is a folder with multiple files it will use Async Multiprocessing.
- Pretty-Printed colored Logging to Standard Output and Log File on OS Temporary Folder.
- Set its own Process name and show up on Process lists.
- Full Unicode/UTF-8 support, SASS SCSS Support.
- Smooth CPU usage.
- Can Watch for changes on files.
- Can execute arbitrary commands after and before running.
- `*.css` files are saved as `*.css`, `*.html` are saved as `*.html`, unless provided a prefix.


# Usage:

```bash
css-html-prettify.py file.html

css-html-prettify.py file.htm

css-html-prettify.py file.css

css-html-prettify.py file.scss

css-html-prettify.py /project/static/
```


# Install permanently on the system:

**PIP:** *(Recommended!)*
```
sudo pip3 install css-html-prettify
```


**Input CSS:**
```css
/* dont remove this comment */
.class, #NotHex, input[type="text"], a:hover  {
    border:none;
    margin:0 0 0 0;
    border-color:    fuchsia;
    color:           mediumspringgreen;
    background-position:0 0;
    transform-origin:0 0;
    margin: 0px !important;
    color: #000000;
    background-color: #FFFFFF;
}





.foo {content: "If you leave too much new lines it will add a horizontal line"}
```

**Output CSS:**
```css
@charset utf-8;


/* dont remove this comment */
.class, #NotHex, input[type="text"], a:hover {
    background-color:    #FFFFFF;
    background-position: 0 0;
    border:              none;
    border-color:        fuchsia;

    color:               mediumspringgreen;
    color:               #000000;

    margin:              0 0 0 0;
    margin:              0 !important;

    transform-origin:    0 0;
}




/* ------------------------------------------------------------------------ */




.foo {content: "If you leave too much new lines it will add a horizontal line"}


```


# Why?:

- This project is the small brother of [another project that does the inverse, a Minifier Compressor for the Web.](https://github.com/juancarlospaco/css-html-js-minify#css-html-js-minify)


# Requisites:

- [Python 3.x](https://www.python.org "Python Homepage")
- BeautifulSoup 4.
- Anglerfish.


# Coding Style Guide:

- Lint, [PEP-8](https://www.python.org/dev/peps/pep-0008), [PEP-257](https://www.python.org/dev/peps/pep-0257), [PyLama](https://github.com/klen/pylama#-pylama), [iSort](https://github.com/timothycrosley/isort) must Pass Ok. `pip install pep8 pep257 pylama isort`
- If theres any kind of Tests, they must Pass Ok, if theres no Tests, its ok, if Tests provided, is even better.


# Contributors:

- **Please Star this Repo on Github !**, it helps to show up faster on searchs.
- **Ad-Hocracy Meritocracy**: 3 Pull Requests Merged on Master you become Repo Admin. *Join us!*
- [Help](https://help.github.com/articles/using-pull-requests) and more [Help](https://help.github.com/articles/fork-a-repo) and Interactive Quick [Git Tutorial](https://try.github.io).


# Licence:

- GNU GPL Latest Version *AND* GNU LGPL Latest Version *AND* any Licence [YOU Request via Bug Report](https://github.com/juancarlospaco/css-html-prettify/issues/new).


Donate, Charityware :
---------------------

- [Charityware](https://en.wikipedia.org/wiki/Donationware) is a licensing model that supplies fully operational unrestricted software to the user and requests an optional donation be paid to a third-party beneficiary non-profit. The amount may be left to discretion of the user.
- If you want to Donate please [click here](http://www.icrc.org/eng/donations/index.jsp) or [click here](http://www.atheistalliance.org/support-aai/donate) or [click here](http://www.msf.org/donate) or [click here](http://richarddawkins.net/) or [click here](http://www.supportunicef.org/) or [click here](http://www.amnesty.org/en/donate) or [click here](http://www.rescue.org/irc-fast-facts)
