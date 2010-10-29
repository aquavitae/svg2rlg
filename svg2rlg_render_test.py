#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
svg2rlg is a tool to convert from SVG to reportlab graphics.

License : BSD

version 0.3
"""
import sys
import os
import time
import glob
import tempfile

import wx

from svg2rlg import svg2rlg

#import svglib
USESVGLIB = False

class Log(wx.PyLog):
    """
    Class to send information to the statusbar.
    The statusbar text is reseted afther a delay when
    no pos is used in write method.
    """
    def __init__(self, target, pos = 0, delay = 5000):
        wx.PyLog.__init__(self)
        
        # Do we have a statusbar or normal controll
        self.statusbar = False
        if isinstance(target, wx.StatusBar):
            self.statusbar = True
        
        self.target = target
        self.pos = pos
        self.delay = delay
        
        # Timer to clear text
        self.timer = wx.Timer(self.target, id=1)
        wx.EVT_TIMER(self.target, self.timer.GetId(), self.clear) 
    
    def DoLogString(self, message, timeStamp):
        # This is called with wx.LogMessage etc.
        self.Write(message)
        
    def Write(self, text, pos = None):
        if self.statusbar:
            # Statusbar widget
            if pos is None:
                self.target.SetStatusText(text, self.pos)
                
                if self.timer.IsRunning():
                    self.timer.Stop()
                    
                self.timer.Start(self.delay, oneShot=True)
            
            else:
                self.target.SetStatusText(text, pos)
        else:
            # Normal controll
            self.target.SetLabel(_("Message: %s") % text)
                
            if self.timer.IsRunning():
                self.timer.Stop()
                
            self.timer.Start(self.delay, oneShot=True)
        
    def clear(self, event = None):
        if self.statusbar:
            # Statusbar widget
            self.target.SetStatusText("", self.pos)
        else:
            # Normal controll
            self.target.SetLabel("")
            
TIMEOUT = 450
SCALELIM = 10

class Image(wx.Panel):
    def __init__(self, parent, image = None):
        wx.Panel.__init__(self, parent, -1)
        
        self.image = image
        self.bitmap = wx.StaticBitmap(self)
        
        # timer for resizing image
        self.timer = wx.Timer(self, -1)
        
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        
        wx.CallAfter(self.UpdateImage)
        
    def OnSize(self, evt):
        # stop timer if it is running
        if self.timer.IsRunning():
            self.timer.Stop()
        
        self.timer.Start(milliseconds=TIMEOUT, oneShot=True)
        
        evt.Skip()
    
    def OnTimer(self, evt):
        self.UpdateImage()
        
    def LoadImage(self, filename):
        if wx.Image.CanRead(filename):
            self.image = wx.Image(filename, wx.BITMAP_TYPE_ANY)
        else:
            raise IOError('Could not load image')
        
        wx.CallAfter(self.UpdateImage)
        
    def SetImage(self, image):
        assert isinstance(image, wx.Image)
        self.image = image.Copy()
        self.UpdateImage(force = True)
        
    def UpdateImage(self, force = False):
        if self.image is None:
            return
        
        img = self.image
        width, height = self.Size
        
        # find best scale
        scale = min(float(width) / img.Width, float(height) / img.Height)
        
        # scaled width and height
        swidth = int(img.Width * scale)
        sheight = int(img.Height * scale)
        
        if swidth <= 0. or sheight <= 0.:
            return
            
        # check against last dimension
        # only scale if more than 10 pixels change
        width, height = self.bitmap.Size
        
        if (abs(width - swidth) > SCALELIM or \
           abs(height - sheight) > SCALELIM) or force:
            
            # create scaled copy
            wx.BeginBusyCursor()
            try:
                scaled = img.Scale(swidth, sheight, wx.IMAGE_QUALITY_NORMAL)
            finally:
                wx.EndBusyCursor()
                
            # update panel
            self.bitmap.SetBitmap(scaled.ConvertToBitmap())
            self.bitmap.GetParent().Refresh()
            
class MainWindow(wx.Frame):
    BORDER = 5
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "svg2rlg_compliance",
                          style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetMinSize((640,480))
        
        # Statusbar
        self.statusbar = self.CreateStatusBar(1, wx.ST_SIZEGRIP)
        
         # Create log
        self.log = Log(self.statusbar, 0)
        
        # GUI layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # test names
        widget = wx.StaticText(self, -1, "Test name: ")
        hsizer.Add(widget, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, self.BORDER)
        
        self.TEST_NAMES = glob.glob(r"test-suite\svg\*.svg")
        
        widget = wx.Choice(self, -1, choices = self.TEST_NAMES)
        widget.SetSelection(0)
        self.test_name = self.TEST_NAMES[0]
        hsizer.Add(widget, 0, wx.ALL, self.BORDER)
        
        self.Bind(wx.EVT_CHOICE, self.OnTestName, widget)
        
        # Render button
        widget = wx.Button(self, -1, "Render")
        self.Bind(wx.EVT_BUTTON, self.OnRender, widget)
        hsizer.Add(widget, 0, wx.ALL, 5)
        
        # add hsizer to main sizer        
        sizer.Add(hsizer)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND)
        
        # create splitter
        splitter =  wx.SplitterWindow(self, -1, style = wx.SP_3DSASH | wx.SP_NO_XP_THEME)
        
        # Image view
        self.leftimage = Image(splitter)
        self.rightimage = Image(splitter)
        
        splitter.SplitVertically(self.leftimage, self.rightimage)
        splitter.SetSashGravity(.5)
        
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Fit()
    
    def OnTestName(self, event):
        self.test_name = event.GetString()
    
    def OnRender(self, event):
        # show expected png image
        path, filename = os.path.split(self.test_name)
        name, ext = os.path.splitext(filename)
        
        imgpath = None
        for prefix in ('', 'basic-', 'full-', 'tiny-'):
            imgpath = os.path.join(os.getcwd(), 'test-suite', 'png', prefix + name + '.png')
            if os.path.exists(imgpath):
                break
        
        if not imgpath is None:
            img = wx.Image(imgpath)
            self.rightimage.SetImage(img)
        else:
            self.log.Write('Could not load image: "%s"' % name)
        
        # render svg file
        start = time.clock()
        
        try:
            if USESVGLIB:
                drawing = svglib.svg2rlg(self.test_name)
            else:
                drawing = svg2rlg(self.test_name)
        except:
            type, value, traceback = sys.exc_info()
            msg = str(value)
            
            dlg = wx.MessageDialog(self, msg, "svg2rlg",
                                   wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
            dlg.Raise()
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        delta = time.clock() - start
        
        self.log.Write('Rendered in %.2f seconds' % delta)
        
        fh, tmp = tempfile.mkstemp(suffix = '.png', prefix = "svg2rlg_")
        os.close(fh)
        
        path, filename = os.path.split(tmp)
        name, ext = os.path.splitext(filename)
        
        drawing.save(formats=['png'],outDir=path,fnRoot=name)
        
        img = wx.Image(os.path.join(path, name + '.png'))
        
        self.leftimage.SetImage(img)
        
        
if __name__ == "__main__":
    wx.InitAllImageHandlers()
    
    app = wx.PySimpleApp(0)
    
    mw = MainWindow()
    mw.Show()
    
    app.SetTopWindow(mw)
    app.MainLoop()
    