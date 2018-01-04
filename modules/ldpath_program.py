import os 
import sys
import json
import datetime
import re

from antlr4 import *
from rdflib import Variable
from rdflib.graph import Graph, URIRef
from rdflib.plugins.sparql import prepareQuery

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
    
    preparedQueries = {
        "depth0_basic": prepareQuery("SELECT ?o WHERE { ?s ?p ?o . }"),
        "depth1_basic": prepareQuery("SELECT ?o WHERE { ?s ?p ?t1 .?t1 ?p2 ?o . }"),
        "depth1_optional": prepareQuery("SELECT ?t1 ?o1 ?o2 WHERE { ?s ?p ?t1 . OPTIONAL { ?t1 ?possible_p1 ?o1 .} . OPTIONAL { ?t1 ?possible_p2 ?o2 .} . }"),
    }
        
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
        
        #for i in self.preparedQueries:
        #    self.preparedQueries[i] = self.preparedQueries[i].replace('%PREFIX%', sparql_prefix_str)
        #    print(self.preparedQueries[i])
        
        depth = 0
        self.logger.debug("Building queries (includes querying the graph, i.e. collecting the values)")
        self._build_query(uri, depth, self.parsed["expressions"], {})
        
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


    def _build_query(self, s, depth, expressions, bindings):
        
        for e in expressions:
            
            # These are common to all queries.
            if depth == 0:
                bindings["s"] = URIRef(s)
            if depth == 0 and e["qname_expanded"] != "":
                bindings["p"] = URIRef(e["qname_expanded"])
            if depth == 1 and e["qname_expanded"] != "":
                bindings["p2"] = URIRef(e["qname_expanded"])
            
            if e["qname"] == ".":
                '''
                    Example:
                    {
                        "datatype": "xsd:string",
                        "filters": [],
                        "function": "",
                        "langtag_filter": "",
                        "qname": ".",
                        "qname_expanded": "",
                        "quotedtext": "",
                        "returnVal": "uri",
                        "then": []
                    },
                '''
                e["query"] = "."
                e["values"] = [[s]]
            elif len(e["then"]) == 0 and e["qname_expanded"] != "":
                
                if depth == 0:
                    '''
                    Depth is 0 (top) and there are no sub selects.
                    The most basic query.
                    These all should have a valid qname_expanded entry, yes?
                    Example:
                        {
                            "datatype": "xsd:string",
                            "function": "",
                            "langtag_filter": "",
                            "qname": "aic:objectTerm",
                            "qname_expanded": "http://definitions.artic.edu/ontology/1.0/objectTerm",
                            "quotedtext": "",
                            "returnVal": "objectTerm_uri",
                            "then": []
                        },
                    '''
                    q = self.preparedQueries["depth0_basic"]
                elif depth == 1:
                    '''
                    Example:
                        {
                            "datatype": "xsd:string",
                            "function": "",
                            "langtag_filter": "",
                            "qname": "aic:objectTerm",
                            "qname_expanded": "http://definitions.artic.edu/ontology/1.0/objectTerm",
                            "quotedtext": "",
                            "returnVal": "objectTerm_uid",
                            "then": [
                                {
                                    "function": "",
                                    "langtag_filter": "",
                                    "qname": "aic:uid",
                                    "qname_expanded": "http://definitions.artic.edu/ontology/1.0/uid",
                                    "quotedtext": "",
                                    "then": []
                                }
                            ]
                        },
                    '''
                    q = self.preparedQueries["depth1_basic"]
                
                e["query"] = q._original_args[0]
                values = self.graph.query(q, initBindings=bindings)
                e["values"] = values
            
            elif len(e["then"]) > 0 and e["qname_expanded"] == "":
                # qname_expanded is null, but there is depth here.
                # Probably a function.
                '''
                    Example:
                    {
                        "datatype": "xsd:string",
                        "function": "",
                        "langtag_filter": "",
                        "qname": "aic:objectTitle",
                        "qname_expanded": "http://definitions.artic.edu/ontology/1.0/objectTitle",
                        "quotedtext": "",
                        "returnVal": "objectTitle",
                        "then": [
                            {
                                "function": "fn:concat",
                                "langtag_filter": "",
                                "qname": "fn:concat(skos:prefLabel,\" (\",aic:languageText,\")\")",
                                "qname_expanded": "",
                                "quotedtext": "",
                                "then": [
                                    {
                                        "function": "",
                                        "langtag_filter": "",
                                        "qname": "skos:prefLabel",
                                        "qname_expanded": "http://www.w3.org/2004/02/skos/core#prefLabel",
                                        "quotedtext": "",
                                        "then": []
                                    },
                                    {
                                        "function": "",
                                        "langtag_filter": "",
                                        "qname": "",
                                        "qname_expanded": "",
                                        "quotedtext": "\" (\"",
                                        "then": []
                                    },
                                    {
                                        "function": "",
                                        "langtag_filter": "",
                                        "qname": "aic:languageText",
                                        "qname_expanded": "http://definitions.artic.edu/ontology/1.0/languageText",
                                        "quotedtext": "",
                                        "then": []
                                    },
                                    {
                                        "function": "",
                                        "langtag_filter": "",
                                        "qname": "",
                                        "qname_expanded": "",
                                        "quotedtext": "\")\"",
                                        "then": []
                                    }
                                ]
                            }
                        ]
                    },
                '''
                
                count = 1
                for e1 in e["then"]:
                    if e1["qname_expanded"] != "":
                        bindings["possible_p" + str(count)] = e1["qname_expanded"]
                        bindings["o" + str(count)] = e1["qname"].replace(':', '')
                        count += 1
                
                q = self.preparedQueries["depth1_optional"]
                
                e["query"] = q._original_args[0]
                values = self.graph.query(q, initBindings=bindings)
                e["values"] = values
            
            else:
                new_depth = depth + 1
                self._build_query(s, new_depth, e["then"], bindings)


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