from interpeter import Interpeter, Token, TYPE, RESERVED_KEYWORDS

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
    __repr__ = __str__

class UnaryOp(object):
    def __init__(self, op, expr) -> None:
        self.token: Token = op
        self.op: Token = op
        self.expr = expr
    def __str__(self) -> str:
        return f'[{self.op.value}{self.expr}]'
    __repr__ = __str__
        
class Num(AST):
    def __init__(self, token: Token):
        if token == None: raise Exception('While making NUM token recived is None!')
        self.value = token.value
        self.type = token.t
    def __str__(self) -> str:
        return f'num: {self.value}'
    __repr__ = __str__

class Compound(AST):
    def __init__(self) -> None:
        self.children = []
    def __str__(self) -> str:
        return f'compound: {self.children}'
    __repr__ = __str__

class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right
    def __str__(self) -> str:
        return f'Assign: {self.left} {self.op} {self.right}'
    __repr__ = __str__

class Var(AST):
    def __init__(self, token) -> None:
        self.token = token
        self.value = self.token.value
    def __str__(self) -> str:
        return f'var: {self.token} {self.value}'
    __repr__ = __str__

class NoOp(AST):
    def __str__(self) -> str:
        return f'NoOp'
    __repr__ = __str__

class Parser():
    def __init__(self, lexer: Interpeter):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    def program(self):
        """program : compound_statement DOT"""
        node = self.compound_statement()
        self.eat(TYPE.DOT)
        return node

    def compound_statement(self):
        """
        compound_statement: BEGIN statement_list END
        """
        self.eat(TYPE.BEGIN)
        nodes = self.statement_list()
        self.eat(TYPE.END)

        root = Compound()
        for node in nodes:
            root.children.append(node)

        return root

    def statement_list(self):
        """
        statement_list : statement
                       | statement SEMI statement_list
        """
        node = self.statement()

        results = [node]

        while self.current_token.t == TYPE.SEMI:
            self.eat(TYPE.SEMI)
            results.append(self.statement())

        if self.current_token.t == TYPE.ID:
            self.error()

        return results

    def statement(self):
        """
        statement : compound_statement
                  | assignment_statement
                  | empty
        """
        if self.current_token.t == TYPE.BEGIN:
            node = self.compound_statement()
        elif self.current_token.t == TYPE.ID:
            node = self.assignment_statement()
        else:
            node = self.empty()
        return node

    def assignment_statement(self):
        """
        assignment_statement : variable ASSIGN expr
        """
        left = self.variable()
        token = self.current_token
        self.eat(TYPE.ASSIGN)
        right = self.expr()
        node = Assign(left, token, right)
        return node

    def variable(self):
        """
        variable : ID
        """
        node = Var(self.current_token)
        self.eat(TYPE.ID)
        return node

    def empty(self):
        """An empty production"""
        return NoOp()

    def eat(self, type: TYPE):
        if self.current_token.t == type:
            self.current_token = self.lexer.next_token()
        else:
            self.error()

    def _id(self):
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.current_index += 1
        
        token = RESERVED_KEYWORDS.get(result)
        return token

    def error(self):
        raise Exception('Invalid syntax!')
    
    def factor(self):
        token = self.current_token
        if token.t == TYPE.PLUS:
            self.eat(TYPE.PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.t == TYPE.MINUS:
            self.eat(TYPE.MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.t == TYPE.INTEGER:
            self.eat(TYPE.INTEGER)
            return Num(token)
        elif token.t == TYPE.P_IN:
            self.eat(TYPE.P_IN)
            node = self.expr()
            self.eat(TYPE.P_OUT)
            return node
        else:
            node = self.variable()
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
        node = self.program()
        if self.current_token.t != TYPE.EOF:
            self.error()
        return node

class NodeVisistor(object):
    def __init__(self):
        self.RPN = ""
        self.call_stack = []
        self.current_scope = -1
    def make_scope(self):
        self.call_stack.append({})
    def remove_scope(self):
        self.call_stack.pop()
    def get_scope(self) -> dict:
        if self.current_scope == None: # no scope...
                self.make_scope()
        return self.call_stack[self.current_scope]
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
        if isinstance(node, Compound):
            #print(f"making new compound, call stack: {self.call_stack}")
            self.make_scope()
            for child in node.children:
                self.visit(child)
            print(f"removing scope, full scope: {self.call_stack}")
            self.remove_scope()
            return None
        if isinstance(node, Assign):
            self.get_scope()[node.left.value] = self.visit(node.right)
            #print(f"assigning var, call stack: {self.call_stack}")
        if isinstance(node, Var):
            var_name = node.value
            val = self.get_scope().get(var_name)
            #print(f"reading stack: {self.call_stack}")
            if val is None:
                raise NameError(repr(var_name))
            else:
                return val
        if isinstance(node, NoOp):
            return None        

        left = self.visit(node.left)
        right = self.visit(node.right)
        self.RPN += f"{node.token.value} "

        if node.token.value == '+': return left + right
        if node.token.value == '-': return left - right
        if node.token.value == '*': return left * right
        if node.token.value == '/': return left / right

def run_script(name: str):
    with open(name, "r") as f:
        inp = f.read()
    inp = " ".join(inp.split()) + " "
    lexer = Interpeter(inp)
    parser = Parser(lexer)
    node_visitor = NodeVisistor()
    node = parser.parse()
    print(node)
    node_visitor.visit(node)
    print(node_visitor.call_stack)

run_script("test.end")
