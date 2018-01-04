import os
import sys
import yaml
import json
import datetime

import requests

import sqlite3
from flask import g

from flask import Flask
from flask import request
from flask import Response, redirect

import logging
import logging.config
from logging import getLogger

sys.path.append(os.path.abspath('..'))

from modules.db import DB
from modules.service import Service

app = Flask(__name__)
config = None

@app.route("/db/init")
def init_db():
    with app.app_context():
        db = DB(app, config["sqlite"]["db"])
        if db.init_db(config["sqlite"]["schema"]):
            return ('Database Created/Reset', 200)    
        else:
            return ("Something went horribly wrong", 500)


@app.route("/db/resources")
def etags():
    with app.app_context():
        db = DB(app, config["sqlite"]["db"])
        results = db.resources()
        if results != None:
            output = "id        cacheTimeout       uri\n"
            for i in results:
                output += str(i[0]) + "     " + i[1] + "        " + i[2] + "\n"
            response = Response(output)
            response.headers['Content-type'] = "text/plain"
            return (response, 200)
        else:
            return ("Results was None?", 500)
            

@app.route("/db/clearexpired")
def clearexpired():
    with app.app_context():
        db = DB(app, config["sqlite"]["db"])
        
        sql_query = "DELETE FROM resources WHERE ? > cacheTimeout"
        values = (datetime.datetime.now(),)
        numrows = db.update(sql_query, values)
        if numrows != None:
            output = "Expired resources deleted: " + str(numrows)
            response = Response(output)
            response.headers['Content-type'] = "text/plain"
            return (response, 200)
        else:
            return ("Results was None?", 500)


@app.route("/ldpath/program", methods=['GET', 'POST'])
def run_ldpath_program():
    uri = request.args.get('uri')
    ldprogram = request.get_data()
    with app.app_context():
        service = Service(app, config)
        
        output_raw = service.run_ldpath_program(uri, ldprogram)
        output = json.dumps(output_raw, sort_keys=True, indent=4)
        
        response = Response(output)
        response.headers['Content-type'] = "application/json"
        return (response, 200)




def load_app(configpath):
    global config
    config = yaml.safe_load(open(configpath))
    
    if not config["sqlite"]["db"].startswith('/'):
        config["sqlite"]["db"] = config["app_base_path"] + config["sqlite"]["db"]
        
    if not config["sqlite"]["schema"].startswith('/'):
        config["sqlite"]["schema"] = config["app_base_path"] + config["sqlite"]["schema"]
        
    logging.config.dictConfig(config["logging"])
    logging.info('Started')
    logger = getLogger(__name__)

    logger.info("Application loaded using config: {}".format(config))
    return app


if __name__ == "__main__":
    from modules.config_parser import args
    config = yaml.safe_load(open(args.config))
    
    if not config["sqlite"]["db"].startswith('/'):
        config["sqlite"]["db"] = config["app_base_path"] + config["sqlite"]["db"]
        
    if not config["sqlite"]["schema"].startswith('/'):
        config["sqlite"]["schema"] = config["app_base_path"] + config["sqlite"]["schema"]
        
    logging.config.dictConfig(config["logging"])
    logging.info('Started')
    logger = getLogger(__name__)

    logger.info("Application loaded using config: {}".format(config))
    app.run(debug=True, host="0.0.0.0", port=8000)

