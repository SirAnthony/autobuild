# -*- coding: utf-8 -*-
#   unicode formatter

from logging import Formatter


class UnicodeFormatter(Formatter):

    def formatTime(self, record, datefmt=None):
        # Old-style class in python < 2.7
        string = Formatter.formatTime(self, record, datefmt).decode('utf-8')
        return unicode(string)
