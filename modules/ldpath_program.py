import os 
import sys
import json
import datetime
import re

from antlr4 import *
from rdflib import Variable
from rdflib.graph import Graph, URIRef

from modules.ldprogram.LDPathProgramLexer import LDPathProgramLexer
from modules.ldprogram.LDPathProgramParser import LDPathProgramParser
from modules.ldprogram.LDPathProgramListenerLDPathy import LDPathProgramListener

from modules.resources import Resources 

from logging import getLogger

class LDPathProgram:
    
    graph = {}
    
    raw = {}
    parsed = {}
    
    response = {}
    
    def __init__(self, db=None, cache_timeout=-1):
        self._db = db
        self.cache_timeout = cache_timeout
        self.logger = getLogger(__name__)
    
    def run(self, uri):

        self.resources = Resources(self._db, self.cache_timeout)
        base_resource = self.resources.get(uri)
        
        self.graph = Graph()
        self.graph.parse(data=base_resource, format="n3")
        
        self._build_graph(uri, self.parsed["expressions"])
        
        sparql_prefixes = []
        for k in self.parsed["prefixes"]:
            p = self.parsed["prefixes"][k]
            prefix_str = 'PREFIX {}: <{}>'.format(p["prefix"], p["iri"])
            sparql_prefixes.append(prefix_str)
        
        sparql_prefix_str = '\n'.join(sparql_prefixes)
        
        depth = 0
        self.logger.debug("Building queries (includes querying the graph, i.e. collecting the values)")
        self._build_query(uri, depth, self.parsed["expressions"], "")
        
        self.logger.debug("Parsing response")
        self._build_response(self.parsed["expressions"], "", "")
            
        # print(json.dumps(self.response, sort_keys=True, indent=4))
            
        pass
        
    def load(self, ldpath_program_loc):
        self.loc = ldpath_program_loc
        if self.loc.startswith('http'):
            r = requests.get(self.loc)
            if r.status_code == 200:
                # Might have to worry about encoding in the future?
                self.raw = r.content
            else:
                print("Unable to load LDPATH program via HTTP.")
                print("Status was: " + str(r.status_code))
        else:
            # Assume it is on the file system.
            # Note that Filestream Fetches the Program with 'rb'
            self.raw = FileStream(self.loc)
    
    def parse(self):
        lexer = LDPathProgramLexer(self.raw)
        stream = CommonTokenStream(lexer)
        parser = LDPathProgramParser(stream)
        tree = parser.program()
    
        listener = LDPathProgramListener()
        walker = ParseTreeWalker()
        walker.walk(listener, tree)
    
        # print(json.dumps(listener.output, sort_keys=True, indent=4))
        self.parsed = listener.output


    def _build_response(self, expressions, returnval, datatype):
        for e in expressions:
            if 'returnVal' in e:
                returnval = e["returnVal"]
            if 'datatype' in e:
                if e["datatype"] == "xsd:string":
                    datatype = "literal"
            
            answers = []
            if 'function' in e and e["function"] != "":
                if e["function"] == "fn:concat":
                    parts = []

                    for e1 in e["then"]:
                        if e1["quotedtext"] != "":
                            parts.append({ "type": "quotedtext", "value": e1["quotedtext"]})
                        else:
                            parts.append({ "type": "qname", "value": e1["qname"].replace(':', '')})
                    
                    strings = []
                    for v in e["values"]:
                        vdict = v.asdict()
                        j = []
                        for p in parts:
                            if p["type"] == "qname" and p["value"] in vdict:
                                j.append(vdict[p["value"]])
                            elif p["type"] == "qname":
                                j.append('')
                            else:
                                j.append(p["value"])
                        strings.append(''.join(j))
                    
                    for s in strings:
                        a = {
                            "type": datatype,
                            "value": s
                        }
                        answers.append(a)
                    self.response[returnval] = answers
            elif 'query' in e:
                for v in e["values"]:
                    a = {
                        "type": datatype,
                        "value": v[0]
                    }
                    answers.append(a)
                self.response[returnval] = answers
            elif len(e["then"]) > 0:
                self._build_response(e["then"], returnval, datatype)


    def _build_query(self, s, depth, expressions, stmt):
        for e in expressions:
            
            if len(e["then"]) > 0 and e["qname_expanded"] == "":
                # qname_expanded is null, but there is depth here.
                # Probably a function.
                
                variables = set()
                stmts = []
                for e1 in e["then"]:
                    if e1["qname_expanded"] != "":
                        
                        new_stmt = "OPTIONAL { %S% <%P%> %O% . } ."
                
                        if s.startswith('?'):
                            new_stmt = new_stmt.replace('%S%', s)
                            variables.add(s)
                        else:
                            new_stmt = new_stmt.replace('%S%', '<' + s + '>')
                
                        new_stmt = new_stmt.replace('%P%', e1["qname_expanded"])
                        
                        new_stmt = new_stmt.replace('%O%', '?' + e1["qname"].replace(':', '') )
                        variables.add('?' + e1["qname"].replace(':', ''))
            
                        stmts.append(new_stmt)
                
                query = """
                        SELECT %VARS%
                            WHERE {
                            %STMTS%
                            %FILTERS%
                        }
                    """
                query = query.replace('%VARS%', ' '.join(variables))
                query = query.replace('%STMTS%', stmt + "\n".join(stmts))
                    
                if 'filters' not in e or len(e["filters"]) == 0:
                    query = query.replace('%FILTERS%', '')
                
                e["query"] = query
                values = self.graph.query(query)
                e["values"] = values
            
            elif e["qname_expanded"] != "":
            
                new_stmt = "%S% <%P%> %O% ."
                
                if s.startswith('?'):
                    new_stmt = new_stmt.replace('%S%', s)
                else:
                    new_stmt = new_stmt.replace('%S%', '<' + s + '>')
                
                new_stmt = new_stmt.replace('%P%', e["qname_expanded"])
            
                if len(e["then"]) == 0:
                    new_stmt = new_stmt.replace('%O%', '?o')
                    query = """
                        SELECT ?o
                            WHERE {
                            %STMTS%
                            %FILTERS%
                        }
                    """
                    query = query.replace('%STMTS%', stmt + new_stmt)
                    
                    if 'filters' not in e or len(e["filters"]) == 0:
                        query = query.replace('%FILTERS%', '')
                    
                    e["query"] = query
                    values = self.graph.query(query)
                    e["values"] = values
                        
                else:
                    new_depth = depth + 1
                    new_s = '?t' + str(new_depth)
                    
                    new_stmt = new_stmt.replace('%O%', new_s)
                    
                    self._build_query(new_s, new_depth, e["then"], stmt + new_stmt)


    def _build_graph(self, uri, expressions):
        relations = []
        for e in expressions:
            if len(e["then"]) > 0:
                relations.append(e["qname_expanded"])
        
        if len(relations) > 0:
            uris = set()
            for r in relations:
                for o in self.graph.objects(URIRef(uri), URIRef(r)):
                    uris.add(o)

            for u in uris:
                r = self.resources.get(u)
                self.graph.parse(data=r, format="n3")
                self._build_graph(u, e["then"])
        
        return 