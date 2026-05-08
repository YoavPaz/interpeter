from interpeter import Interpeter, Token, TYPE


class AST(object):
    pass

class BinOpt(object):
    def __init__(self, left, op: Token, right):
        self.left = left
        self.token: Token = op
        self.op: Token = op
        self.right = right
    def __str__(self) -> str:
        return f'[op: {self.op}, left: {self.left}, right: {self.right}]'

class UnaryOp(object):
    def __init__(self, op, expr) -> None:
        self.token: Token = op
        self.op: Token = op
        self.expr = expr
    def __str__(self) -> str:
        return f'[{self.op.value}{self.expr}]'
        
class Num(AST):
    def __init__(self, token: Token):
        if token == None: raise Exception('While making NUM token recived is None!')
        self.value = token.value
        self.type = token.t
    def __str__(self) -> str:
        return f'num: {self.value}'

class Parser():
    def __init__(self, lexer: Interpeter):
        self.lexer = lexer

        self.current_token = self.lexer.next_token()

    def eat(self, type: TYPE):
        if self.current_token.t == type:
            self.current_token = self.lexer.next_token()
        else:
            self.error()

    def error(self):
        raise Exception('Invalid syntax!')
    
    def factor(self):
        token = self.current_token
        if token.t == TYPE.PLUS:
            self.eat(TYPE.PLUS)
            node = UnaryOp(token, self.factor())
            return node
        if token.t == TYPE.MINUS:
            self.eat(TYPE.MINUS)
            node = UnaryOp(token, self.factor())
            return node
        if token.t == TYPE.INTEGER:
            self.eat(TYPE.INTEGER)
            return Num(token)
        elif token.t == TYPE.P_IN:
            self.eat(TYPE.P_IN)
            node = self.expr()
            self.eat(TYPE.P_OUT)
            return node
    def term(self):
        node = self.factor()

        while self.current_token.t in (TYPE.MULTIPLY, TYPE.DIVIDE):
            t = self.current_token
            if self.current_token.t == TYPE.MULTIPLY:
                self.eat(TYPE.MULTIPLY)
                print("MUL")
            elif self.current_token.t == TYPE.DIVIDE:
                self.eat(TYPE.DIVIDE)
                print("DIVIDE")

            node = BinOpt(left=node, op=t, right=self.factor())

        return node

    def expr(self):
        """
        expr   : term ((PLUS | MINUS) term)*
        term   : factor ((MUL | DIV) factor)*
        factor : INTEGER | LPAREN expr RPAREN
        """

        node = self.term()

        while self.current_token.t in (TYPE.PLUS, TYPE.MINUS):
            t = self.current_token
            if self.current_token.t == TYPE.PLUS:
                print("PLUS")
                self.eat(TYPE.PLUS)
            elif self.current_token.t == TYPE.MINUS:
                print("MINUS")
                self.eat(TYPE.MINUS)
            print(f"making node with token {self.current_token}")
            node = BinOpt(left=node, op=t, right=self.term())

        return node

    def parse(self):
        return self.expr()

class NodeVisistor(object):
    def __init__(self):
        self.RPN = ""
    def visit(self, node):
        if node is None:
            raise Exception('Invalid Syntax')
        
        if isinstance(node, Num):
            self.RPN += f"{node.value} "
            return node.value
        if isinstance(node, UnaryOp):
            print("White vising nodes detecting unaryop!")
            if node.expr == None:
                raise Exception('expr none!')
            val: float = self.visit(node.expr)
            if node.token.value == '+': return +val
            if node.token.value == '-': return -val

        left = self.visit(node.left)
        right = self.visit(node.right)
        self.RPN += f"{node.token.value} "

        if node.token.value == '+': return left + right
        if node.token.value == '-': return left - right
        if node.token.value == '*': return left * right
        if node.token.value == '/': return left / right
while True:
    inp = input('calc> ')
    if inp == 'q':
        break
    lexer = Interpeter(inp)
    parser = Parser(lexer)
    nodeVisitor = NodeVisistor()

    print(nodeVisitor.visit(parser.parse()))
