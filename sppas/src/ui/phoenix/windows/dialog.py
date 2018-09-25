# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.ui.phoenix.windows.dialog.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import wx

from sppas.src.config import sg
from sppas.src.ui.phoenix.tools import sppasSwissKnife
from sppas.src.ui.phoenix.windows import sppasBitmapTextButton
from sppas.src.ui.phoenix.windows import sppasStaticBitmap
from sppas.src.ui.phoenix.windows import sppasPanel

# ---------------------------------------------------------------------------


class sppasDialog(wx.Dialog):
    """Base class for dialogs in SPPAS.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, *args, **kw):
        """Create a dialog.

        Possible constructors:

            - sppasDialog()
            - sppasDialog(parent, id=ID_ANY, title="", pos=DefaultPosition,
                     size=DefaultSize, style=DEFAULT_DIALOG_STYLE,
                     name=DialogNameStr)

        A sppasDialog is made of 3 (optional) wx.Window() with name:

            - at top: "header"
            - at middle: "content"
            - at bottom: "actions"

        """
        super(sppasDialog, self).__init__(*args, **kw)
        self._init_infos()
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def _init_infos(self):
        """Initialize the main frame.

        Set the title, the icon and the properties of the frame.

        """
        # Fix frame properties
        self.SetMinSize((320, 200))
        w = int(wx.GetApp().settings.frame_size[0] * 0.7)
        h = int(wx.GetApp().settings.frame_size[1] * 0.8)
        self.SetSize(wx.Size(w, h))
        self.SetName('{:s}-{:d}'.format(sg.__name__, self.GetId()))

        # icon
        _icon = wx.Icon()
        bmp = sppasSwissKnife.get_bmp_icon("sppas_32", height=32)
        _icon.CopyFromBitmap(bmp)
        self.SetIcon(_icon)

        # colors & font
        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # -----------------------------------------------------------------------
    # Override existing but un-useful methods
    # -----------------------------------------------------------------------

    def CreateButtonSizer(self, flags):
        """Override to disable."""
        pass

    def CreateSeparatedButtonSizer(self, flags):
        """Override to disable."""
        pass

    def CreateSeparatedSizer(self, sizer):
        """Override to disable."""
        pass

    def CreateStdDialogButtonSizer(self, flags):
        """Override to disable."""
        pass

    def CreateTextSizer(self, message):
        """Override to disable."""
        pass

    # -----------------------------------------------------------------------

    def GetContentWindow(self):
        """Override.

        Return a window containing the main content of the dialog.

        """
        return self.FindWindow("content")

    # -----------------------------------------------------------------------
    # Methods to add/set the header, content, actions
    # -----------------------------------------------------------------------

    def CreateHeader(self, title, icon_name=None):
        """Create a panel including a title with an optional icon.

        :param title: (str) The message in the header
        :param icon_name: (str) Base name of the icon.

        """
        # Create the header panel and sizer
        panel = sppasPanel(self, name="header")
        panel.SetMinSize((-1, wx.GetApp().settings.title_height))
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add the icon, at left, with its title
        if icon_name is not None:
            static_bmp = sppasStaticBitmap(panel, icon_name)
            sizer.Add(static_bmp, 0,
                      wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 10)

        txt = wx.StaticText(panel, label=title)
        sizer.Add(txt, 0, wx.ALIGN_CENTER_VERTICAL)

        # This header panel properties
        panel.SetSizer(sizer)
        self.SetHeader(panel)

    # -----------------------------------------------------------------------

    def SetHeader(self, window):
        """Assign the header window to this dialog.

        :param window: (wx.Window) Any kind of wx.Window, wx.Panel, ...

        """
        window.SetName("header")
        window.SetBackgroundColour(wx.GetApp().settings.header_bg_color)
        window.SetForegroundColour(wx.GetApp().settings.header_fg_color)
        window.SetFont(wx.GetApp().settings.header_text_font)

    # -----------------------------------------------------------------------

    def SetContent(self, object):
        """Assign the content window to this dialog.

        :param window: (wx.Window) Any kind of wx.Window, wx.Panel, ...

        """
        object.SetName("content")
        object.SetBackgroundColour(wx.GetApp().settings.bg_color)
        object.SetForegroundColour(wx.GetApp().settings.fg_color)
        object.SetFont(wx.GetApp().settings.text_font)

    # -----------------------------------------------------------------------

    def CreateActions(self, left_flags, right_flags=()):
        """Create the actions panel.

        Flags is a bit list of the following flags:
            - wx.ID_OK,
            - wx.ID_CANCEL,
            - wx.ID_YES,
            - wx.ID_NO,
            - wx.ID_APPLY,
            - wx.ID_CLOSE,
            - wx.ID_SAVE.

        :param left_flags: (list) Buttons to put at left
        :param right_flags: (list) Buttons to put at right

        """
        # Create the action panel and sizer
        panel = sppasPanel(self, name="actions")
        panel.SetMinSize(wx.Size(-1, wx.GetApp().settings.action_height))

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        if len(left_flags) > 0:
            for i, flag in enumerate(left_flags):
                button = self.__create_button(panel, flag)
                sizer.Add(button, 2, wx.LEFT | wx.EXPAND, 0)
                if len(right_flags) > 0 or i+1 < len(left_flags):
                    line = wx.StaticLine(panel, style=wx.LI_VERTICAL)
                    sizer.Add(line, 0, wx.EXPAND, 0)

        if len(right_flags) > 0:
            if len(left_flags) > 0:
                sizer.AddStretchSpacer(1)

            for flag in right_flags:
                button = self.__create_button(panel, flag)
                line = wx.StaticLine(panel, style=wx.LI_VERTICAL)
                sizer.Add(line, 0, wx.EXPAND, 0)
                sizer.Add(button, 2, wx.RIGHT | wx.EXPAND, 0)

        # This action panel properties
        panel.SetSizer(sizer)
        self.SetActions(panel)

    # -----------------------------------------------------------------------

    def SetActions(self, window):
        """Assign the actions window to this dialog.

        :param window: (wx.Window) Any kind of wx.Window, wx.Panel, ...

        """
        window.SetName("actions")
        window.SetBackgroundColour(wx.GetApp().settings.action_bg_color)
        window.SetForegroundColour(wx.GetApp().settings.action_fg_color)
        window.SetFont(wx.GetApp().settings.action_text_font)

    # ---------------------------------------------------------------------------
    # Put the whole content of the dialog in a sizer
    # ---------------------------------------------------------------------------

    def LayoutComponents(self):
        """Layout the components of the dialog."""
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add header
        header = self.FindWindow("header")
        if header is not None:
            sizer.Add(header, 0, wx.EXPAND, 0)
            h_line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
            sizer.Add(h_line, 0, wx.EXPAND, 0)

        # Add content
        content = self.FindWindow("content")
        if content is not None:
            sizer.Add(content, 1, wx.EXPAND, 0)
        else:
            sizer.AddSpacer(1)

        # Add action buttons
        actions = self.FindWindow("actions")
        if actions is not None:
            h_line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
            sizer.Add(h_line, 0, wx.ALL | wx.EXPAND, 0)
            # proportion is 0 to ask the sizer to never hide the buttons
            sizer.Add(actions, 0, wx.EXPAND, 0)

        # Since Layout doesn't happen until there is a size event, you will
        # sometimes have to force the issue by calling Layout yourself. For
        # example, if a frame is given its size when it is created, and then
        # you add child windows to it, and then a sizer, and finally Show it,
        # then it may not receive another size event (depending on platform)
        # in order to do the initial layout. Simply calling self.Layout from
        # the end of the frame's __init__ method will usually resolve this.
        self.SetSizer(sizer)
        self.Layout()

    # -----------------------------------------------------------------------

    def UpdateUI(self):
        """Assign settings to self and children, then refresh."""
        # colors & font
        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

        # apply new (or not) 'wx' values to content.
        p = self.FindWindow("content")
        if p is not None:
            p.SetBackgroundColour(wx.GetApp().settings.bg_color)
            p.SetForegroundColour(wx.GetApp().settings.fg_color)
            p.SetFont(wx.GetApp().settings.text_font)

        # apply new (or not) 'wx' values to header.
        p = self.FindWindow("header")
        if p is not None:
            p.SetBackgroundColour(wx.GetApp().settings.header_bg_color)
            p.SetForegroundColour(wx.GetApp().settings.header_fg_color)
            p.SetFont(wx.GetApp().settings.header_text_font)

        # apply new (or not) 'wx' values to actions.
        p = self.FindWindow("actions")
        if p is not None:
            p.SetBackgroundColour(wx.GetApp().settings.action_bg_color)
            p.SetForegroundColour(wx.GetApp().settings.action_fg_color)
            p.SetFont(wx.GetApp().settings.action_text_font)

        self.Refresh()

    # ---------------------------------------------------------------------------
    # Private
    # ---------------------------------------------------------------------------

    def __create_button(self, parent, flag):
        """Create a button from a flag and return it.

        :param parent: (wx.Window)
        :param flag: (int)

        """
        btns = {
            wx.ID_OK: ("Okay", "ok"),
            wx.ID_CANCEL: ("Cancel", "cancel"),
            wx.ID_YES: ("Yes", "yes"),
            wx.ID_NO: ("No", "no"),
            wx.ID_APPLY: ("Apply", "apply"),
            wx.ID_CLOSE: ("Close", "close-window"),
            wx.ID_SAVE: ("Save", "save"),
        }
        btn = sppasBitmapTextButton(parent, btns[flag][0], btns[flag][1])
        btn.SetId(flag)

        if flag == wx.CANCEL:
            self.SetAffirmativeId(wx.ID_CANCEL)

        elif flag in (wx.CLOSE, wx.OK):
            btn.SetDefault()
            btn.SetFocus()
            self.SetAffirmativeId(flag)

        elif flag == wx.YES:
            self.SetAffirmativeId(wx.ID_YES)

        elif flag == wx.OK:
            btn.SetDefault()

        return btn
