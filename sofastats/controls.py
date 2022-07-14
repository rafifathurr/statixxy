"""
Although a lot of this is based on wxPython in Action the APIs have changed in
some cases with wxPython 4 vs 2.8) e.g. ApplyEdit.
"""
import wx  #@UnusedImport
import wx.grid

## new event types to pass around
myEVT_TEXT_BROWSE_KEY_DOWN = wx.NewEventType()
## events to bind to
EVT_TEXT_BROWSE_KEY_DOWN = wx.PyEventBinder(myEVT_TEXT_BROWSE_KEY_DOWN, 1)

MY_KEY_TEXT_BROWSE_BROWSE_BTN = 1000  ## wx.WXK_SPECIAL20 is 212 and is highest?
MY_KEY_TEXT_BROWSE_MOVE_NEXT = 1001


class KeyDownEvent(wx.PyCommandEvent):
    "See 3.6.1 in wxPython in Action"
    def __init__(self, evtType, _id):
        wx.PyCommandEvent.__init__(self, evtType, _id)

    def set_key_code(self, keycode):
        self.keycode = keycode

    def get_key_code(self):
        return self.keycode


class TextBrowse(wx.Control):
    """
    Custom control with a text box and browse button (to populate text box).

    Handles Enter key and tab key strokes as expected. Tab from text takes you
    to the Browse button. Enter in the text disables editor and we go down. Tab
    from the Browse button and we go back to the text. Enter is allowed to be
    processed normally. NB if Enter hit when in text box, a custom event is sent
    for processing.
    """

    def __init__(self, parent, _id, grid, file_phrase, wildcard=''):
        wx.Control.__init__(self, parent, -1)
        self.debug = False
        self.parent = parent
        self.grid = grid
        self.file_phrase = file_phrase
        self.wildcard = wildcard
        self.txt = wx.TextCtrl(self, -1, '', style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.txt.Bind(wx.EVT_KEY_DOWN, self.on_txt_key_down)
        self.btn_browse = wx.Button(self, -1, _('Browse ...'))
        self.btn_browse.Bind(wx.EVT_BUTTON, self.on_btn_browse_click)
        szr = wx.BoxSizer(wx.HORIZONTAL)
        self.txt_margins = 3
        self.btn_margin = 3
        szr.Add(self.txt, 1, wx.RIGHT|wx.LEFT, self.txt_margins)
        szr.Add(self.btn_browse, 0, wx.RIGHT, self.btn_margin)
        szr.SetSizeHints(self)
        self.SetSizer(szr)
        self.Layout()

    def on_size(self, evt):
        if self.debug: print("resizing")
        overall_width = self.GetSize()[0]
        btn_width, btn_height = self.btn_browse.GetSize()
        inner_padding = (2*self.txt_margins) + self.btn_margin
        txt_width = overall_width - (btn_width + inner_padding)
        self.txt.SetSize(wx.Size(txt_width, btn_height-2))
        self.txt.SetSize(-1, 3, txt_width, -1)
        btn_x_pos = overall_width - (btn_width + self.btn_margin)        
        self.btn_browse.SetSize(btn_x_pos, 2, btn_width, btn_height)
        evt.Skip() # otherwise, resizing sets infinite number of EndEdits!    

    def on_txt_key_down(self, evt):
        """
        http://wiki.wxpython.org/AnotherTutorial#head-999ff1e3fbf5694a51a91cf4ed2140f692da013c
        """
        if self.debug: print("txt key down")
        if evt.GetKeyCode() in [wx.WXK_RETURN, wx.WXK_TAB]:
            key_event = KeyDownEvent(myEVT_TEXT_BROWSE_KEY_DOWN, self.GetId())
            key_event.SetEventObject(self)
            key_event.set_key_code(MY_KEY_TEXT_BROWSE_MOVE_NEXT)
            self.GetEventHandler().ProcessEvent(key_event)
        elif evt.GetKeyCode() == wx.WXK_ESCAPE:
            key_event = KeyDownEvent(myEVT_TEXT_BROWSE_KEY_DOWN, self.GetId())
            key_event.SetEventObject(self)
            key_event.set_key_code(wx.WXK_ESCAPE)
            self.GetEventHandler().ProcessEvent(key_event)
        else:
            evt.Skip()

    def on_btn_browse_click(self, _evt):
        """
        Open dialog and takes the file selected (if any)
        """
        gotval = False
        dlg_get_file = wx.FileDialog(
            self, message=self.file_phrase, wildcard=self.wildcard)
        ## MUST have a parent to enforce modal in Windows
        if dlg_get_file.ShowModal() == wx.ID_OK:
            self.txt.SetValue(dlg_get_file.GetPath())
            gotval = True
        dlg_get_file.Destroy()
        if gotval:
            key_event = KeyDownEvent(myEVT_TEXT_BROWSE_KEY_DOWN, self.GetId())
            key_event.SetEventObject(self)
            key_event.set_key_code(MY_KEY_TEXT_BROWSE_BROWSE_BTN)
            self.GetEventHandler().ProcessEvent(key_event)

    def set_text(self, text):
        if self.debug: print("setting text")
        self.txt.SetValue(text)

    def set_insertion_point(self, i):
        if self.debug: print("setting insertion point")
        self.txt.SetInsertionPoint(i)

    def get_text(self):
        if self.debug: print("getting the text")
        return self.txt.GetValue()

    def set_focus(self):
        "Must implement this if I want to call for the custom control"
        if self.debug: print("setting the focus")
        self.txt.SetFocus()


class GridCellTextBrowseEditor(wx.grid.GridCellEditor):
    """
    Provides a text box and a browse button (which can populate the text box).

    The text browser can send a special event to the grid frame if Enter key
    pressed while in the text box.
    """
    def __init__(self, grid, file_phrase, wildcard):
        self.debug = False
        wx.grid.GridCellEditor.__init__(self)
        self.grid = grid
        self.file_phrase = file_phrase
        self.wildcard = wildcard

    def Create(self, parent, _id, evt_handler):
        self.text_browse = TextBrowse(
            parent, -1, self.grid, self.file_phrase, self.wildcard)
        self.SetControl(self.text_browse)
        if evt_handler:
            self.text_browse.PushEventHandler(evt_handler)

    def BeginEdit(self, row, col, grid):
        if self.debug: print('Beginning edit')
        self.text_browse.set_text(grid.GetCellValue(row, col))
        self.text_browse.set_focus()

    def StartingKey(self, event):
        if event.GetKeyCode() <= 255:
            self.text_browse.set_text(chr(event.GetKeyCode()))
            self.text_browse.set_insertion_point(1)
        else:
            event.Skip()

    def SetSize(self, rect):
        self.text_browse.SetSize(
            rect.x, rect.y-2, rect.width,
            rect.height+5, wx.SIZE_ALLOW_MINUS_ONE)

    def EndEdit(self, row, col, grid, oldval):
        """
        This function must check if the current value of the editing cell is
        valid and different from the original value in its string form. If
        not then simply return None. If it has changed then this method should
        save the new value so that ApplyEdit can apply it later and the string
        representation of the new value should be returned.
        """
        newval = self.text_browse.get_text()
        if newval == oldval:
            return None
        else:
            return True

    def ApplyEdit(self, row, col, grid):
        """
        Effectively save the changes in the grid.

        This function should save the value of the control in the grid. It is
        called only after EndEdit returns True
        """
        grid.SetCellValue(row, col, self.text_browse.get_text())

    def Reset(self):
        pass  ## N/A

    def Clone(self):
        return GridCellTextBrowseEditor(self.file_phrase, self.wildcard)

