# -*- coding: utf-8 -*-

"""Search file contents with tracker."""

import mimetypes
from gi.repository import Gio
import os
import re
import subprocess
from urllib.parse import unquote
from shutil import which
from albertv0 import *

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Tracker"
__version__ = "1.0"
__trigger__ = "tracker "
__author__ = "Florian Kraft"
__dependencies__ = ["tracker"]

if which("tracker") is None:
    raise Exception("'tracker' is not in $PATH.")

def findIconPathByIconNames(iconNames):
    for iconName in iconNames:
        iconPath = iconLookup(iconName)
        if iconPath:
            return iconPath
    return ""

def findIconPathByFileName(fileName):
    iconNames = []
    mimeType, encoding = mimetypes.guess_type(fileName)
    if mimeType:
        icons = Gio.content_type_get_icon(mimeType)
        iconNames = icons.get_names()
    iconNames.append("text-x-generic")
    return findIconPathByIconNames(iconNames)

def getDefaultResultSet():
    return [Item(
                id=__prettyname__,
                icon=appIconPath,
                text=__prettyname__,
                subtext="Enter a search term with at least 3 characters to search for file contents.")]

appIconPath = findIconPathByIconNames(["system-search", "search"])

def handleQuery(query):
    if query.isTriggered:
        strippedQuery = query.string.strip()
        items = []
        if len(strippedQuery) > 2:
            result = subprocess.Popen(['tracker', 'search', '--disable-snippets', '--disable-color', strippedQuery], stdout=subprocess.PIPE)
            for line in result.stdout:
                urlEncodedPath = line.decode().strip()
                if urlEncodedPath.startswith('file://'):
                    clearTextPath = unquote(urlEncodedPath, encoding='utf-8')[7:]
                    fileName = clearTextPath.rsplit('/', 1)[-1]
                    mimeType, encoding = mimetypes.guess_type(fileName)
                    items.append(
                        Item(
                            id=fileName,
                            icon=findIconPathByFileName(fileName),
                            text=fileName,
                            subtext=clearTextPath,
                            actions=[UrlAction("Open", "%s" % urlEncodedPath)]
                        )
                    )
            if not items:
                items.append(
                    Item(
                        id="No results",
                        icon=appIconPath,
                        text="No results",
                        subtext="Your search for \"%s\" did not return any results." % strippedQuery))

        if not items:
            items = getDefaultResultSet()

        return items
