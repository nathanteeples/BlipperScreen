import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import time


class CustomScrolledWindow(Gtk.ScrolledWindow):
    def __init__(self, steppers=False, **kwargs):
        args = {
            "hexpand": True,
            "vexpand": True,
            "overlay_scrolling": False
        }
        args.update(kwargs)
        super().__init__(**args)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                        Gdk.EventMask.TOUCH_MASK |
                        Gdk.EventMask.BUTTON_RELEASE_MASK)
        if steppers:
            self.get_vscrollbar().get_style_context().add_class("with-steppers")

        self._last_scroll_sound = 0
        vadj = self.get_vadjustment()
        if vadj is not None:
            vadj.connect("value-changed", self._on_scroll_value_changed)

    def _on_scroll_value_changed(self, _adj):
        parent = self.get_toplevel()
        sounds = getattr(parent, "sounds", None)
        now = time.monotonic()
        if sounds is not None and (now - self._last_scroll_sound) > 0.2:
            sounds.play("scroll")
            self._last_scroll_sound = now
