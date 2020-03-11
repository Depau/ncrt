import asyncio

from ncrt import config
from ncrt.controller.controller import NCRTController
from ncrt.ui.clicrt.view import CLIView
from ncrt.ui.clicrt.viewmodel import CLIViewModel


def main():
    config.ensure_valid()

    event_loop = asyncio.get_event_loop()
    view_model = CLIViewModel()
    controller = NCRTController(view_model)
    view = CLIView(event_loop, controller, view_model)
    event_loop.run_until_complete(view.run())
