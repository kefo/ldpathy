grammar LDPathProgram;

program
    : prologue instructions EOF
    ;

prologue
    : prefixDecl*
    ;

prefixDecl
    : '@prefix' PNAME_NS IRI_REF
    ;

instructions
    : instruction*
    ;

instruction
    : returnVal EQUALS queryPath ('|' queryPath)* DOUBLECOLONS datatype SEMICOLON
    ;

returnVal
    : VARNAME
    ;
    
//| queryPath ('|' queryPath)*
// queryPath ('/') queryPath
// | queryPath (',') queryPath
queryPath
    : queryPath ',' queryPath 
    | queryPath '/' queryPath
    | qnameExpr
    | '(' queryPath ('|' queryPath)* ')'
    | '[' queryPath ']'
    ;

// | PNAME_LN ('/') queryPath
qnameExpr
    : FUNC '(' queryPath ')'  
    | PNAME_LN '[' LANGTAG ']' ('/' queryPath)*
    | PNAME_LN '[' typefilter ('|' typefilter)* ']'  ('/' queryPath)*
    | PNAME_LN ('/') queryPath
    | PNAME_LN
    | QUOTEDTEXT
    | '.'
    ;
    

qName  :  PN_PREFIX (':' PN_PREFIX)*;

 
datatype
    : datatypeValue
    ;
    
datatypeValue: PNAME_LN;

typefilter: PNAME_LN 'is' PNAME_LN;

// LEXER RULES

FUNC: 'fn:concat';

DOUBLECOLONS: '::';

IRI_REF
    : '<' ( ~('<' | '>' | '"' | '{' | '}' | '|' | '^' | '\\' | '`') | (PN_CHARS))* '>'
    ;
    
QUOTEDTEXT
    : '"' ( PN_CHARS | COLON | ' ' | '(' | ')' | '.' | ';' )* '"'
    ;

PNAME_NS
    : PN_PREFIX? ':'
    ;

PNAME_LN
    : PNAME_NS PN_LOCAL
    ;

BLANK_NODE_LABEL
    : '_:' PN_LOCAL
    ;

VAR1
    : '?' VARNAME
    ;

VAR2
    : '$' VARNAME
    ;

LANGTAG
    : '@' PN_CHARS_BASE+ ('-' (PN_CHARS_BASE DIGIT)+)*
    ;

INTEGER
    : DIGIT+
    ;

DECIMAL
    : DIGIT+ '.' DIGIT*
    | '.' DIGIT+
    ;

DOUBLE
    : DIGIT+ '.' DIGIT* EXPONENT
    | '.' DIGIT+ EXPONENT
    | DIGIT+ EXPONENT
    ;

INTEGER_POSITIVE
    : '+' INTEGER
    ;

DECIMAL_POSITIVE
    : '+' DECIMAL
    ;

DOUBLE_POSITIVE
    : '+' DOUBLE
    ;

INTEGER_NEGATIVE
    : '-' INTEGER
    ;

DECIMAL_NEGATIVE
    : '-' DECIMAL
    ;

DOUBLE_NEGATIVE
    : '-' DOUBLE
    ;

EXPONENT
    : ('e'|'E') ('+'|'-')? DIGIT+
    ;

STRING_LITERAL1
    : '\'' ( ~('\u0027' | '\u005C' | '\u000A' | '\u000D') | ECHAR )* '\''
    ;

STRING_LITERAL2
    : '"'  ( ~('\u0022' | '\u005C' | '\u000A' | '\u000D') | ECHAR )* '"'
    ;

STRING_LITERAL_LONG1
    : '\'\'\'' ( ( '\'' | '\'\'' )? (~('\'' | '\\') | ECHAR ) )* '\'\'\''
    ;

STRING_LITERAL_LONG2
    : '"""' ( ( '"' | '""' )? ( ~('\'' | '\\') | ECHAR ) )* '"""'
    ;

ECHAR
    : '\\' ('t' | 'b' | 'n' | 'r' | 'f' | '"' | '\'')
    ;

NIL
    : '(' WS* ')'
    ;

ANON
    : '[' WS* ']'
    ;

PN_CHARS_U
    : PN_CHARS_BASE | '_'
    ;

VARNAME
    : ( PN_CHARS_U | DIGIT ) ( PN_CHARS_U | DIGIT | '\u00B7' | ('\u0300'..'\u036F') | ('\u203F'..'\u2040') )*
    ;

fragment
PN_CHARS
    : PN_CHARS_U
    | '-'
    | DIGIT
    ;

PN_PREFIX
    : PN_CHARS_BASE ((PN_CHARS|'.')* PN_CHARS)?
    ;

PN_LOCAL
    : ( PN_CHARS_U | DIGIT ) ((PN_CHARS|'.')* PN_CHARS)?
    ;

fragment
PN_CHARS_BASE
    : 'A'..'Z'
    | 'a'..'z'
    | '\u00C0'..'\u00D6'
    | '\u00D8'..'\u00F6'
    | '\u00F8'..'\u02FF'
    | '\u0370'..'\u037D'
    | '\u037F'..'\u1FFF'
    | '\u200C'..'\u200D'
    | '\u2070'..'\u218F'
    | '\u2C00'..'\u2FEF'
    | '\u3001'..'\uD7FF'
    | '\uF900'..'\uFDCF'
    | '\uFDF0'..'\uFFFD'
    ;

fragment
DIGIT
    : '0'..'9'
    ;

EQUALS: '=';
COLON: ':';
SEMICOLON: ';';

WS              : [ \t\n\r]+ -> skip ;
COMMENTS        : ('/*' .*? '*/' | '//' ~'\n'* '\n' ) -> skip;
