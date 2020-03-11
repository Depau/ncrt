import asyncio
import sys
from abc import ABC, abstractmethod
from typing import Optional


class Prompt(ABC):
    queue: asyncio.Queue

    # noinspection PyUnusedLocal
    @abstractmethod
    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        pass

    async def __call__(self, msg: str, end=' ', flush=True) -> Optional[str]:
        print(msg, end=end, flush=flush)
        # noinspection PyShadowingBuiltins
        input = await self.queue.get()
        if input is None or input == "":
            return None
        return input.rstrip('\n')

    @staticmethod
    def get(loop: asyncio.AbstractEventLoop = None) -> 'Prompt':
        # if Platform.get() in (Platform.POSIX, Platform.WSL):
        #     return PosixPrompt(loop)
        # else:
        return CommonPrompt(loop)

    def close(self):
        return


# class PosixPrompt(Prompt):
#     def __init__(self, loop: asyncio.AbstractEventLoop = None):
#         super().__init__(loop)
#         self.loop = loop or asyncio.get_event_loop()
#         self.queue = asyncio.Queue(loop=self.loop)
#         self.loop.add_reader(sys.stdin, self._got_input)
#
#     def _got_input(self):
#         if
#         asyncio.ensure_future(self.queue.put(sys.stdin.readline()), loop=self.loop)


# class WindowsPrompt(Prompt):
class CommonPrompt(Prompt):
    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        super().__init__(loop)
        self.loop = loop or asyncio.get_event_loop()
        self.queue = asyncio.Queue(loop=self.loop)
        self._task = self.loop.create_task(self._async_read_input(), name="stdin reader")

    async def _async_read_input(self):
        while self.loop.is_running():
            if not sys.stdin.closed:
                line = await self.loop.run_in_executor(None, sys.stdin.readline)
            else:
                line = None
            await self.queue.put(line)
            if line is None:
                break

    def close(self):
        super().close()
        self._task.cancel()
