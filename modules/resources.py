import sqlite3
import requests

from logging import getLogger

import datetime

class Resources:
    
    resources = {}
    
    def __init__(self, db=None, cache_timeout=-1):
        self.logger = getLogger(__name__)
        self.s = requests.Session()
        self._db = db
        self.cache_timeout = cache_timeout

    def get(self, uri):
        # Disabling this for the time being.  IE, destroy self.resources
        # Is the original idea necessary?  Is it potentially too memory intensive?
        self.resources = {}
        
        if uri in self.resources:
            now = datetime.datetime.now()
            if now > self.resources[uri]["cacheTimeout"]:
                del self.resources[uri]

        if uri not in self.resources:
            # Default decision to fetch the resource
            fetch_new = True
            # Not in DB until proven otherwise
            found_in_db = False
            
            # Do we have a DB connection and a valid timeout?
            # This allows us to operate without a db
            if self._db is not None and self.cache_timeout != -1:
                #sql_query = "SELECT * FROM resources WHERE uri = ?"
                #values = (uri,)
                #resource = self._db.query(sql_query, values)
                
                sql_query = "SELECT * FROM resources WHERE uri = '" + uri + "';"
                rows = self._db.query(sql_query)
                if rows != None:
                    # This URI was found in the DB, but is it too old?
                    self.logger.info("Found URI in cache db: {}".format(uri))
                    found_in_db = True
                    now = datetime.datetime.now()
                    
                    # This is fast by the smallest of margins than the below, commented out section.
                    cacheTimeout = datetime.datetime.strptime( rows[0][1], "%Y-%m-%d %H:%M:%S.%f" )
                    if cacheTimeout > now:
                        # It is not too old.  We'll use this one.
                        self.logger.info("Using cached version: {}".format(uri))
                        fetch_new = False
                        now_plus = now + datetime.timedelta(seconds = self.cache_timeout)
                        self.resources[uri] = {}
                        self.resources[uri]["n3"] = rows[0][3]
                        self.resources[uri]["cacheTimeout"] = now_plus
                    else:
                        self.logger.info("URI expired: {}".format(uri))
                    
                    '''
                    sql_query = "SELECT * FROM resources WHERE uri = ? AND cacheTimeout > ?;"
                    values = (uri, now)
                    resource = self._db.query(sql_query, values)
                    
                    if resource != None:
                        # It is not too old.  We'll use this one.
                        self.logger.info("Using cached version: {}".format(uri))
                        fetch_new = False
                        now_plus = now + datetime.timedelta(seconds = self.cache_timeout)
                        self.resources[uri] = {}
                        self.resources[uri]["n3"] = resource[0][3]
                        self.resources[uri]["cacheTimeout"] = now_plus
                    else:
                        self.logger.info("URI expired: {}".format(uri))
                    '''
            
            if fetch_new:
                self.logger.info("Fetching original resource for URI: {}".format(uri))
                
                now = datetime.datetime.now()
                now_plus = now + datetime.timedelta(seconds = self.cache_timeout)
                    
                r = self.s.get(uri)
                self.resources[uri] = {}
                self.resources[uri]["n3"] = r.content
                self.resources[uri]["cacheTimeout"] = now_plus
                # Have fetched the resource from its source.  Cache it?
                
                if self._db is not None and self.cache_timeout > -1:
                    # Yes.  Valid DB connection and valid timeout setting
                    if found_in_db:
                        # Already exists, so we want to update it.
                        sql_query = "UPDATE resources SET cacheTimeout=?, resource=? WHERE uri=?"
                        values = (now_plus, sqlite3.Binary(self.resources[uri]["n3"]), uri)
                        dbid = self._db.update(sql_query, values)
                    else:
                        # It's new.
                        sql_query = "INSERT INTO resources (cacheTimeout, uri, resource) VALUES (?, ?, ?)"
                        values = (now_plus, uri, sqlite3.Binary(self.resources[uri]["n3"]) )
                        dbid = self._db.update(sql_query, values)

        return self.resources[uri]["n3"]