# Generated from LDPathProgram.g4 by ANTLR 4.7.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .LDPathProgramParser import LDPathProgramParser
else:
    from LDPathProgramParser import LDPathProgramParser

# This class defines a complete listener for a parse tree produced by LDPathProgramParser.
class LDPathProgramListener(ParseTreeListener):

    currentFilters = []
    currentExpressions = []
    currentExpression = {}
    currentDepth = -1
    
    def __init__(self):
        self.output = {}
        self.output["prefixes"] = {
            "rdf": { "prefix": "rdf", "iri": "http://www.w3.org/1999/02/22-rdf-syntax-ns#" },
            "rdfs": { "prefix": "rdfs", "iri": "http://www.w3.org/2000/01/rdf-schema#" },
            "owl": { "prefix": "owl", "iri": "http://www.w3.org/2002/07/owl#" },
            "skos": { "prefix": "skos", "iri": "http://www.w3.org/2004/02/skos/core#" },
            "dc": { "prefix": "dc", "iri": "http://purl.org/dc/elements/1.1/" },
            "xsd": { "prefix": "xsd", "iri": "http://www.w3.org/2001/XMLSchema#" },
        }
        self.output["expressions"] = []
        
    # Enter a parse tree produced by LDPathProgramParser#program.
    def enterProgram(self, ctx:LDPathProgramParser.ProgramContext):
        pass

    # Exit a parse tree produced by LDPathProgramParser#program.
    def exitProgram(self, ctx:LDPathProgramParser.ProgramContext):
        pass


    # Enter a parse tree produced by LDPathProgramParser#prologue.
    def enterPrologue(self, ctx:LDPathProgramParser.PrologueContext):
        pass

    # Exit a parse tree produced by LDPathProgramParser#prologue.
    def exitPrologue(self, ctx:LDPathProgramParser.PrologueContext):
        pass


    # Enter a parse tree produced by LDPathProgramParser#prefixDecl.
    def enterPrefixDecl(self, ctx:LDPathProgramParser.PrefixDeclContext):
        prefix = ctx.PNAME_NS().getText().replace(' ' , '')
        prefix = prefix.strip()
        
        iri = ctx.IRI_REF().getText()
        p = {
            "prefix": prefix.replace(':', ''),
            "iri": iri.replace('<', '').replace('>', '')
        }
        if p["prefix"] not in self.output["prefixes"]:
            self.output["prefixes"][p["prefix"]] = p
        pass

    # Exit a parse tree produced by LDPathProgramParser#prefixDecl.
    def exitPrefixDecl(self, ctx:LDPathProgramParser.PrefixDeclContext):
        pass


    # Enter a parse tree produced by LDPathProgramParser#instructions.
    def enterInstructions(self, ctx:LDPathProgramParser.InstructionsContext):
        pass

    # Exit a parse tree produced by LDPathProgramParser#instructions.
    def exitInstructions(self, ctx:LDPathProgramParser.InstructionsContext):
        pass


    # Enter a parse tree produced by LDPathProgramParser#instruction.
    def enterInstruction(self, ctx:LDPathProgramParser.InstructionContext):
        pass

    # Exit a parse tree produced by LDPathProgramParser#instruction.
    def exitInstruction(self, ctx:LDPathProgramParser.InstructionContext):
        self.currentReturnVal = ""
        pass

    # Enter a parse tree produced by LDPathProgramParser#returnVal.
    def enterReturnVal(self, ctx:LDPathProgramParser.ReturnValContext):
        self.currentReturnVal = ctx.getText()
        pass

    # Exit a parse tree produced by LDPathProgramParser#returnVal.
    def exitReturnVal(self, ctx:LDPathProgramParser.ReturnValContext):
        pass

    # Enter a parse tree produced by LDPathProgramParser#queryPath.
    def enterQueryPath(self, ctx:LDPathProgramParser.QueryPathContext):
        # print("Entering queryPath: " + ctx.getText())
        pass

    # Exit a parse tree produced by LDPathProgramParser#queryPath.
    def exitQueryPath(self, ctx:LDPathProgramParser.QueryPathContext):
        # print("Exiting queryPath: " + ctx.getText())
        pass


    # Enter a parse tree produced by LDPathProgramParser#qnameExpr.
    def enterQnameExpr(self, ctx:LDPathProgramParser.QnameExprContext):
        
        
        quotedtext = ""
        if ctx.QUOTEDTEXT() is not None:
            value = ""
            quotedtext = ctx.QUOTEDTEXT().getText()
        elif ctx.PNAME_LN() is not None:
            value = ctx.PNAME_LN().getText()
        else:
            value = ctx.getText()
        
        qname_expanded = ""
        if value != "" and ':' in value:
            qname_parts = value.split(':')
            prefix = qname_parts[0]
            if prefix in self.output["prefixes"]:
                qname_expanded = self.output["prefixes"][prefix]["iri"] + qname_parts[1]
        
        func = ""
        if ctx.FUNC() is not None:
            func = ctx.FUNC().getText()
            
        langtag = ""
        if ctx.LANGTAG() is not None:
            langtag = ctx.LANGTAG().getText()
            
        if self.currentDepth == -1:
            # We are at the beginning/top of an expression.
            self.currentDepth = 0
            e = {
                "returnVal": self.currentReturnVal,
                "qname": value,
                "qname_expanded": qname_expanded,
                "quotedtext": quotedtext,
                "function": func,
                "langtag_filter": langtag,
                "then": []
            }
            self.currentExpression = e
        elif self.currentDepth == 0:
            self.currentDepth = 1
            e = {
                "qname": value,
                "qname_expanded": qname_expanded,
                "quotedtext": quotedtext,
                "function": func,
                "langtag_filter": langtag,
                "then": []
            }
            self.currentExpression["then"].append(e)
        elif self.currentDepth == 1:
            self.currentDepth = 2
            e = {
                "qname": value,
                "qname_expanded": qname_expanded,
                "quotedtext": quotedtext,
                "function": func,
                "langtag_filter": langtag,
                "then": []
            }
            for a in self.currentExpression["then"]:
                a["then"].append(e)
        elif self.currentDepth == 2:
            self.currentDepth = 3
            e = {
                "qname": value,
                "qname_expanded": qname_expanded,
                "quotedtext": quotedtext,
                "function": func,
                "langtag_filter": langtag,
                "then": []
            }
            for a in self.currentExpression["also"]:
                for a1 in a["then"]:
                    a1["then"].append(e)
        
        """
        if ctx.PNAME_LN() is not None:
            print("Entering qname expression: " + ctx.PNAME_LN().getText())
        elif ctx.FUNC() is not None:
            print("Entering qname expression: " + ctx.FUNC().getText())
        else:
            print("Entering qname expression: " + ctx.getText())
        """
        
        pass

    # Exit a parse tree produced by LDPathProgramParser#qnameExpr.
    def exitQnameExpr(self, ctx:LDPathProgramParser.QnameExprContext):
        self.currentDepth = self.currentDepth - 1
        
        self.currentExpression["filters"] = []
        if len(self.currentFilters) > 0:
            self.currentExpression["filters"] = self.currentFilters
        self.currentFilters = []
                
        if self.currentDepth == -1:
            # self.output["expressions"].append(self.currentExpression)
            self.currentExpressions.append(self.currentExpression)
            self.currentExpression = {}
        
        
        """
        if ctx.PNAME_LN() is not None:
            print("Exiting qname expression: " + ctx.PNAME_LN().getText())
        elif ctx.FUNC() is not None:
            print("Exiting qname expression: " + ctx.FUNC().getText())
        else:
            print("Exiting qname expression: " + ctx.getText())
        """
        
        pass


    # Enter a parse tree produced by LDPathProgramParser#qName.
    def enterQName(self, ctx:LDPathProgramParser.QNameContext):
        pass

    # Exit a parse tree produced by LDPathProgramParser#qName.
    def exitQName(self, ctx:LDPathProgramParser.QNameContext):
        pass

    # Enter a parse tree produced by LDPathProgramParser#datatype.
    def enterDatatype(self, ctx:LDPathProgramParser.DatatypeContext):
        #print(ctx.getText())
        for e in self.currentExpressions:
            e["datatype"] = ctx.getText()
            self.output["expressions"].append(e)
        self.currentExpressions = []
        pass

    # Exit a parse tree produced by LDPathProgramParser#datatype.
    def exitDatatype(self, ctx:LDPathProgramParser.DatatypeContext):
        # print(ctx.getText())
        pass

    # Enter a parse tree produced by LDPathProgramParser#datatypeValue.
    def enterDatatypeValue(self, ctx:LDPathProgramParser.DatatypeValueContext):
        # print("Entering datatype value: " + ctx.getText())
        pass

    # Exit a parse tree produced by LDPathProgramParser#datatypeValue.
    def exitDatatypeValue(self, ctx:LDPathProgramParser.DatatypeValueContext):
        pass

    # Enter a parse tree produced by LDPathProgramParser#typefilter.
    def enterTypefilter(self, ctx:LDPathProgramParser.TypefilterContext):
        filterPredicate = ctx.PNAME_LN()[0].getText()
        filterValue = ctx.PNAME_LN()[1].getText()
        f = {
            "predicate": filterPredicate,
            "value": filterValue
        }
        self.currentFilters.append(f)
        pass

    # Exit a parse tree produced by LDPathProgramParser#typefilter.
    def exitTypefilter(self, ctx:LDPathProgramParser.TypefilterContext):
        pass
