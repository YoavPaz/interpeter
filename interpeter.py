from enum import Enum
from typing import Optional

from enum import Enum

class TYPE(Enum):
    INTEGER = 0
    PLUS = 1
    MINUS = 2
    MULTIPLY = 3
    DIVIDE = 4
    P_IN = 5
    P_OUT = 6
    ASSIGN = 7
    SEMI = 8
    DOT = 9

    ID = 10
    BEGIN = 11
    END = 12

    EOF = -1

class Token:
    def __init__(self, type: TYPE, value):
        self.t: TYPE = type
        self.value = value
    def __str__(self):
        return 'Token({type}, {value})'.format(
                type = self.t,
                value = self.value
                )
    def __repr__(self):
        return self.__str__()

RESERVED_KEYWORDS = {
    'BEGIN': Token(TYPE.BEGIN, 'BEGIN'),
    'END': Token(TYPE.END, 'END'),
}

class Interpeter:
    def __init__(self, txt: str) -> None:
        self.txt = txt#txt.replace(" ", "")        
        self.i = 0
        self.current_token: Optional[Token] = None
    def _id(self) -> Token:
        result = ''

        while self.i < len(self.txt) and self.txt[self.i].isalnum():
            result += self.txt[self.i]
            self.i += 1

        return RESERVED_KEYWORDS.get(result, Token(TYPE.ID, result))    
    def next_token(self) -> Token:
        if self.i >= len(self.txt):
            return Token(TYPE.EOF, None)
        
        while self.i < len(self.txt) and self.txt[self.i].isspace():
            #print("Detected space skipping to next one!")
            self.i += 1
        
        if self.i >= len(self.txt):
            return Token(TYPE.EOF, None)
        
        value = self.txt[self.i]
        #print(f"Read value: {value}")
        if value.isalpha():
            d = self._id()
            #print(f"Value is alpha, getting from id: {d}")
            return d
        self.i += 1
        if value.isdigit():
            val = self.extract_number(self.txt, self.i - 1)
            print(f"Value is digit: {val}")
            self.i += len(str(val)) - 1
            return Token(TYPE.INTEGER, val)
        #print(f"Value {value} Peek {self.peek()}")
        if value == ':' and self.peek() == '=':
            self.i += 1
            return Token(TYPE.ASSIGN, ':=')
        if value == ';':
            return Token(TYPE.SEMI, ';')
        if value == '.':
            return Token(TYPE.DOT, '.')
        if value == '+': 
            return Token(TYPE.PLUS, value)
        if value == '-': return Token(TYPE.MINUS, value)
        if value == '*': return Token(TYPE.MULTIPLY, value)
        if value == '/': return Token(TYPE.DIVIDE, value)
        if value == '(': return Token(TYPE.P_IN, value)
        if value == ')': return Token(TYPE.P_OUT, value)
        return Token(TYPE.EOF, None)
    def extract_number(self, txt: str, index: int) -> Optional[int]:
        current_digit = txt[index]
        digits = ""
        
        while current_digit.isdigit():
            digits += str(current_digit)
            index+=1
            if index == len(txt): break
            current_digit = txt[index]
        if digits == "": return None
        return int(digits)
    def peek(self):
        peek_pos = self.i
        #print("Peek pos",peek_pos,"i",self.i,"longer than length: ",peek_pos > len(self.txt) - 1)
        if peek_pos > len(self.txt) - 1:
            #print("Returning None From Peek!")
            return None
        else:
            #print(f"Returning {self.txt[peek_pos]} From Peek!")
            return self.txt[peek_pos]
        
    def error(self):
        raise Exception("invalid character!")
    
    def noneError(self):
        raise Exception("Current token is none!, can't parse the token.")
    
    def checkForNoneToken(self):
        if self.current_token == None:
            self.noneError()

    def eat(self, token_type: TYPE):
        if self.current_token == None:
            raise Exception("Current token is none!, can't parse the token.")
        #print(f"[eat] current token type {self.current_token.t} token type {token_type}, equal {self.current_token.t == token_type}")
        if self.current_token.t == token_type:
            #print(f"While eating getting next token. {self.i}")
            self.current_token = self.next_token()
        else:
            self.error()

    def factor(self):
        val = self.current_token.value
        self.eat(TYPE.INTEGER)
        return val

        
    def paranthetis_expr(self):
        if self.current_token.t == TYPE.P_IN:
            self.eat(TYPE.P_IN)          # consume '('
            result = self.expr_inner()   # evaluate inside
            self.eat(TYPE.P_OUT)         # consume ')'
            return result
        else:
            return self.factor()         # plain number

    def expr_inner(self) -> float:
        result = self.term()
        if self.current_token == None:
            self.error()
        while self.current_token.t in (TYPE.PLUS, TYPE.MINUS):
            token = self.current_token
            if token.t == TYPE.PLUS:
                self.eat(TYPE.PLUS)
                result += self.term()
            elif token.t == TYPE.MINUS:
                self.eat(TYPE.MINUS)
                result -= self.term()
        return float(result)

    def multi_expr(self):
        if self.current_token == None:
            self.current_token = self.next_token()
        self.current_token.value = self.paranthetis_expr()
        result = self.current_token.value

        while self.current_token.t in (TYPE.MULTIPLY, TYPE.DIVIDE):
            token = self.current_token
            if token.t == TYPE.MULTIPLY:
                self.eat(TYPE.MULTIPLY)
                result *= self.paranthetis_expr()
            if token.t == TYPE.DIVIDE:
                self.eat(TYPE.DIVIDE)
                result /= self.paranthetis_expr()
        return result

    def term(self):
        return self.multi_expr()

    def expr(self) -> float:
        self.current_token = self.next_token()
        return self.expr_inner()

if __name__ == "__main__":
    while True:
        inp = input("> ")
        if inp == "q": break
    interpeter = Interpeter(inp)
    print(interpeter.expr())
