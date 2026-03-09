"""
System tray manager -- allows VoxControl to run minimized to tray.
Uses pystray for Windows system tray integration.
"""

import logging
import threading
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class SystemTrayManager:
    """Manages a Windows system tray icon with context menu."""

    def __init__(
        self, *,
        on_show: Callable,
        on_quit: Callable,
    ):
        self._on_show = on_show
        self._on_quit = on_quit
        self._icon = None
        self._thread: Optional[threading.Thread] = None
        self._alive = False

    def start(self):
        """Start the tray icon in a background thread."""
        try:
            import pystray
            from PIL import Image, ImageDraw
        except ImportError:
            logger.debug("pystray or Pillow not installed — tray disabled")
            return

        # Create a simple icon (purple circle with mic shape)
        image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        # Background circle
        draw.ellipse([4, 4, 60, 60], fill=(108, 99, 255, 255))
        # Mic body
        draw.rounded_rectangle([24, 14, 40, 38], radius=8, fill=(255, 255, 255, 255))
        # Mic stand
        draw.arc([20, 28, 44, 48], start=0, end=180, fill=(255, 255, 255, 255), width=2)
        draw.line([32, 48, 32, 54], fill=(255, 255, 255, 255), width=2)
        draw.line([26, 54, 38, 54], fill=(255, 255, 255, 255), width=2)

        menu = pystray.Menu(
            pystray.MenuItem("Show VoxControl", self._show, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._quit),
        )

        self._icon = pystray.Icon("VoxControl", image, "VoxControl", menu)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._alive = True

    def _run(self):
        if self._icon:
            self._icon.run()

    def _show(self, icon=None, item=None):
        self._on_show()

    def _quit(self, icon=None, item=None):
        self._on_quit()

    def stop(self):
        self._alive = False
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass

    def is_alive(self) -> bool:
        return self._alive
