import os
import glob
import re
import errno
import requests

from logging import getLogger

from modules.db import DB
from modules.ldpath_program import LDPathProgram

from flask import Response

import codecs
from antlr4.InputStream import InputStream

class Service:
    
    app = None
    config = None
    
    def __init__(self, app, config):
        self.logger = getLogger(__name__)
        self.app = app
        self.config = config
        
        self._db = DB(app, config["sqlite"]["db"])
        
        return

    
    def run_ldpath_program(self, uri, ldprogram_data):
        #See https://github.com/antlr/antlr4/blob/master/runtime/Python3/src/antlr4/FileStream.py#L27
        ldprogram_raw = codecs.decode(ldprogram_data, 'ascii', 'strict')
        
        self.logger.debug("Running ldpath program on uri: {}".format(uri))
        self.logger.debug("Running ldpath program: {}".format(ldprogram_data))
        
        ldprogram = LDPathProgram(self._db, self.config["cache"]["timeout"])
        # This instantiates the InputStream as needed by antlr
        self.logger.debug("Creating InputStream")
        ldprogram.raw = InputStream(ldprogram_raw)
        self.logger.debug("Parsing")
        ldprogram.parse()
        self.logger.debug("Running")
        ldprogram.run(uri)
        
        return ldprogram.response

