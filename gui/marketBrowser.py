#===============================================================================
# Copyright (C) 2010 Diego Duclos
#
# This file is part of pyfa.
#
# pyfa is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyfa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with pyfa.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

import wx
import controller
import bitmapLoader

class MarketBrowser(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.splitter = wx.SplitterWindow(self, style = wx.SP_LIVE_UPDATE)

        vbox.Add(self.splitter, 1, wx.EXPAND)
        self.SetSizer(vbox)

        self.marketView = wx.TreeCtrl(self.splitter)
        self.itemView = wx.ListView(self.splitter)

        treeStyle = self.marketView.GetWindowStyleFlag()
        treeStyle |= wx.TR_HIDE_ROOT
        self.marketView.SetWindowStyleFlag(treeStyle)

        listStyle = self.itemView.GetWindowStyleFlag()
        listStyle |= wx.LC_REPORT | wx.LC_NO_HEADER | wx.LC_SINGLE_SEL | wx.LC_ICON
        self.itemView.SetWindowStyleFlag(listStyle)
        self.itemView.InsertColumn(0, "Name")

        self.splitter.SplitHorizontally(self.marketView, self.itemView)
        self.splitter.SetMinimumPaneSize(10)

        self.marketRoot = self.marketView.AddRoot("Market")

        self.marketImageList = wx.ImageList(16, 16)
        self.marketView.SetImageList(self.marketImageList)

        self.itemImageList = wx.ImageList(16, 16)
        self.itemView.SetImageList(self.itemImageList, wx.IMAGE_LIST_NORMAL)

        cMarket = controller.Market.getInstance()

        root = cMarket.getMarketRoot()
        for id, name, iconFile in root:
            if iconFile: iconId = self.marketImageList.Add(bitmapLoader.getBitmap(iconFile, "pack"))
            else: iconId = -1
            childId = self.marketView.AppendItem(self.marketRoot, name, iconId, data=wx.TreeItemData(id))
            self.marketView.AppendItem(childId, "dummy")

        self.marketView.SortChildren(self.marketRoot)

        #Bind our lookup method to when the tree gets expanded
        self.marketView.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.expandLookup)
        self.marketView.Bind(wx.EVT_TREE_SEL_CHANGED, self.selectionMade)

    def expandLookup(self, event):
        root = event.Item
        child, cookie = self.marketView.GetFirstChild(root)
        if self.marketView.GetItemText(child) == "dummy":
            cMarket = controller.Market.getInstance()
            #A DUMMY! Keeeel!!! EBUL DUMMY MUST DIAF!
            self.marketView.Delete(child)

            #Add 'real stoof!' instead
            for id, name, iconFile, more in cMarket.getChildren(self.marketView.GetPyData(root)):
                if iconFile: iconId = self.marketImageList.Add(bitmapLoader.getBitmap(iconFile, "pack"))
                else: iconId = -1
                childId = self.marketView.AppendItem(root, name, iconId, data=wx.TreeItemData(id))
                if more:
                    self.marketView.AppendItem(childId, "dummy")

            self.marketView.SortChildren(root)


    def selectionMade(self, event):
        self.itemView.DeleteAllItems()
        self.itemImageList.RemoveAll()

        root = event.Item
        if self.marketView.GetChildrenCount(root) != 0:
            return

        cMarket = controller.Market.getInstance()
        idNameMap = {}
        for id, name, iconFile in cMarket.getItems(self.marketView.GetPyData(root)):
            item = wx.ListItem()
            if iconFile: iconId = self.itemImageList.Add(bitmapLoader.getBitmap(iconFile, "pack"))
            else: iconId = -1
            item.SetImage(iconId)
            item.SetText(name)
            item.SetData(id)
            idNameMap[id] = name
            self.itemView.InsertItem(item)


        self.itemView.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.itemView.SortItems(lambda id1, id2: cmp(idNameMap[id1], idNameMap[id2]))
