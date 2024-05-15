import ast
import unittest

from mutpy import operators, codegen, coverage, utils

EOL = '\n'
INDENT = ' ' * 4
PASS = 'pass'


class MutationOperatorTest(unittest.TestCase):
    class PassIdOperator(operators.MutationOperator):

        def mutate_Pass(self, node):
            return node

    def setUp(self):
        self.operator = self.PassIdOperator()
        self.target_ast = utils.create_ast(PASS)

    def test_generate_all_mutations_if_always_sampler(self):
        class AlwaysSampler:

            def is_mutation_time(self):
                return True

        mutations = list(self.operator.mutate(self.target_ast, sampler=AlwaysSampler()))

        self.assertEqual(len(mutations), 1)

    def test_no_mutations_if_never_sampler(self):
        class NeverSampler:

            def is_mutation_time(self):
                return False

        mutations = list(self.operator.mutate(self.target_ast, sampler=NeverSampler()))

        self.assertEqual(len(mutations), 0)


class OperatorTestCase(unittest.TestCase):

    def assert_mutation(self, original, mutants, lines=None, operator=None, with_coverage=False, with_exec=False):
        original_ast = utils.create_ast(original)
        if with_coverage:
            coverage_injector = coverage.CoverageInjector()
            coverage_injector.inject(original_ast)
        else:
            coverage_injector = None
        if not operator:
            operator = self.__class__.op
        if isinstance(mutants, str):
            mutants = [mutants]
        mutants = list(map(codegen.remove_extra_lines, mutants))
        module = None
        if with_exec:
            module = utils.create_module(original_ast)
        for mutation, mutatnt in operator.mutate(original_ast, coverage_injector=coverage_injector, module=module):
            mutant_code = codegen.remove_extra_lines(codegen.to_source(mutatnt))
            msg = '\n\nMutant:\n\n' + mutant_code + '\n\nNot found in:'
            for other_mutant in mutants:
                msg += '\n\n----------\n\n' + other_mutant
            self.assertIn(mutant_code, mutants, msg)
            mutants.remove(mutant_code)
            self.assert_location(mutatnt)
            if lines is not None:
                if not hasattr(mutation.node, 'lineno'):
                    self.assert_mutation_lineo(mutation.node.parent.lineno, lines)
                else:
                    self.assert_mutation_lineo(mutation.node.lineno, lines)

        self.assertListEqual(mutants, [], 'did not generate all mutants')

    def assert_no_mutation(self, original, **kwargs):
        self.assert_mutation(original, mutants=[], **kwargs)

    def assert_location(self, mutant):
        for node in ast.walk(mutant):
            if 'lineno' in node._attributes:
                self.assertTrue(hasattr(node, 'lineno'), 'Missing lineno in ' + str(node))
            if 'col_offset' in node._attributes:
                self.assertTrue(hasattr(node, 'col_offset'), 'Missing col_offset in ' + str(node))

    def assert_mutation_lineo(self, lineno, lines):
        mutation_line = lines.pop(0)
        self.assertEqual(mutation_line, lineno, 'Bad mutation lineno!')


class ConstantReplacementTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.ConstantReplacement()

    def test_numbers_increment(self):
        self.assert_mutation('2 + 3 - 99', ['(3 + 3) - 99', '(2 + 4) - 99', '(2 + 3) - 100'])

    def test_string_replacement(self):
        self.assert_mutation(
            "x = 'ham' + 'egs'",
            [
                "x = '{}' + 'egs'".format(self.op.FIRST_CONST_STRING),
                "x = 'ham' + '{}'".format(self.op.FIRST_CONST_STRING),
                "x = '' + 'egs'",
                "x = 'ham' + ''",
            ],
        )

    def test_resign_if_empty(self):
        self.assert_mutation(
            "'ham' + ''",
            [
                "'{}' + ''".format(self.op.FIRST_CONST_STRING),
                "'' + ''", "'ham' + '{}'".format(self.op.FIRST_CONST_STRING),
            ],
        )

    def test_resign_first(self):
        self.assert_mutation(
            "'' + 'ham'",
            [
                "'' + '{}'".format(self.op.FIRST_CONST_STRING),
                "'' + ''",
                "'{}' + 'ham'".format(self.op.FIRST_CONST_STRING),
            ],
        )

    def test_not_mutate_function(self):
        self.assert_mutation("@notmutate" + EOL + "def x():" + EOL + INDENT + "'ham'", [])

    def test_not_mutate_class(self):
        self.assert_mutation("@notmutate" + EOL + "class X:" + EOL + INDENT + "'ham'", [])

    def test_replace_first_const_string(self):
        self.assert_mutation(
            "x = '{}'".format(self.op.FIRST_CONST_STRING),
            ["x = '{}'".format(self.op.SECOND_CONST_STRING), "x = ''"],
        )

    def test_not_mutate_docstring(self):
        self.assert_mutation("def x():" + EOL + INDENT + '""""doc"""', [])


class ArithmeticOperatorReplacementTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.ArithmeticOperatorReplacement()

    def test_add_to_sub_replacement(self):
        self.assert_mutation('x + y + z', ['(x - y) + z', '(x + y) - z'])

    def test_sub_to_add_replacement(self):
        self.assert_mutation('x - y', ['x + y'])

    def test_mult_to_div_and_pow_replacement(self):
        self.assert_mutation('x * y', ['x / y', 'x // y', 'x ** y'])

    def test_div_replacement(self):
        self.assert_mutation('x / y', ['x * y', 'x // y'])

    def test_floor_div_to_div(self):
        self.assert_mutation('x // y', ['x / y', 'x * y'])

    def test_mod_to_mult(self):
        self.assert_mutation('x % y', ['x * y'])

    def test_pow_to_mult(self):
        self.assert_mutation('x ** y', ['x * y'])

    def test_mutation_lineno(self):
        self.assert_mutation(
            'pass' + EOL + 'x + y' + EOL + 'x - y',
            ['pass' + EOL + 'x - y' + EOL + 'x - y', 'pass' + EOL + 'x + y' + EOL + 'x + y'],
            [2, 3],
        )

    def test_not_mutate_augmented_assign(self):
        self.assert_mutation('x += y', [])

    def test_usub(self):
        self.assert_mutation('(-x)', ['+x'])

    def test_uadd(self):
        self.assert_mutation('(+x)', ['-x'])


class AssignmentOperatorReplacementTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.AssignmentOperatorReplacement()

    def test_add_to_sub_replacement(self):
        self.assert_mutation('x += y', ['x -= y'])

    def test_not_mutate_normal_use(self):
        self.assert_mutation('x + y', [])


class ArithmeticOperatorDeletionTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.ArithmeticOperatorDeletion()

    def test_usub(self):
        self.assert_mutation('-x', ['x'])

    def test_uadd(self):
        self.assert_mutation('+x', ['x'])


class LogicalOperatorReplacementTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.LogicalOperatorReplacement()

    def test_bin_and_to_bit_or(self):
        self.assert_mutation('x & y', ['x | y'])

    def test_bit_or_to_bit_and(self):
        self.assert_mutation('x | y', ['x & y'])

    def test_bit_xor_to_bit_and(self):
        self.assert_mutation('x ^ y', ['x & y'])

    def test_lshift_to_rshift(self):
        self.assert_mutation('x << y', ['x >> y'])

    def test_rshift_to_lshift(self):
        self.assert_mutation('x >> y', ['x << y'])


class LogicalOperatorDeletionTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.LogicalOperatorDeletion()

    def test_invert(self):
        self.assert_mutation('~x', ['x'])


class LogicalConnectorReplacementTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.LogicalConnectorReplacement()

    def test_and_to_or(self):
        self.assert_mutation('(x and y)', ['(x or y)'])

    def test_or_to_and(self):
        self.assert_mutation('(x or y)', ['(x and y)'])


class RelationalOperatorReplacementTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.RelationalOperatorReplacement()

    def test_lt(self):
        self.assert_mutation('x < y', ['x > y', 'x <= y'])

    def test_gt(self):
        self.assert_mutation('x > y', ['x < y', 'x >= y'])

    def test_lte(self):
        self.assert_mutation('x <= y', ['x >= y', 'x < y'])

    def test_gte(self):
        self.assert_mutation('x >= y', ['x <= y', 'x > y'])

    def test_eq(self):
        self.assert_mutation('x == y', ['x != y'])

    def test_not_eq(self):
        self.assert_mutation('x != y', ['x == y'])


class SliceIndexRemoveTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.SliceIndexRemove()

    def test_slice_indexes_remove(self):
        self.assert_mutation('x[1:2:3]', ['x[:2:3]', 'x[1::3]', 'x[1:2]'])


class ConditionalOperatorInsertionTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.ConditionalOperatorInsertion()

    def test_negate_while_condition(self):
        self.assert_mutation("while x:\n    pass", ["while not x:\n    pass"])

    def test_negate_if_condition(self):
        self.assert_mutation('if x:\n    pass', ['if not x:\n    pass'])

    def test_negate_if_and_elif_condition(self):
        self.assert_mutation(
            'if x:' + EOL + INDENT + 'pass' + EOL + 'elif y:' + EOL + INDENT + 'pass',
            [
                'if not x:' + EOL + INDENT + 'pass' + EOL + 'elif y:' + EOL + INDENT + 'pass',
                'if x:' + EOL + INDENT + 'pass' + EOL + 'elif not y:' + EOL + INDENT + 'pass',
            ],
            lines=[1, 3],
        )

    def test_in_to_not_in(self):
        self.assert_mutation('x in y', ['x not in y'])


class ConditionalOperatorDeletionTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.ConditionalOperatorDeletion()

    def test_not(self):
        self.assert_mutation('not x', ['x'])

    def test_not_in_to_in(self):
        self.assert_mutation('x not in y', ['x in y'])


class ExceptionSwallowingTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.ExceptionSwallowing()

    def test_swallow_exception(self):
        self.assert_mutation(utils.f("""
        try:
            pass
        except:
            raise
        """), [utils.f("""
        try:
            pass
        except:
            pass
        """)])

    def test_not_swallow_if_pass(self):
        self.assert_mutation(utils.f("""
        try:
            pass
        except:
            pass
        """), [])


class ExceptionHandlerDeletionTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.ExceptionHandlerDeletion()

    def test_delete_except(self):
        self.assert_mutation(
            'try:' + EOL + INDENT + PASS + EOL + 'except Z:' + EOL + INDENT + PASS,
            ['try:' + EOL + INDENT + PASS + EOL + 'except Z:' + EOL + INDENT + 'raise'],
        )

    def test_delete_two_except(self):
        self.assert_mutation(
            'try:' + EOL + INDENT + PASS + EOL + 'except Z:' + EOL
            + INDENT + PASS + EOL + 'except Y:' + EOL + INDENT + PASS,
            [
                'try:' + EOL + INDENT + PASS + EOL + 'except Z:' + EOL
                + INDENT + 'raise' + EOL + 'except Y:' + EOL + INDENT + PASS,
                'try:' + EOL + INDENT + PASS + EOL + 'except Z:' + EOL
                + INDENT + PASS + EOL + 'except Y:' + EOL + INDENT + 'raise'
            ],
        )

    def test_not_delete_if_raise(self):
        self.assert_mutation(utils.f("""
        try:
            pass
        except:
            raise
        """), [])


class DecoratorDeletionTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.DecoratorDeletion()

    def test_single_decorator_deletion(self):
        self.assert_mutation(utils.f("""
        @a
        def f():
            pass
        """), [utils.f("""
        def f():
            pass
        """)])

    def test_double_decorators_deletion(self):
        self.assert_mutation(utils.f("""
        @a
        @b
        def f():
            pass
        """), [utils.f("""
        def f():
            pass
        """)])

    def test_deletion_with_arguments(self):
        self.assert_mutation(utils.f("""
        @a(1)
        def f():
            pass
        """), [utils.f("""
        def f():
            pass
        """)])


class MutateOnlyCoveredNodesTest(OperatorTestCase):

    def test_not_covered_assign_node(self):
        self.assert_mutation('x = 1' + EOL + 'if False:' + EOL + INDENT + 'y = 2',
                             [PASS + EOL + 'if False:' + EOL + INDENT + 'y = 2'],
                             operator=operators.StatementDeletion(),
                             with_coverage=True)

    def test_not_covered_if_node(self):
        self.assert_mutation('if False:' + EOL + INDENT + 'if False:' + EOL + 2 * INDENT + PASS,
                             ['if not False:' + EOL + INDENT + 'if False:' + EOL + 2 * INDENT + PASS],
                             operator=operators.ConditionalOperatorInsertion(),
                             with_coverage=True)

    def test_not_covered_expr_node(self):
        self.assert_mutation('1 + 1' + EOL + 'if False:' + EOL + INDENT + '1 + 1',
                             ['1 - 1' + EOL + 'if False:' + EOL + INDENT + '1 + 1'],
                             operator=operators.ArithmeticOperatorReplacement(),
                             with_coverage=True)

    def test_not_covered_while_node(self):
        self.assert_mutation('while False:' + EOL + INDENT + 'while False:' + EOL + 2 * INDENT + PASS,
                             ['while not False:' + EOL + INDENT + 'while False:' + EOL + 2 * INDENT + PASS],
                             operator=operators.ConditionalOperatorInsertion(),
                             with_coverage=True)

    def test_not_covered_return_node(self):
        self.assert_mutation('def foo():' + EOL + INDENT + 'return' + EOL + INDENT + 'return' + EOL + 'foo()',
                             ['def foo():' + EOL + INDENT + 'pass' + EOL + INDENT + 'return' + EOL + 'foo()',
                              'def foo():' + EOL + INDENT + 'return' + EOL + INDENT + 'return' + EOL + 'pass'],
                             operator=operators.StatementDeletion(),
                             with_coverage=True)

    def test_not_covered_except_handler_node(self):
        self.assert_mutation('try:' + EOL + INDENT + 'raise' + EOL + 'except:' + EOL + INDENT + 'try:' + EOL +
                             2 * INDENT + PASS + EOL + INDENT + 'except:' + EOL + 2 * INDENT + PASS,
                             ['try:' + EOL + INDENT + 'raise' + EOL + 'except:' + EOL + INDENT + 'raise'],
                             operator=operators.ExceptionHandlerDeletion(),
                             with_coverage=True)


class OverridingMethodDeletionTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.OverridingMethodDeletion()

    def test_delete_overriding_method(self):
        self.assert_mutation(utils.f("""
        class A:
            def foo(self):
                pass
        class B(A):
            def foo(self):
                pass
        """), [utils.f("""
        class A:
            def foo(self):
                pass
        class B(A):
            pass
        """)], with_exec=True)

    def test_delete_overriding_method_in_inner_class(self):
        self.assert_mutation(utils.f("""
        class X:
            class A:
                def foo(self):
                    pass
            class B(A):
                def foo(self):
                    pass
        """), [utils.f("""
        class X:
            class A:
                def foo(self):
                    pass
            class B(A):
                pass
        """)], with_exec=True)

    def test_delete_overriding_method_when_base_class_from_other_module(self):
        self.assert_mutation(utils.f("""
        import ast
        class A(ast.NodeTransformer):
            def visit(self):
                pass
        """), [utils.f("""
        import ast
        class A(ast.NodeTransformer):
            pass
        """)], with_exec=True)


class OverriddenMethodCallingPositionChangeTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.OverriddenMethodCallingPositionChange()

    def test_change_position_from_first_to_last(self):
        self.assert_mutation(utils.f("""
        class A:
            def foo(self):
                super().foo()
                pass
        """), [utils.f("""
        class A:
            def foo(self):
                pass
                super().foo()
        """)])

    def test_change_position_from_last_to_first(self):
        self.assert_mutation(utils.f("""
        class A:
            def foo(self):
                pass
                super().foo()
        """), [utils.f("""
        class A:
            def foo(self):
                super().foo()
                pass
        """)])

    def test_not_change_position_if_single_statement(self):
        self.assert_mutation(utils.f("""
        class A:
            def foo(self):
                super().foo()
        """), [])


class SuperCallingDeletionTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.SuperCallingDeletion()

    def test_change_position_from_first_to_last(self):
        self.assert_mutation(utils.f("""
        class A:
            def foo(self, x):
                super().foo(x)
        """), [utils.f("""
        class A:
            def foo(self, x):
                pass
        """)])


class SuperCallingInsertTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.SuperCallingInsert()

    def test_change_position_from_first_to_last(self):
        self.assert_mutation(utils.f("""
        class B:
            def foo(self, x, y=1, *args, **kwargs):
                pass
        class A(B):
            def foo(self, x, y=1, *args, **kwargs):
                pass
        """), [utils.f("""
        class B:
            def foo(self, x, y=1, *args, **kwargs):
                pass
        class A(B):
            def foo(self, x, y=1, *args, **kwargs):
                super().foo(x, y=1, *args, **kwargs)
                pass
        """)], with_exec=True)


class HidingVariableDeletionTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.HidingVariableDeletion()

    def test_delete_variable(self):
        self.assert_mutation(utils.f("""
        class B:
            x = 1
        class A(B):
            x = 2
        """), [utils.f("""
        class B:
            x = 1
        class A(B):
            pass
        """)], with_exec=True)

    def test_delete_variable_if_one_hiding_in_two_targets(self):
        self.assert_mutation(utils.f("""
        class B:
            x = 1
        class A(B):
            (x, y) = (2, 3)
        """), [utils.f("""
        class B:
            x = 1
        class A(B):
            y = 3
        """)], with_exec=True)

    def test_delete_variable_if_one_hiding_in_three_targets(self):
        self.assert_mutation(utils.f("""
        class B:
            x = 1
        class A(B):
            (x, y, z) = (2, 3, 4)
        """), [utils.f("""
        class B:
            x = 1
        class A(B):
            (y, z) = (3, 4)
        """)], with_exec=True)

    def test_delete_variable_if_two_hiding_in_two_targets(self):
        self.assert_mutation(utils.f("""
        class B:
            (x, y) = (1, 2)
        class A(B):
            (x, y) = (3, 4)
        """), [utils.f("""
        class B:
            (x, y) = (1, 2)
        class A(B):
            pass
        """)], with_exec=True)


class BreakContinueReplacementTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.BreakContinueReplacement()

    def test_replace_break_by_continue(self):
        self.assert_mutation(utils.f("""
        for x in y:
            break
        """), [utils.f("""
        for x in y:
            continue
        """)])

    def test_replace_continue_by_break(self):
        self.assert_mutation(utils.f("""
        for x in y:
            continue
        """), [utils.f("""
        for x in y:
            break
        """)])


class SelfVariableDeletionTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.SelfVariableDeletion()

    def test_self_deletion_with_attribute(self):
        self.assert_mutation('self.x', ['x'])

    def test_self_deletion_with_method(self):
        self.assert_mutation('self.f()', ['f()'])

    def test_self_deletion_with_multi_attribute(self):
        self.assert_mutation('self.x.y.z', ['x.y.z'])

    def test_self_deletion_with_multi_attribute_after_method(self):
        self.assert_mutation('self.f().x.y.z', ['f().x.y.z'])


class StaticmethodDecoratorInsertionTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.StaticmethodDecoratorInsertion()

    def test_add_staticmethod_decorator(self):
        self.assert_mutation(
            utils.f("""
            class X:
                def f():
                    pass
            """),
            utils.f("""
            class X:
                @staticmethod
                def f():
                    pass
            """)
        )

    def test_not_add_if_already_has_staticmethod(self):
        self.assert_no_mutation(utils.f("""
            class X:
                @staticmethod
                def f():
                    pass
        """))


class StatementDeletionTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.StatementDeletion()

    def test_return_deletion(self):
        self.assert_mutation('def f():' + EOL + INDENT + 'return 1', ['def f():' + EOL + INDENT + PASS])

    def test_assign_deletion(self):
        self.assert_mutation('x = 1', [PASS])

    def test_fuction_call_deletion(self):
        self.assert_mutation('f()', ['pass'])

    def test_assign_with_call_deletion(self):
        self.assert_mutation('x = f()', ['pass'])

    def test_not_mutate_docstring(self):
        self.assert_mutation('""""doc"""', [])


class ZeroIterationLoopTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.ZeroIterationLoop()

    def test_for_zero_iteration(self):
        self.assert_mutation('for x in y:' + EOL + INDENT + PASS, ['for x in y:' + EOL + INDENT + 'break'])

    def test_multiline_for_zero_iteration(self):
        self.assert_mutation(
            'for x in y:' + EOL + INDENT + PASS + EOL + INDENT + PASS,
            ['for x in y:' + EOL + INDENT + 'break'],
        )

    def test_while_zero_iteration(self):
        self.assert_mutation('while x:' + EOL + INDENT + PASS, ['while x:' + EOL + INDENT + 'break'])


class OneIterationLoopTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.OneIterationLoop()

    def test_for_one_iteration(self):
        self.assert_mutation(
            'for x in y:' + EOL + INDENT + PASS,
            ['for x in y:' + EOL + INDENT + PASS + EOL + INDENT + 'break'],
        )

    def test_while_one_iteration(self):
        self.assert_mutation(
            'while x:' + EOL + INDENT + PASS,
            ['while x:' + EOL + INDENT + PASS + EOL + INDENT + 'break'],
        )

    def test_double_mutation(self):
        self.assert_mutation(utils.f("""
        while x:
            pass
        for x in y:
            pass
        """), [
            utils.f("""
            while x:
                pass
                break
            for x in y:
                pass
            """),
            utils.f("""
            while x:
                pass
            for x in y:
                pass
                break
            """),
        ])


class ReverseIterationLoopTest(OperatorTestCase):

    @classmethod
    def setUpClass(cls):
        cls.op = operators.ReverseIterationLoop()

    def test_for_reverse(self):
        self.assert_mutation(
            'for x in y:' + EOL + INDENT + PASS,
            ['for x in reversed(y):' + EOL + INDENT + PASS],
        )
