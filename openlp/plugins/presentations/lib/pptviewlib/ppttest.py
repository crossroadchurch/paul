# -*- coding: utf-8 -*-
# vim: autoindent shiftwidth=4 expandtab textwidth=120 tabstop=4 softtabstop=4

###############################################################################
# OpenLP - Open Source Lyrics Projection                                      #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2015 OpenLP Developers                                   #
# --------------------------------------------------------------------------- #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation; version 2 of the License.                              #
#                                                                             #
# This program is distributed in the hope that it will be useful, but WITHOUT #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    #
# more details.                                                               #
#                                                                             #
# You should have received a copy of the GNU General Public License along     #
# with this program; if not, write to the Free Software Foundation, Inc., 59  #
# Temple Place, Suite 330, Boston, MA 02111-1307 USA                          #
###############################################################################

import sys
from PyQt4 import QtGui, QtCore
from ctypes import *
from ctypes.wintypes import RECT


class PPTViewer(QtGui.QWidget):
    """
    Standalone Test Harness for the pptviewlib library
    """
    def __init__(self, parent=None):
        super(PPTViewer, self).__init__(parent)
        self.pptid = -1
        self.setWindowTitle('PowerPoint Viewer Test')

        ppt_label = QtGui.QLabel('Open PowerPoint file')
        slide_label = QtGui.QLabel('Go to slide #')
        self.pptEdit = QtGui.QLineEdit()
        self.slideEdit = QtGui.QLineEdit()
        x_label = QtGui.QLabel('X pos')
        y_label = QtGui.QLabel('Y pos')
        width_label = QtGui.QLabel('Width')
        height_label = QtGui.QLabel('Height')
        self.xEdit = QtGui.QLineEdit('100')
        self.yEdit = QtGui.QLineEdit('100')
        self.widthEdit = QtGui.QLineEdit('900')
        self.heightEdit = QtGui.QLineEdit('700')
        self.total = QtGui.QLabel()
        ppt_btn = QtGui.QPushButton('Open')
        ppt_dlg_btn = QtGui.QPushButton('...')
        folder_label = QtGui.QLabel('Slide .bmp path')
        self.folderEdit = QtGui.QLineEdit('slide')
        slide_btn = QtGui.QPushButton('Go')
        prev = QtGui.QPushButton('Prev')
        next = QtGui.QPushButton('Next')
        blank = QtGui.QPushButton('Blank')
        unblank = QtGui.QPushButton('Unblank')
        restart = QtGui.QPushButton('Restart')
        close = QtGui.QPushButton('Close')
        resume = QtGui.QPushButton('Resume')
        stop = QtGui.QPushButton('Stop')
        grid = QtGui.QGridLayout()
        row = 0
        grid.addWidget(folder_label, 0, 0)
        grid.addWidget(self.folderEdit, 0, 1)
        row += 1
        grid.addWidget(x_label, row, 0)
        grid.addWidget(self.xEdit, row, 1)
        grid.addWidget(y_label, row, 2)
        grid.addWidget(self.yEdit, row, 3)
        row += 1
        grid.addWidget(width_label, row, 0)
        grid.addWidget(self.widthEdit, row, 1)
        grid.addWidget(height_label, row, 2)
        grid.addWidget(self.heightEdit, row, 3)
        row += 1
        grid.addWidget(ppt_label, row, 0)
        grid.addWidget(self.pptEdit, row, 1)
        grid.addWidget(ppt_dlg_btn, row, 2)
        grid.addWidget(ppt_btn, row, 3)
        row += 1
        grid.addWidget(slide_label, row, 0)
        grid.addWidget(self.slideEdit, row, 1)
        grid.addWidget(slide_btn, row, 2)
        row += 1
        grid.addWidget(prev, row, 0)
        grid.addWidget(next, row, 1)
        row += 1
        grid.addWidget(blank, row, 0)
        grid.addWidget(unblank, row, 1)
        row += 1
        grid.addWidget(restart, row, 0)
        grid.addWidget(close, row, 1)
        row += 1
        grid.addWidget(stop, row, 0)
        grid.addWidget(resume, row, 1)
        self.connect(ppt_btn, QtCore.SIGNAL('clicked()'), self.openClick)
        self.connect(ppt_dlg_btn, QtCore.SIGNAL('clicked()'), self.openDialog)
        self.connect(slide_btn, QtCore.SIGNAL('clicked()'), self.gotoClick)
        self.connect(prev, QtCore.SIGNAL('clicked()'), self.prevClick)
        self.connect(next, QtCore.SIGNAL('clicked()'), self.nextClick)
        self.connect(blank, QtCore.SIGNAL('clicked()'), self.blankClick)
        self.connect(unblank, QtCore.SIGNAL('clicked()'), self.unblankClick)
        self.connect(restart, QtCore.SIGNAL('clicked()'), self.restartClick)
        self.connect(close, QtCore.SIGNAL('clicked()'), self.closeClick)
        self.connect(stop, QtCore.SIGNAL('clicked()'), self.stopClick)
        self.connect(resume, QtCore.SIGNAL('clicked()'), self.resumeClick)
        self.setLayout(grid)
        self.resize(300, 150)

    def prevClick(self):
        if self.pptid < 0:
            return
        self.pptdll.PrevStep(self.pptid)
        self.updateCurrSlide()
        app.processEvents()

    def nextClick(self):
        if self.pptid < 0:
            return
        self.pptdll.NextStep(self.pptid)
        self.updateCurrSlide()
        app.processEvents()

    def blankClick(self):
        if self.pptid < 0:
            return
        self.pptdll.Blank(self.pptid)
        app.processEvents()

    def unblankClick(self):
        if self.pptid < 0:
            return
        self.pptdll.Unblank(self.pptid)
        app.processEvents()

    def restartClick(self):
        if self.pptid < 0:
            return
        self.pptdll.RestartShow(self.pptid)
        self.updateCurrSlide()
        app.processEvents()

    def stopClick(self):
        if self.pptid < 0:
            return
        self.pptdll.Stop(self.pptid)
        app.processEvents()

    def resumeClick(self):
        if self.pptid < 0:
            return
        self.pptdll.Resume(self.pptid)
        app.processEvents()

    def closeClick(self):
        if self.pptid < 0:
            return
        self.pptdll.ClosePPT(self.pptid)
        self.pptid = -1
        app.processEvents()

    def openClick(self):
        oldid = self.pptid
        rect = RECT(int(self.xEdit.text()), int(self.yEdit.text()),
                    int(self.widthEdit.text()), int(self.heightEdit.text()))
        filename = str(self.pptEdit.text().replace('/', '\\'))
        folder = str(self.folderEdit.text().replace('/', '\\'))
        print(filename, folder)
        self.pptid = self.pptdll.OpenPPT(filename, None, rect, folder)
        print('id: ' + str(self.pptid))
        if oldid >= 0:
            self.pptdll.ClosePPT(oldid)
        slides = self.pptdll.GetSlideCount(self.pptid)
        print('slidecount: ' + str(slides))
        self.total.setNum(self.pptdll.GetSlideCount(self.pptid))
        self.updateCurrSlide()

    def updateCurrSlide(self):
        if self.pptid < 0:
            return
        slide = str(self.pptdll.GetCurrentSlide(self.pptid))
        print('currslide: ' + slide)
        self.slideEdit.setText(slide)
        app.processEvents()

    def gotoClick(self):
        if self.pptid < 0:
            return
        print(self.slideEdit.text())
        self.pptdll.GotoSlide(self.pptid, int(self.slideEdit.text()))
        self.updateCurrSlide()
        app.processEvents()

    def openDialog(self):
        self.pptEdit.setText(QtGui.QFileDialog.getOpenFileName(self, 'Open file'))

if __name__ == '__main__':
    pptdll = cdll.LoadLibrary(r'pptviewlib.dll')
    pptdll.SetDebug(1)
    print('Begin...')
    app = QtGui.QApplication(sys.argv)
    window = PPTViewer()
    window.pptdll = pptdll
    window.show()
    sys.exit(app.exec_())
