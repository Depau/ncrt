
# ncrt - ncurses SecureCRT session browser

Actually not yet, the back-end is barely working and currently only
a shell-like front-end is implemented.

Soon I will finish it and add an urwid-based front-end, maybe some
other GUI front-ends.

# Project objectives

- Build something that will make me never want to open SecureCRT again
- Be easy to use with a keyboard, easy and fast navigation
- Be as fast as possible (performance-wise)
- Support searching sessions
- Support SSH sessions, but be easily extensible for other protocols
- Support customizable handlers for sessions, for example:
    - ssh (for the shell)
    - FileZilla (for SFTP/FTP/FTPS)
    - Allow printing a pre-generated command line for manual usage (useful for `scp`)
- Support all major operating systems (except macOS unless you guys send PRs)
    - That includes Windows, since I have to use Windows at work
    - That also includes GNU/Linux
    - WSL is also to be supported (though, for performance, native Windows usage
      would be preferred)
    - I think macOS will work as long as GNU/Linux works but I don't have any
      CrapBookPro handy to check

In the long term, if I feel like it or if anybody wants to send patches:

- Port to GTK and Qt, `gcrt` and `qtcrt`
    - I'm trying hard to adopt an MVC pattern to make porting to other toolkits
      easy
    - I hope this doesn't end up in utter crap
- Support writing session files
    
## About `clicrt`

`clicrt` is currently the only implemented user interface, it serves mostly as a
development aid to test the code easily before implementing a decent UI.

(but don't worry, I will write unit tests too ;) )

## License

This work is licensed under the GNU General Public License v3.0 