# Generated from LDPathProgram.g4 by ANTLR 4.7.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .LDPathProgramParser import LDPathProgramParser
else:
    from LDPathProgramParser import LDPathProgramParser

# This class defines a complete generic visitor for a parse tree produced by LDPathProgramParser.

class LDPathProgramVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by LDPathProgramParser#program.
    def visitProgram(self, ctx:LDPathProgramParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LDPathProgramParser#prologue.
    def visitPrologue(self, ctx:LDPathProgramParser.PrologueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LDPathProgramParser#prefixDecl.
    def visitPrefixDecl(self, ctx:LDPathProgramParser.PrefixDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LDPathProgramParser#instructions.
    def visitInstructions(self, ctx:LDPathProgramParser.InstructionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LDPathProgramParser#instruction.
    def visitInstruction(self, ctx:LDPathProgramParser.InstructionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LDPathProgramParser#returnVal.
    def visitReturnVal(self, ctx:LDPathProgramParser.ReturnValContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LDPathProgramParser#queryPath.
    def visitQueryPath(self, ctx:LDPathProgramParser.QueryPathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LDPathProgramParser#qnameExpr.
    def visitQnameExpr(self, ctx:LDPathProgramParser.QnameExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LDPathProgramParser#qName.
    def visitQName(self, ctx:LDPathProgramParser.QNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LDPathProgramParser#datatype.
    def visitDatatype(self, ctx:LDPathProgramParser.DatatypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LDPathProgramParser#datatypeValue.
    def visitDatatypeValue(self, ctx:LDPathProgramParser.DatatypeValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LDPathProgramParser#typefilter.
    def visitTypefilter(self, ctx:LDPathProgramParser.TypefilterContext):
        return self.visitChildren(ctx)



del LDPathProgramParser