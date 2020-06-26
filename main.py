#!/usr/bin/python3
import logging

import util
from moyubot import MoyuBot

if __name__ == '__main__':
    _level = logging.INFO
    _format = "%(asctime)s - %(message)s"
    _filename = util.absolute_path("moyu.log")
    _filemode = "a"
    logging.basicConfig(level=_level, format=_format,
                        filename=_filename, filemode=_filemode)
    bot: MoyuBot = MoyuBot()
    bot.run()
