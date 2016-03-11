# -*- coding: utf-8 -*-
# ================================
# name: 2048.py
# version: 1.0.2
# coder: Frost Ming
# email: mianghong@gmail.com
# ================================
import wx
import os
import random


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def invert(matrix):
    return [row[::-1] for row in matrix]


class Frame(wx.Frame):
    def __init__(self, title, size=4, win=2048):
        super(Frame, self).__init__(None, -1, title,
                                    style=wx.DEFAULT_FRAME_STYLE ^ wx.MAXIMIZE_BOX ^ wx.RESIZE_BORDER)
        self.colors = {0: (204, 192, 179),
                       2: (238, 228, 218),
                       4: (237, 224, 200),
                       8: (242, 177, 121),
                       16: (245, 149, 99),
                       32: (246, 124, 95),
                       64: (246, 94, 59),
                       128: (237, 207, 114),
                       256: (237, 207, 114),
                       512: (237, 207, 114),
                       1024: (237, 207, 114),
                       2048: (237, 207, 114),
                       4096: (237, 207, 114),
                       8192: (237, 207, 114)}
        self.size = size
        self.win = win
        self.setIcon()
        self.initGame()
        panel = wx.Panel(self)
        panel.Bind(wx.EVT_KEY_UP, self.onKeyDown)
        panel.SetFocus()
        self.initBuffer()
        self.Bind(wx.EVT_SIZE, self.onSize)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.SetClientSize((505, 720))
        self.Center()
        self.Show()

    def onPaint(self, event):
        dc = wx.BufferedPaintDC(self, self.buffer)

    def onClose(self, event):
        self.saveScore()
        self.Destroy()

    def setIcon(self):
        icon = wx.Icon("2048.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

    def loadScore(self):
        if os.path.exists("bestscore.ini"):
            ff = open("bestscore.ini")
            self.bstScore = ff.read()
            ff.close()

    def saveScore(self):
        ff = open("bestscore.ini", "w")
        ff.write(str(self.bstScore))
        ff.close()

    def initGame(self):
        self.bgFont = wx.Font(50, wx.SWISS, wx.NORMAL, wx.BOLD, face=u"Roboto")
        self.scFont = wx.Font(36, wx.SWISS, wx.NORMAL, wx.BOLD, face=u"Roboto")
        self.smFont = wx.Font(
            12, wx.SWISS, wx.NORMAL, wx.NORMAL, face=u"Roboto")
        self.curScore = 0
        self.bstScore = 0
        self.changeScore = False
        self.loadScore()
        self.data = [[0] * self.size for i in range(self.size)]
        self.putTile()
        self.putTile()

    def initBuffer(self):
        w, h = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(w, h)

    def onSize(self, event):
        self.initBuffer()
        self.drawAll()

    def putTile(self):
        new_element = 2 if random.randrange(100) < 89 else 4
        x, y = random.choice([(i, j) for i in range(self.size)
                              for j in range(self.size) if self.data[i][j] == 0])
        self.data[x][y] = new_element

    def isGameOver(self):
        return not any(self.isMoveable(direction) for direction in
                       [wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_UP, wx.WXK_DOWN])

    def isWin(self):
        return any(self.data[i][j] >= self.win for i in range(self.size) for j in range(self.size))

    def doMove(self, direction):
        def move_left(row):
            def tighten(row):
                new_row = [i for i in row if i != 0]
                new_row += [0] * (len(row) - len(new_row))
                return new_row

            def merge(row):
                new_row = []
                i = 0
                while i < len(row) and row[i]:
                    if i < len(row) - 1 and row[i] == row[i + 1]:
                        new_row.append(2 * row[i])
                        self.curScore += 2 * row[i]
                        self.changeScore = True
                        i += 2
                    else:
                        new_row.append(row[i])
                        i += 1
                new_row += [0] * (len(row) - len(new_row))
                return new_row

            return merge(tighten(row))

        moves = dict()
        moves[wx.WXK_LEFT] = lambda matrix: [move_left(row) for row in matrix]
        moves[wx.WXK_RIGHT] = lambda matrix: invert(
            moves[wx.WXK_LEFT](invert(matrix)))
        moves[wx.WXK_UP] = lambda matrix: transpose(
            moves[wx.WXK_LEFT](transpose(matrix)))
        moves[wx.WXK_DOWN] = lambda matrix: transpose(
            moves[wx.WXK_RIGHT](transpose(matrix)))

        if direction in moves:
            if self.isMoveable(direction):
                self.data = moves[direction](self.data)
                return True
            else:
                return False

    def isMoveable(self, direction):
        def row_is_left_moveable(row):
            def change(i):
                if row[i] == 0 and row[i + 1] != 0:
                    return True
                if row[i] and row[i] == row[i + 1]:
                    return True
                return False
            return any(change(i) for i in range(len(row) - 1))

        check = dict()
        check[wx.WXK_LEFT] = lambda matrix: any(
            row_is_left_moveable(row) for row in matrix)
        check[wx.WXK_RIGHT] = lambda matrix: check[wx.WXK_LEFT](invert(matrix))
        check[wx.WXK_UP] = lambda matrix: check[wx.WXK_LEFT](transpose(matrix))
        check[wx.WXK_DOWN] = lambda matrix: check[
            wx.WXK_RIGHT](transpose(matrix))

        if direction in check:
            return check[direction](self.data)
        else:
            return False

    def onKeyDown(self, event):
        keyCode = event.GetKeyCode()
        if self.doMove(keyCode):
            self.putTile()
            self.drawChange()
            if self.isGameOver():
                if wx.MessageBox(u"GAME OVER, restart?", u"Oops!",
                                 wx.YES_NO | wx.ICON_INFORMATION) == wx.YES:
                    bstScore = self.bstScore
                    self.initGame()
                    self.bstScore = bstScore
                    self.drawAll()
            if self.isWin():
                if wx.MessageBox(u"YOU WIN!, restart?", u"Congratulations!",
                                 wx.YES_NO | wx.ICON_INFORMATION) == wx.YES:
                    bstScore = self.bstScore
                    self.initGame()
                    self.bstScore = bstScore
                    self.drawAll()

    def drawBg(self, dc):
        dc.SetBackground(wx.Brush((250, 248, 239)))
        dc.Clear()
        dc.SetBrush(wx.Brush((187, 173, 160)))
        dc.SetPen(wx.Pen((187, 173, 160)))
        dc.DrawRoundedRectangle(15, 150, 475, 475, 5)

    def drawLogo(self, dc):
        dc.SetFont(self.bgFont)
        dc.SetTextForeground((119, 110, 101))
        dc.DrawText(u"2048", 15, 26)

    def drawLabel(self, dc):
        dc.SetFont(self.smFont)
        dc.SetTextForeground((119, 110, 101))
        dc.DrawText(u"Merge tiles to get 2048!", 15, 114)
        dc.DrawText(u"Hint: \nPress up, down, left, right to move tiles. \
                \nTiles will merge into one when they are equal", 15, 639)

    def drawScore(self, dc):
        dc.SetFont(self.smFont)
        scoreLabelSize = dc.GetTextExtent(u"SCORE")
        bestLabelSize = dc.GetTextExtent(u"BEST")
        curScoreBoardMinW = 15 * 2 + scoreLabelSize[0]
        bstScoreBoardMinW = 15 * 2 + bestLabelSize[0]
        curScoreSize = dc.GetTextExtent(str(self.curScore))
        bstScoreSize = dc.GetTextExtent(str(self.bstScore))
        curScoreBoardNedW = 10 + curScoreSize[0]
        bstScoreBoardNedW = 10 + bstScoreSize[0]
        curScoreBoardW = max(curScoreBoardMinW, curScoreBoardNedW)
        bstScoreBoardW = max(bstScoreBoardMinW, bstScoreBoardNedW)
        dc.SetBrush(wx.Brush((187, 173, 160)))
        dc.SetPen(wx.Pen((187, 173, 160)))
        dc.DrawRoundedRectangle(
            505 - 15 - bstScoreBoardW, 40, bstScoreBoardW, 50, 3)
        dc.DrawRoundedRectangle(
            505 - 15 - bstScoreBoardW - 5 - curScoreBoardW, 40, curScoreBoardW, 50, 3)
        dc.SetTextForeground((238, 228, 218))
        dc.DrawText(u"BEST", 505 - 15 - bstScoreBoardW +
                    (bstScoreBoardW - bestLabelSize[0]) / 2, 48)
        dc.DrawText(u"SCORE", 505 - 15 - bstScoreBoardW - 5 - curScoreBoardW + (curScoreBoardW - scoreLabelSize[0]) / 2,
                    48)
        dc.SetTextForeground((255, 255, 255))
        dc.DrawText(str(self.bstScore), 505 - 15 -
                    bstScoreBoardW + (bstScoreBoardW - bstScoreSize[0]) / 2, 68)
        dc.DrawText(str(self.curScore),
                    505 - 15 - bstScoreBoardW - 5 - curScoreBoardW + (curScoreBoardW - curScoreSize[0]) / 2, 68)

    def drawTiles(self, dc):
        for row in range(self.size):
            for col in range(self.size):
                value = self.data[row][col]
                color = self.colors[value]
                if value == 2 or value == 4:
                    dc.SetTextForeground((119, 110, 101))
                else:
                    dc.SetTextForeground((255, 255, 255))
                dc.SetBrush(wx.Brush(color))
                dc.SetPen(wx.Pen(color))
                dc.DrawRoundedRectangle(
                    30 + col * 115, 165 + row * 115, 100, 100, 2)
                sc_font = self.scFont
                dc.SetFont(sc_font)
                size = dc.GetTextExtent(str(value))
                while size[0] > 100 - 15 * 2:
                    sc_font = wx.Font(sc_font.GetPointSize() * 4 / 5, wx.SWISS, wx.NORMAL, wx.BOLD,
                                      face=u"Roboto")
                    dc.SetFont(sc_font)
                    size = dc.GetTextExtent(str(value))
                if value != 0:
                    dc.DrawText(str(value), 30 + col * 115 + (100 - size[0]) / 2,
                                165 + row * 115 + (100 - size[1]) / 2)

    def drawAll(self):
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        self.drawBg(dc)
        self.drawLogo(dc)
        self.drawLabel(dc)
        self.drawScore(dc)
        self.drawTiles(dc)

    def drawChange(self):
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        if self.curScore > self.bstScore:
            self.bstScore = self.curScore
        if self.changeScore:
            self.drawScore(dc)
        self.drawTiles(dc)


if __name__ == "__main__":
    app = wx.App()
    Frame(u"2048 v1.0.2 by Frost Ming")
    app.MainLoop()
