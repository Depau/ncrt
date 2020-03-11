import asyncio
import errno
import functools
import textwrap
from typing import cast

from ncrt import NAME, VERSION
from ncrt.controller.controller import NCRTController
from ncrt.model.entry import EntryType, SessionEntry
from ncrt.ui.clicrt.prompt import Prompt
from ncrt.ui.clicrt.viewmodel import CLIViewModel
from ncrt.ui.viewbase import ViewBase


# noinspection PyUnusedLocal
class CLIView(ViewBase):
    def __init__(self, mainloop: asyncio.AbstractEventLoop, controller: NCRTController, view_model: CLIViewModel):
        self.mainloop = mainloop
        self.controller = controller
        self.view_model = view_model
        self.prompt = Prompt.get(mainloop)
        self._should_stop = False

        self._commands = tuple(i[5:] for i in dir(self) if i.startswith("_cmd_"))

    async def _cmd_quit(self, *a, **kw):
        """
        quit

        Quit clicrt.
        """
        print("Bye!")
        self._should_stop = True

    async def _cmd_cd(self, args: str = None):
        """
        cd, cd [directory]

        Enter a subdirectory. If no argument is provided, go back to top directory.
        """
        if not args:
            self.controller.cd('/')
        try:
            self.controller.cd(args)
        except OSError as err:
            if err.errno == errno.ENOENT:
                print("Specified location does not exist")
            elif err.errno == errno.ENOTDIR:
                print("Specified location is not a directory")
            else:
                raise

    @staticmethod
    async def _print_listing(coro, full_path=False):
        async for entry in coro():
            path = "" if not full_path else (entry.parent.full_path + "/")
            if entry.entry_type == EntryType.DIRECTORY:
                print(f"> {path}{entry.name}")
            else:
                entry = cast(SessionEntry, entry)
                print(f"  {path}{entry.name.ljust(40)} ({entry.type}, {entry.user}@{entry.host})")
        pass

    async def _cmd_ls(self, args: str = None):
        """
        ls

        List subdirectories and sessions in the current directory.
        """
        await self._print_listing(self.controller.ls)

    async def _cmd_run(self, args: str = None):
        pass

    async def _cmd_find(self, args: str = None):
        """
        find [pattern]

        Recursively ind items matching "pattern" in the current directory.
        """
        print(f"Search results for '{args}' in current directory:")
        await self._print_listing(functools.partial(self.controller.find, args), full_path=True)

    async def _cmd_help(self, args: str = None):
        """
        help, help [command]

        Get help on clicrt or its commands.
        """
        if not args:
            print("Available commands:")
            print(', '.join(self._commands))
            print()
            print("Run 'help [command]' to see a command's help")
            print("Note that all commands's syntax is: 'command_name [SPACE] argument'")
            print("All commands accept only zero or one argument, no need for quoting")
        else:
            if args not in self._commands:
                print(f"Invalid command: {args}")
            else:
                fn = getattr(self, f"_cmd_{args}")
                print(textwrap.dedent(fn.__doc__).strip())

    async def _loop(self):
        cmdline = await self.prompt(f"{self.view_model.current_dir.full_path}>")

        if cmdline == "":
            return
        if cmdline is None:  # stdin closed
            return await self._cmd_quit()

        if ' ' in cmdline:
            cmd, args = cmdline.split(' ', 1)
        else:
            cmd, args = cmdline, None

        handler = getattr(self, f"_cmd_{cmd}", None)
        if not handler:
            print("Invalid command")
            return

        await handler(args)

    async def run(self):
        print(f"clicrt ({NAME} v{VERSION})")
        print(f"Supported commands: {', '.join(sorted(self._commands))}")

        while self.mainloop.is_running() and not self._should_stop:
            await self._loop()

        self.prompt.close()
