# Author: Kelly Smith
# Created: October 30, 2012
# Modified: October 31, 2012

import re


# Used to make sure that Token and PrefixOperator both include each of these functions
class ArgumentInterface():
    def isToken(self):
        raise NotImplementedError( "Must implement isToken()" )
    
    def isOperation(self):
        raise NotImplementedError( "Must implement isOperation()" )
    

# Used to represent each of the smallest pieces of the infix expression being parsed
class Token(ArgumentInterface):
    INT = 1
    VAR = 2
    PLUS = 3
    MINUS = 4
    TIMES = 5
    DIV = 6
    LPAREN = 7
    RPAREN = 8
    EOF = 9
    
    string2tok = {
        "^[1-9]$": 1,
        "^[a-zA_Z]$": 2,
        "^\+$": 3,
        "^-$": 4,
        "^\*$": 5,
        "^/$": 6,
        "^\($": 7,
        "^\)$": 8
    }
    
    def isToken(self):
        return True
    
    def isOperation(self):
        return False
    
    # returns a string value representing each valid type of Token
    @staticmethod
    def lookupToken(token):
        
        for key in Token.string2tok.iterkeys():
            m = re.match(key, token)
            if m is not None and m.group(0) != None:
                return Token.string2tok[key]
        
        return None
        
    
    def __init__(self, token):
        self.value = token # No intrinsic value except for INT and VAR
        if token is not None:
            self.type = Token.lookupToken(self.value)
        else:
            self.type = Token.EOF
    
    # Used to directly compare Token objects
    def __eq__(self, other):
        return self.type == other
    
    def __str__(self):
        if self == Token.INT:
            return str(self.value)
        elif self == Token.VAR:
            return str(self.value)
        elif self == Token.PLUS:
            return "PLUS"
        elif self == Token.MINUS:
            return "MINUS"
        elif self == Token.TIMES:
            return "TIMES"
        elif self.type == Token.DIV:
            return "DIV"
        elif self == Token.LPAREN:
            return "LPAREN"
        elif self == Token.RPAREN:
            return "RPAREN"
        elif self == Token.EOF:
            return "EOF"
        else:
            return "Invalid Token."

# Default exception thrown by Tokenizer class
class InvalidTokenError(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)

# Represents a prefix operation -> (OPERATOR ARG1 ARG2)
# Used to implement a binary parse tree with Token objects as the leaves
class PrefixOperator(ArgumentInterface):
    PLUS = 1
    MINUS = 2
    MULTIPLY = 3
    DIVIDE = 4
    NOP = 5
    
    op2string = {
        1: "+",
        2: "-",
        3: "*",
        4: "/",
        5: "NOP"
    }
    
    def isToken(self):
        return False
    
    def isOperation(self):
        return True
    
    def __init__(self, operator=5, left_arg=None, right_arg=None):
        self.operator = operator
        self.left_arg = left_arg
        self.right_arg = right_arg
    
    def __str__(self):
        # Constants default to NOP with the left_arg set to the value
        return "(" + PrefixOperator.op2string[self.operator] + " " + str(self.left_arg) + " " + str(self.right_arg) + ")"

    
'''
This class managers splitting an expression into tokens and then identifying their type.
    - For the given input class, this is as simple as splitting between ' ' characters.
'''
class Tokenizer:
    
    def __init__(self, expression):
        self.current_tok = 0 # start pointing at nothing
        self.expressionStr = expression
        self.tokens = []
        
        self.__tokenize()
    
    def __tokenize(self):
        for tok_str in self.expressionStr.split(" "):
            self.current_tok += 1 # keep track of the current token for error reporting
            token = Token(tok_str)
            if token.type is None:
                raise InvalidTokenError(tok_str + " is not a valid token. Token number: " + str(self.current_tok))
            
            self.tokens.append(token)
        
        self.current_tok = 0 # reset counter for use in parsing
    
    def nextToken(self):
        self.current_tok += 1
        if len(self.tokens) > self.current_tok-1:
            return self.tokens[self.current_tok-1]
        else:
            return Token(None)

# General purpose exception raised by the Parser when it encounters an error.
class ParsingError(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)

'''
Parser implements a recursive descent parser.  Tokens are generated using Tokenizer.  Returns a binary operator tree based on the PrefixOperator class.
    Can potentially return a Token leaf for simple expressions which do not have any operations.
'''
class Parser:
    
    def __init__(self, expression):
        self.token_count = 0
        self.current_token = None
        self.tokenizer = Tokenizer(expression)
    
    # Looks to see if the current token has been matched
    #    - if it has, returns the next token
    #    - else returns the most recent token
    def __nextToken(self):
        if self.current_token == None:
            self.token_count += 1
            self.current_token = self.tokenizer.nextToken()
            return self.current_token
        
        return self.current_token
    
    # Asserts that the current(next) token will match a given token
    #   Throws an error if this is not the case to abort parsing
    def match(self, token):
        next_tok = self.__nextToken()
        if next_tok == token:
            if self.DEBUG:
                print "Match: " + str(next_tok) + " (" + str(next_tok.value) + ")" 
            self.current_token = None # cause __nextToken to grab another from the Tokenizer
            return True
        else:
            raise ParsingError("Invalid token at position: " + self.token_count + ". Exiting parser.")
            return False
    
    # Used by the simplify method to perform simplification operations
    @staticmethod
    def execute_operation(operator, left, right):

        left = int(left)
        right = int(right)
        
        if operator == PrefixOperator.PLUS:
            return left + right
        elif operator == PrefixOperator.MINUS:
            return left - right
        elif operator == PrefixOperator.MULTIPLY:
            return left * right
        elif operator == PrefixOperator.DIVIDE:
            return round(left / right)
        else:
            raise ParsingError("Invalid simplification operation: " + str(PrefixOperator.op2string[operator]) + ", " + str(left) + ", " + str(right) + ".")
    
    # op arg is a binary tree.  Simplify will recursively simplify each node and return a binary tree, the size of which is less than or equal to the original
    def simplify(self, op):
        if op is not None:
            if op.isToken():
                #print "Reached a token: " + str(op)
                return op
            
            
            if op.isOperation():
                #print "Reached an operation: " + str(op)
                left_arg = self.simplify(op.left_arg)
                right_arg = self.simplify(op.right_arg)
                
                if left_arg.isToken() and right_arg.isToken():
                    if left_arg.type == Token.INT and right_arg.type == Token.INT:
                        # Simplification is possible
                        result = int(Parser.execute_operation(op.operator, left_arg.value, right_arg.value))
                        # Make an invalid placeholder token
                        token = Token(None)
                        token.type = Token.INT
                        token.value = result
                        return token
                
                op.left_arg = left_arg
                op.right_arg = right_arg
                return op
                
        return None
            
        
    # Initialize the entire parsing process and return the result
    def parse(self, simplify=False, debug=False):
        self.DEBUG = debug
        
        '''while self.__nextToken():
            self.match(self.current_token.type)
        
        return'''
        result = self.Expr()
        if simplify:
            result = self.simplify(result)
            
        return result
    
    
    ######################
    #  BELOW is a series of functions implementing a recursive decent parser.  This parser implements the LL(1) grammer listed below
    '''
    Start -> Expr

    Expr -> Term SimpleExpr
    
    SimpleExpr -> MINUS Term SimpleExpr
           -> PLUS Term SimpleExpr
           -> EMPTY
    
    Term -> Factor TermCont
               
    TermCont -> TIMES Term
         -> DIV Term
         -> EMPTY
    
    Factor -> INT
           -> VAR
           -> LPAREN Expr RPAREN
    '''
    
    def Expr(self):
        if self.DEBUG:
            print 'Expr -> Term SimpleExpr'
        
        
        term = self.Term() # maintains operator precedence
        expr = self.SimpleExpr()
        
        if expr is not None and expr.operator != PrefixOperator.NOP:
            if expr.left_arg is None:
                expr.left_arg = term
                return expr
        else:
            return term
    
    def Term(self):
        if self.DEBUG:
            print 'Term -> Factor TermCont'
        
        factor = self.Factor()
        term = self.TermCont() # this is either None or a PrefixOperation
        op = None
        if term == None:
            return factor
        else:
            op = term
            op.left_arg = factor
        
        return op
    
    def SimpleExpr(self):      
        '''SimpleExpr -> MINUS Term SimpleExpr
                      -> PLUS Term SimpleExpr
                       > EMPTY'''
                       
        next_token = self.__nextToken()
        if next_token == Token.MINUS:
            if self.DEBUG:
                print 'SimpleExpr -> MINUS Term SimpleExpr'
            self.match(Token.MINUS)
            term = self.Term()
            expr = self.SimpleExpr()
            
            if expr is not None:
                if expr.left_arg is None:
                    expr.left_arg = term
                    return expr
                else:
                    return PrefixOperator(PrefixOperator.MINUS, term, expr)
            else:
                return PrefixOperator(PrefixOperator.MINUS, None, term)
                        
        elif next_token == Token.PLUS:
            if self.DEBUG:
                print 'SimpleExpr -> PLUS Term SimpleExpr'
            self.match(Token.PLUS)
            term = self.Term()
            expr = self.SimpleExpr()
            
            if expr is not None:
                if expr.left_arg is None:
                    expr.left_arg = term
                    return PrefixOperator(PrefixOperator.PLUS, None, expr)
                else:
                    return PrefixOperator(PrefixOperator.PLUS, term, expr)
            else:
                return PrefixOperator(PrefixOperator.PLUS, None, term)
        else:
            if self.DEBUG:
                print 'SimpleExpr -> EMPTY'
            return None
            
    def TermCont(self):
        '''TermCont -> TIMES Term
                    -> DIV Term
                    -> EMPTY'''
            
        next_token = self.__nextToken()
        if next_token == Token.TIMES:
            if self.DEBUG:
                print 'TermCont -> TIMES Term'
            self.match(Token.TIMES)
            arg = self.Term()
            return PrefixOperator(PrefixOperator.MULTIPLY, None, arg)
            
        elif next_token == Token.DIV:
            if self.DEBUG:
                print 'TermCont -> DIV Term'
            self.match(Token.DIV)
            arg = self.Term()
            return PrefixOperator(PrefixOperator.DIVIDE, None, arg)
        
        else:
            if self.DEBUG:
                print 'TermCont -> EMPTY'
            return None
            
    def Factor(self):
        ''' Factor -> INT
                   -> VAR
                   -> LPAREN Expr RPAREN'''
        
        next_token = self.__nextToken()
        if next_token == Token.INT:
            if self.DEBUG:
                print 'Factor -> INT'
            self.match(Token.INT)
            return next_token
            
        elif next_token == Token.VAR:
            if self.DEBUG:
                print 'Factor -> VAR'
            self.match(Token.VAR)
            return next_token
            
        elif next_token == Token.LPAREN:
            if self.DEBUG:
                print 'Factor -> LPAREN Expr RPAREN'
                
            self.match(Token.LPAREN)
            op = self.Expr()
            self.match(Token.RPAREN)
            return op
            
        else:
            raise ParsingError("Invalid token. Found " + str(next_token.value) + " but expecting INT, VAR, or ( at pos: " + str(self.token_count))