from luaparser.utils  import tests
from luaparser import ast
from luaparser.astnodes import *
import textwrap


class StatementsTestCase(tests.TestCase):
    """
    3.3.1 – Blocks
    """
    def test_empty_block(self):
        tree = ast.parse(";;;;")
        exp = Chunk(body=Block(body=[]))
        self.assertEqual(exp, tree)

    def test_2_block(self):
        tree = ast.parse("local a;local b;")
        exp = Chunk(body=Block(body=[
            LocalAssign(targets=[Name('a')],values=[]),
            LocalAssign(targets=[Name('b')],values=[])
        ]))
        self.assertEqual(exp, tree)

        """
    3.3.3 – Assignment
    """
    def test_set_number(self):
        tree = ast.parse("i=3")
        exp = Chunk(body=Block(body=[
            Assign(targets=[Name('i')],values=[Number(3)])
        ]))
        self.assertEqual(exp, tree)

    def test_set_string(self):
        tree = ast.parse('i="foo bar"')
        exp = Chunk(body=Block(body=[
            Assign(targets=[Name('i')],values=[String('foo bar')])
        ]))
        self.assertEqual(exp, tree)

    def test_set_array_index(self):
        tree = ast.parse('a[i] = 42')
        exp = Chunk(body=Block(body=[
            Assign(targets=[Index(idx=Name('i'), value=Name('a'))], values=[Number(42)])
        ]))
        self.assertEqual(exp, tree)

    def test_set_table_index(self):
        tree = ast.parse('_ENV.x = val')
        exp = Chunk(body=Block(body=[
            Assign(targets=[Index(idx=Name('x'), value=Name('_ENV'))], values=[Name('val')])
        ]))
        self.assertEqual(exp, tree)

    def test_set_multi(self):
        tree = ast.parse('x, y = y, x')
        exp = Chunk(body=Block(body=[
            Assign(targets=[Name('x'), Name('y')],values=[Name('y'), Name('x')])
        ]))
        self.assertEqual(exp, tree)

    '''
    3.3.4 – Control Structures
    '''
    def test_for_in(self):
        tree = ast.parse(textwrap.dedent("""
            for k, v in pairs({}) do
              print(k, v)
            end
            """))
        exp = Chunk(body=Block(body=[
            Forin(
                body=[Call(func=Name('print'), args=[Name('k'), Name('v')])],
                iter=Call(func=Name('pairs'), args=[Table(keys=[], values=[])]),
                targets=[Name('k'), Name('v')]
            )
        ]))
        self.assertEqual(exp, tree)

    def test_numeric_for(self):
        tree = ast.parse(textwrap.dedent("""
            for i=1,10,2 do print(i) end
            """))
        exp = Chunk(body=Block(body=[
            Fornum(
                start=Number(1),
                stop=Number(10),
                step=Number(2)
            )
        ]))
        self.assertEqual(exp, tree)

    def test_do_end(self):
        tree = ast.parse(textwrap.dedent("""
            do
              local foo = 'bar'
            end
            """))
        exp = Chunk(body=Block(body=[
            Do(
                body=[LocalAssign(targets=[Name('foo')],values=[String('bar')])]
            )
        ]))
        self.assertEqual(exp, tree)

    def test_while(self):
        tree = ast.parse(textwrap.dedent("""
            while true do
              print('hello world')
            end"""))
        exp = Chunk(body=Block(body=[
            While(test=TrueExpr(), body=[
                Call(func=Name('print'), args=[String('hello world')])
            ])
        ]))
        self.assertEqual(exp, tree)

    def test_repeat_until(self):
        tree = ast.parse(textwrap.dedent("""
            repeat        
            until true
            """))
        exp = Chunk(body=Block(body=[
            Repeat(body=[], test=TrueExpr())
        ]))
        self.assertEqual(exp, tree)

    def test_if(self):
        tree = ast.parse(textwrap.dedent("""
            if true then    
            end
            """))
        exp = Chunk(body=Block(body=[
            If(
                test=TrueExpr(),
                body=[],
                orelse=None
            )
        ]))
        self.assertEqual(exp, tree)

    def test_if_exp(self):
        tree = ast.parse(textwrap.dedent("""
            if (a<2) then    
            end
            """))
        exp = Chunk(body=Block(body=[
            If(
                test=LessThanOp(
                    left=Name('a'),
                    right=Number(2)
                ),
                body=[],
                orelse=None
            )
        ]))
        self.assertEqual(exp, tree)

    def test_if_elseif(self):
        tree = ast.parse(textwrap.dedent("""
            if true then 
            elseif false then     
            end
            """))
        print(ast.toPrettyStr(tree))
        exp = Chunk(body=Block(body=[
            If(
                test=TrueExpr(),
                body=[],
                orelse=If(test=FalseExpr(), body=[], orelse=None)
            )
        ]))
        self.assertEqual(exp, tree)

    def test_if_elseif_else(self):
        tree = ast.parse(textwrap.dedent("""
            if true then 
            elseif false then  
            else   
            end
            """))
        exp = Chunk(body=Block(body=[
            If(
                test=TrueExpr(),
                body=[],
                orelse=If(
                    test=FalseExpr(),
                    body=[],
                    orelse=[]
                )
            )
        ]))
        self.assertEqual(exp, tree)

    def test_if_elseif_elseif_else(self):
        tree = ast.parse(textwrap.dedent("""
            if true then 
            elseif false then  
            elseif 42 then 
            else   
            end
            """))
        exp = Chunk(body=Block(body=[
            If(
                test=TrueExpr(),
                body=[],
                orelse=If(
                    test=FalseExpr(),
                    body=[],
                    orelse=If(
                        test=Number(42),
                        body=[],
                        orelse=[]
                    )
                )
            )
        ]))
        self.assertEqual(exp, tree)

    def test_label(self):
        tree = ast.parse(textwrap.dedent("""
            ::foo::
            """))
        exp = Chunk(body=Block(body=[
            If(
                test=TrueExpr(),
                body=[],
                orelse=If(
                    test=FalseExpr(),
                    body=[],
                    orelse=If(
                        test=Number(42),
                        body=[],
                        orelse=[]
                    )
                )
            )
        ]))
        self.assertEqual(exp, tree)

    def test_label(self):
        tree = ast.parse(textwrap.dedent("""
            goto foo
            ::foo::
            """))
        exp = Chunk(body=Block(body=[
            Goto(label='foo'),
            Label(id='foo')
        ]))
        self.assertEqual(exp, tree)


    def test_comment_line(self):
        tree = ast.parse(textwrap.dedent("""
            -- a basic comment
            """))
        exp = Chunk(body=Block(body=[
            Comment('a basic comment')
        ]))
        self.assertEqual(exp, tree)

    # def test_comment_enable_code(self):
    #     tree = ast.parse(textwrap.dedent("""
    #         ---[[The long handled doubleshovel means that this code will run
    #         print "This will print because it is not a comment!"
    #         -- We can still include comments by prefixing them with a doubledash
    #         -- print "This will not print because it is commented out"
    #         ]]
    #         """))
    #     exp = Chunk(body=Block(body=[
    #         Goto(label='foo'),
    #         Label(id='foo')
    #     ]))
    #     Printer.pprint(tree, Printer.Style.PYTHON, True)
    #     self.assertEqual(exp, tree)