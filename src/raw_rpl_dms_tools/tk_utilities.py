"""Utilities for tkinter, including a Tooltip."""

from typing import Literal

import tkinter as tk
from tkinter import ttk, font


class Tooltip:
    """Add a tooltip for a given widget as the mouse goes on it.

    From: https://stackoverflow.com/a/41381685/20921535

    see:

    http://stackoverflow.com/questions/3221956/
           what-is-the-simplest-way-to-make-tooltips-
           in-tkinter/36221216#36221216

    http://www.daniweb.com/programming/software-development/
           code/484591/a-tooltip-class-for-tkinter

    - Originally written by vegaseat on 2014.09.09.

    - Modified to include a delay time by Victor Zaccardo on 2016.03.25.

    - Modified
        - to correct extreme right and extreme bottom behavior,
        - to stay inside the screen whenever the tooltip might go out on
          the top but still the screen is higher than the tooltip,
        - to use the more flexible mouse positioning,
        - to add customizable background color, padding, waittime and
          wraplength on creation
      by Alberto Vassena on 2016.11.05.

      Tested on Ubuntu 16.04/16.10, running Python 3.5.2

    TODO: themes styles support
    """

    def __init__(
        self,
        widget: tk.Widget,
        *,
        fg: str = "#000000",
        bg: str = '#FFFFEA',
        pad: tuple[int, int, int, int] = (5, 3, 5, 3),
        text: str = 'widget info',
        waittime: int = 400,
        wraplength: int = 400,
    ) -> None:

        self.waittime = waittime
        self.wraplength = wraplength
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.onEnter)
        self.widget.bind("<Leave>", self.onLeave)
        self.widget.bind("<ButtonPress>", self.onLeave)
        self.fg = fg
        self.bg = bg
        self.pad = pad
        self.id = None
        self.tw = None

    def onEnter(self, event: tk.Event | None = None) -> None:
        """Enter event."""
        self.schedule()

    def onLeave(self, event: tk.Event | None = None) -> None:
        """Leave event."""
        self.unschedule()
        self.hide()

    def schedule(self) -> None:
        """Schedule."""
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.show)

    def unschedule(self) -> None:
        """Unschedule."""
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def show(self) -> None:
        """Show."""
        def tip_pos_calculator(
            widget: tk.Widget,
            label: tk.Label, *,
            tip_delta: tuple[int, int] = (10, 5),
            pad: tuple[int, int, int, int] = (5, 3, 5, 3)
        ) -> tuple[int, int]:

            w = widget

            s_width, s_height = w.winfo_screenwidth(), w.winfo_screenheight()

            width, height = (
                pad[0] + label.winfo_reqwidth() + pad[2],
                pad[1] + label.winfo_reqheight() + pad[3]
            )

            mouse_x, mouse_y = w.winfo_pointerxy()

            x1, y1 = mouse_x + tip_delta[0], mouse_y + tip_delta[1]
            x2, y2 = x1 + width, y1 + height

            x_delta = x2 - s_width
            if x_delta < 0:
                x_delta = 0
            y_delta = y2 - s_height
            if y_delta < 0:
                y_delta = 0

            offscreen = (x_delta, y_delta) != (0, 0)

            if offscreen:
                if x_delta:
                    x1 = mouse_x - tip_delta[0] - width

                if y_delta:
                    y1 = mouse_y - tip_delta[1] - height

            offscreen_again = y1 < 0  # out on the top

            if offscreen_again:
                # No further checks will be done.

                # TIP:
                # A further mod might automagically augment the
                # wraplength when the tooltip is too high to be
                # kept inside the screen.
                y1 = 0

            return x1, y1

        fg = self.fg
        bg = self.bg
        pad = self.pad
        widget = self.widget

        # creates a toplevel window
        self.tw = tk.Toplevel(widget)

        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)

        win = tk.Frame(
            self.tw,
            background=bg,
            borderwidth=0,
        )
        label = tk.Label(
            win,
            text=self.text,
            justify=tk.LEFT,
            fg=fg,
            background=bg,
            relief=tk.SOLID,
            borderwidth=0,
            wraplength=self.wraplength
        )

        label.grid(
            padx=(pad[0], pad[2]),
            pady=(pad[1], pad[3]),
            sticky=tk.NSEW,
        )
        win.grid()

        x, y = tip_pos_calculator(widget, label)

        self.tw.wm_geometry("+%d+%d" % (x, y))

    def hide(self) -> None:
        """Hide."""
        tw = self.tw
        if tw:
            tw.destroy()
        self.tw = None


class LabelText(tk.Text):
    """tk.Text styled as ttk.Label with selectable, copyable text."""
    def __init__(
        self,
        *args,
        text: str,
        justify: Literal["left", "right"] = "left",
        **kwargs
    ) -> None:
        super().__init__(*args, height=1, **kwargs)
        self.set_text(text)
        self.configure(font=font.nametofont('TkTextFont'))
        try:
            bg = self.master.cget('bg')  # tk
        except tk.TclError:
            style = self.master.cget("style") or self.master.winfo_class()  # ttk
            bg = ttk.Style().lookup(style, 'background')
        self.configure(bg=bg, relief="flat")
        self.configure(state="disabled")
        self.tag_configure('tag-justify', justify=justify)
        self.configure(cursor="arrow")  # No mouse cursor

    def set_text(self, text: str) -> None:
        """Set the text."""
        self.configure(state="normal")
        self.delete(1.0, "end")
        self.insert(1.0, text, 'tag-justify')
        self.configure(state="disabled")


class ModalDialog(tk.Toplevel):
    """Modal dialog window that takes full application focus.

    ```
    window = tk.Tk()
    window.protocol("WM_DELETE_WINDOW", parent.destroy)
    dialog = ModalDialog(window)
    dialog.grid_rowconfigure(index=0, weight=1)
    dialog.grid_columnconfigure(index=0, weight=1)
    tk.Label(dialog, text="Loading...").grid(row=0, column=0)
    window.after(ms=2 * 1000, func=dialog.destroy)
    ```
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        geometry: str = f"+{self.master.winfo_rootx()}+{self.master.winfo_rooty()}"
        self.geometry(geometry)  # Set to root position
        self.transient(kwargs.get("master"))
        self.title("Dialog")
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)


class ModalLoadingDialog(ModalDialog):
    """Convenience ModalDialog with an indeterminate ttk.Progressbar and text."""
    def __init__(
        self,
        *args,
        text: str = "Loading...",
        auto_start: bool = True,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        pad: tuple[int, int] = (5, 5)
        self.grid_rowconfigure(index=0, weight=1)
        self.grid_columnconfigure(index=0, weight=1)
        self.grid_columnconfigure(index=1, weight=1)
        self.label = ttk.Label(master=self, text=text)
        self.label.grid(row=0, column=0, sticky="e", padx=pad, pady=pad)
        self.progressbar = ttk.Progressbar(master=self, mode="indeterminate")
        self.progressbar.grid(row=0, column=1, sticky="w", padx=pad, pady=pad)
        if auto_start:
            self.start()

    def start(self, interval: int = 10) -> None:
        """Start the progressbar."""
        self.progressbar.start(interval=interval)
