"""SlopeScript test suite.

Run with:  python3 -m unittest discover tests
     or:   python3 -m pytest tests
"""

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slopescript import (  # noqa: E402
    AvalancheError,
    Interpreter,
    SlopeError,
    SlopeRuntimeError,
    SlopeSyntaxError,
    compile_source,
    format_value,
    run_source,
)


def run(code: str, snippet: bool = False) -> str:
    """Run a program and capture what it carves."""
    out = io.StringIO()
    with redirect_stdout(out):
        run_source(code, snippet=snippet)
    return out.getvalue()


def program(body: str) -> str:
    return f"summit\n{body}\nlodge\n"


class TestBasics(unittest.TestCase):
    def test_hello(self):
        self.assertEqual(run(program('carve "Hello, slopes!"')), "Hello, slopes!\n")

    def test_requires_summit(self):
        with self.assertRaises(SlopeSyntaxError):
            run('carve "no summit"\nlodge')

    def test_requires_lodge(self):
        with self.assertRaises(SlopeSyntaxError):
            run('summit\ncarve "no lodge"')

    def test_nothing_after_lodge(self):
        with self.assertRaises(SlopeSyntaxError):
            run('summit\nlodge\ncarve "too late"')

    def test_carve_multiple_args(self):
        self.assertEqual(run(program('carve "Run", 3, "done"')), "Run 3 done\n")

    def test_carve_blank_line(self):
        self.assertEqual(run(program('carve\ncarve "x"')), "\nx\n")

    def test_comments(self):
        code = program('// a comment\ncarve "ok" /* inline */\n/* multi\nline */\ncarve "done"')
        self.assertEqual(run(code), "ok\ndone\n")

    def test_string_escapes(self):
        self.assertEqual(run(program(r'carve "a\tb\nc \"quoted\""')), 'a\tb\nc "quoted"\n')

    def test_single_quoted_strings(self):
        self.assertEqual(run(program("carve 'hi there'")), "hi there\n")


class TestVariables(unittest.TestCase):
    def test_pack_and_reassign(self):
        code = program('pack x = 1\nx = x + 1\npack x = x * 10\ncarve x')
        self.assertEqual(run(code), "20\n")

    def test_compound_assignment(self):
        code = program('pack x = 10\nx += 5\nx -= 3\nx *= 2\nx /= 4\ncarve x')
        self.assertEqual(run(code), "6\n")

    def test_unpacked_variable_errors(self):
        with self.assertRaises(SlopeRuntimeError) as ctx:
            run(program('carve mystery'))
        self.assertIn("not packed", str(ctx.exception))

    def test_reassign_unpacked_errors(self):
        with self.assertRaises(SlopeRuntimeError):
            run(program('x = 5'))

    def test_booleans_and_whiteout(self):
        code = program('carve powder\ncarve ice\ncarve whiteout')
        self.assertEqual(run(code), "powder\nice\nwhiteout\n")


class TestOperators(unittest.TestCase):
    def test_arithmetic(self):
        code = program('carve 7 + 3, 7 - 3, 7 * 3, 7 / 2, 7 % 3, 2 ** 10')
        self.assertEqual(run(code), "10 4 21 3.5 1 1024\n")

    def test_even_division_is_whole(self):
        self.assertEqual(run(program('carve 10 / 2')), "5\n")

    def test_division_by_zero(self):
        with self.assertRaises(SlopeRuntimeError) as ctx:
            run(program('carve 1 / 0'))
        self.assertIn("Yard sale", str(ctx.exception))

    def test_string_concat(self):
        code = program('carve "vertical: " + 2500 + " feet"')
        self.assertEqual(run(code), "vertical: 2500 feet\n")

    def test_comparisons(self):
        code = program('carve 3 < 5, 3 > 5, 3 <= 3, 4 >= 5, 3 == 3, 3 != 3')
        self.assertEqual(run(code), "powder ice powder ice powder ice\n")

    def test_type_mismatch_comparison(self):
        with self.assertRaises(SlopeRuntimeError):
            run(program('carve 3 < "5"'))

    def test_logical_short_circuit(self):
        code = program('pack x = ice && boom()\ncarve x\npack y = powder || boom()\ncarve y')
        self.assertEqual(run(code), "ice\npowder\n")

    def test_not(self):
        self.assertEqual(run(program('carve !powder, !ice, !0, !1')), "ice powder powder ice\n")

    def test_in_operator(self):
        code = program('carve 2 in [1, 2, 3], "ski" in "skiing", "x" in {x: 1}')
        self.assertEqual(run(code), "powder powder powder\n")

    def test_unary_minus(self):
        self.assertEqual(run(program('carve -5 + 2, -(3 * 2)')), "-3 -6\n")

    def test_add_type_error(self):
        with self.assertRaises(SlopeRuntimeError):
            run(program('carve [1] + 2'))


class TestConditionals(unittest.TestCase):
    def test_green_taken(self):
        code = program("""
pack speed = 10
greenCircle (speed < 20)
  carve "easy"
blueSquare (speed < 40)
  carve "cruise"
blackDiamond
  carve "send"
runout
""")
        self.assertEqual(run(code), "easy\n")

    def test_blue_taken(self):
        code = program("""
pack speed = 30
greenCircle (speed < 20)
  carve "easy"
blueSquare (speed < 40)
  carve "cruise"
blackDiamond
  carve "send"
runout
""")
        self.assertEqual(run(code), "cruise\n")

    def test_black_taken(self):
        code = program("""
pack speed = 99
greenCircle (speed < 20)
  carve "easy"
blackDiamond
  carve "send"
runout
""")
        self.assertEqual(run(code), "send\n")

    def test_no_branch_taken(self):
        code = program("""
greenCircle (ice)
  carve "never"
runout
carve "after"
""")
        self.assertEqual(run(code), "after\n")

    def test_statement_after_runout_is_outside(self):
        code = program("""
pack hits = 0
greenCircle (ice)
  hits += 100
runout
hits += 1
carve hits
""")
        self.assertEqual(run(code), "1\n")

    def test_nested_conditionals(self):
        code = program("""
pack a = 1
greenCircle (a == 1)
  greenCircle (a > 0)
    carve "inner"
  runout
  carve "outer"
runout
""")
        self.assertEqual(run(code), "inner\nouter\n")

    def test_blue_without_green_errors(self):
        with self.assertRaises(SlopeSyntaxError):
            run(program('blueSquare (powder)\ncarve "x"\nrunout'))

    def test_unclosed_block_errors(self):
        with self.assertRaises(SlopeSyntaxError) as ctx:
            run(program('greenCircle (powder)\ncarve "x"'))
        self.assertIn("never closed", str(ctx.exception))


class TestLoops(unittest.TestCase):
    def test_gondola(self):
        code = program("""
pack laps = 0
gondola (laps < 3)
  laps += 1
  carve "lap", laps
runout
""")
        self.assertEqual(run(code), "lap 1\nlap 2\nlap 3\n")

    def test_liftline_rack(self):
        code = program("""
liftline skier in ["Ann", "Bo"]
  carve skier, "drops in"
runout
""")
        self.assertEqual(run(code), "Ann drops in\nBo drops in\n")

    def test_liftline_laps(self):
        code = program('liftline i in laps(3)\n  carve i\nrunout')
        self.assertEqual(run(code), "0\n1\n2\n")

    def test_liftline_text(self):
        code = program('liftline c in "ski"\n  carve c\nrunout')
        self.assertEqual(run(code), "s\nk\ni\n")

    def test_liftline_locker_iterates_keys(self):
        code = program('liftline k in {a: 1, b: 2}\n  carve k\nrunout')
        self.assertEqual(run(code), "a\nb\n")

    def test_bail(self):
        code = program("""
pack n = 0
gondola (powder)
  n += 1
  greenCircle (n == 3)
    bail
  runout
runout
carve n
""")
        self.assertEqual(run(code), "3\n")

    def test_sendit(self):
        code = program("""
liftline i in laps(5)
  greenCircle (i % 2 == 0)
    sendIt
  runout
  carve i
runout
""")
        self.assertEqual(run(code), "1\n3\n")

    def test_nested_loop_bail_only_inner(self):
        code = program("""
pack total = 0
liftline i in laps(3)
  liftline j in laps(10)
    greenCircle (j == 2)
      bail
    runout
    total += 1
  runout
runout
carve total
""")
        self.assertEqual(run(code), "6\n")

    def test_bail_outside_loop_errors(self):
        with self.assertRaises(SlopeRuntimeError):
            run(program('bail'))

    def test_liftline_over_number_errors(self):
        with self.assertRaises(SlopeRuntimeError) as ctx:
            run(program('liftline i in 5\n  carve i\nrunout'))
        self.assertIn("laps", str(ctx.exception))


class TestTricks(unittest.TestCase):
    def test_simple_trick(self):
        code = program("""
trick greet(name)
  carve "Shred on, " + name + "!"
nail
greet("Tony")
""")
        self.assertEqual(run(code), "Shred on, Tony!\n")

    def test_stomp_returns_value(self):
        code = program("""
trick double(n)
  stomp n * 2
nail
carve double(21)
""")
        self.assertEqual(run(code), "42\n")

    def test_trick_without_stomp_returns_whiteout(self):
        code = program('trick noop()\nnail\ncarve noop()')
        self.assertEqual(run(code), "whiteout\n")

    def test_recursion_fibonacci(self):
        code = program("""
trick fib(n)
  greenCircle (n < 2)
    stomp n
  runout
  stomp fib(n - 1) + fib(n - 2)
nail
carve fib(10)
""")
        self.assertEqual(run(code), "55\n")

    def test_local_scope(self):
        code = program("""
pack x = "global"
trick shadow()
  pack x = "local"
  carve x
nail
shadow()
carve x
""")
        self.assertEqual(run(code), "local\nglobal\n")

    def test_trick_can_update_global(self):
        code = program("""
pack total = 0
trick addRun(feet)
  total = total + feet
nail
addRun(2500)
addRun(1800)
carve total
""")
        self.assertEqual(run(code), "4300\n")

    def test_wrong_arg_count(self):
        with self.assertRaises(SlopeRuntimeError):
            run(program('trick f(a, b)\nnail\nf(1)'))

    def test_unknown_trick(self):
        with self.assertRaises(SlopeRuntimeError) as ctx:
            run(program('ollie()'))
        self.assertIn("Unknown trick", str(ctx.exception))

    def test_stomp_outside_trick_errors(self):
        with self.assertRaises(SlopeRuntimeError):
            run(program('stomp 5'))

    def test_recursion_limit(self):
        with self.assertRaises(SlopeRuntimeError) as ctx:
            run(program('trick forever()\nstomp forever()\nnail\nforever()'))
        self.assertIn("Avalanche risk", str(ctx.exception))

    def test_early_stomp_skips_rest(self):
        code = program("""
trick check(n)
  greenCircle (n > 0)
    stomp "positive"
  runout
  carve "still here"
  stomp "not positive"
nail
carve check(5)
carve check(-1)
""")
        self.assertEqual(run(code), "positive\nstill here\nnot positive\n")


class TestRacks(unittest.TestCase):
    def test_literal_and_index(self):
        code = program('pack r = [10, 20, 30]\ncarve r[0], r[2], r[-1]')
        self.assertEqual(run(code), "10 30 30\n")

    def test_index_assignment(self):
        code = program('pack r = [1, 2, 3]\nr[1] = 99\ncarve r')
        self.assertEqual(run(code), "[1, 99, 3]\n")

    def test_out_of_bounds(self):
        with self.assertRaises(SlopeRuntimeError) as ctx:
            run(program('pack r = [1]\ncarve r[5]'))
        self.assertIn("off the edge", str(ctx.exception))

    def test_push_pop_length(self):
        code = program("""
pack r = []
push(r, "a")
push(r, "b")
carve length(r)
carve pop(r)
carve r
""")
        self.assertEqual(run(code), "2\nb\n[\"a\"]\n")

    def test_rack_concat(self):
        self.assertEqual(run(program('carve [1, 2] + [3]')), "[1, 2, 3]\n")

    def test_nested_racks(self):
        code = program('pack grid = [[1, 2], [3, 4]]\ncarve grid[1][0]')
        self.assertEqual(run(code), "3\n")


class TestLockers(unittest.TestCase):
    def test_literal_and_access(self):
        code = program("""
pack lift = {name: "Big Red", capacity: 6}
carve lift.name
carve lift["capacity"]
""")
        self.assertEqual(run(code), "Big Red\n6\n")

    def test_member_assignment(self):
        code = program("""
pack lift = {name: "Old Blue"}
lift.name = "New Blue"
lift["speed"] = 5
carve lift.name, lift.speed
""")
        self.assertEqual(run(code), "New Blue 5\n")

    def test_keys_values_has(self):
        code = program("""
pack l = {a: 1, b: 2}
carve keys(l)
carve values(l)
carve has(l, "a"), has(l, "z")
""")
        self.assertEqual(run(code), '["a", "b"]\n[1, 2]\npowder ice\n')

    def test_missing_key_errors(self):
        with self.assertRaises(SlopeRuntimeError) as ctx:
            run(program('pack l = {a: 1}\ncarve l.zzz'))
        self.assertIn("no 'zzz'", str(ctx.exception))


class TestSkiPatrol(unittest.TestCase):
    def test_avalanche_caught(self):
        code = program("""
patrol
  avalanche "cornice collapse"
  carve "unreachable"
patroller (whoops)
  carve "patrol caught:", whoops
runout
carve "safe"
""")
        self.assertEqual(run(code), "patrol caught: cornice collapse\nsafe\n")

    def test_runtime_error_caught(self):
        code = program("""
patrol
  carve 1 / 0
patroller (whoops)
  carve "caught:", whoops
runout
""")
        self.assertEqual(run(code), "caught: Yard sale! Division by zero\n")

    def test_uncaught_avalanche(self):
        with self.assertRaises(AvalancheError):
            run(program('avalanche "runaway"'))

    def test_avalanche_carries_any_value(self):
        code = program("""
patrol
  avalanche {code: 404, msg: "trail not found"}
patroller (e)
  carve e.code, e.msg
runout
""")
        self.assertEqual(run(code), "404 trail not found\n")

    def test_nested_patrol(self):
        code = program("""
patrol
  patrol
    avalanche "inner"
  patroller (e)
    carve "inner caught", e
    avalanche "outer"
  runout
patroller (e)
  carve "outer caught", e
runout
""")
        self.assertEqual(run(code), "inner caught inner\nouter caught outer\n")


class TestBaseLodge(unittest.TestCase):
    def test_number_and_text(self):
        code = program('carve number("42") + 1\ncarve number("3.5")\ncarve text(7) + "!"')
        self.assertEqual(run(code), "43\n3.5\n7!\n")

    def test_number_failure(self):
        with self.assertRaises(SlopeRuntimeError):
            run(program('carve number("gnar")'))

    def test_math(self):
        code = program('carve abs(-5), basin(3.7), cornice(3.2), sqrt(16), round(3.456, 2)')
        self.assertEqual(run(code), "5 3 4 4 3.46\n")

    def test_min_max_sum(self):
        code = program('pack r = [3, 1, 2]\ncarve min(r), max(r), sum(r), min(5, 2), max(5, 2)')
        self.assertEqual(run(code), "1 3 6 2 5\n")

    def test_groom_and_flip(self):
        code = program('carve groom([3, 1, 2])\ncarve flip([1, 2, 3])\ncarve flip("ski")')
        self.assertEqual(run(code), "[1, 2, 3]\n[3, 2, 1]\niks\n")

    def test_text_functions(self):
        code = program("""
carve upper("gnar"), lower("GNAR"), trim("  x  ")
carve split("a,b,c", ",")
carve join(["a", "b"], "-")
carve replace("powpow", "pow", "ski")
carve startsWith("skiing", "ski"), endsWith("skiing", "ing")
""")
        self.assertEqual(run(code), 'GNAR gnar x\n["a", "b", "c"]\na-b\nskiski\npowder powder\n')

    def test_find_contains_slice(self):
        code = program("""
carve find([10, 20], 20), find([10], 99), find("skiing", "ing")
carve contains([1, 2], 2), contains("pow", "z")
carve slice([1, 2, 3, 4], 1, 3), slice("skiing", 0, 3)
""")
        self.assertEqual(run(code), "1 -1 3\npowder ice\n[2, 3] ski\n")

    def test_snowflake_range(self):
        code = program("""
liftline i in laps(20)
  pack n = snowflake(1, 6)
  greenCircle (n < 1 || n > 6)
    avalanche "out of range"
  runout
runout
carve "ok"
""")
        self.assertEqual(run(code), "ok\n")

    def test_type(self):
        code = program('carve type(1), type("x"), type([1]), type({a: 1}), type(powder), type(whiteout)')
        self.assertEqual(run(code), "number text rack locker condition whiteout\n")

    def test_aliases(self):
        code = program('carve floor(3.9), ceil(3.1), sort([2, 1])[0], reverse("ab"), tune("5") + 1')
        self.assertEqual(run(code), "3 4 1 ba 6\n")

    def test_wrong_arity_message(self):
        with self.assertRaises(SlopeRuntimeError) as ctx:
            run(program('carve abs(1, 2)'))
        self.assertIn("abs() takes 1", str(ctx.exception))

    def test_user_trick_shadows_builtin(self):
        code = program('trick abs(n)\nstomp "custom"\nnail\ncarve abs(-3)')
        self.assertEqual(run(code), "custom\n")


class TestFormatting(unittest.TestCase):
    def test_whole_floats_print_clean(self):
        self.assertEqual(format_value(3.0), "3")
        self.assertEqual(format_value(3.5), "3.5")

    def test_containers(self):
        self.assertEqual(format_value([1, "a", True, None]), '[1, "a", powder, whiteout]')
        self.assertEqual(format_value({"k": 1}), '{"k": 1}')


class TestSnippets(unittest.TestCase):
    def test_snippet_mode_needs_no_summit(self):
        self.assertEqual(run('carve "quick"', snippet=True), "quick\n")

    def test_snippet_mode_accepts_full_program(self):
        self.assertEqual(run(program('carve "full"'), snippet=True), "full\n")

    def test_state_persists_across_snippets(self):
        interp = Interpreter()
        out = io.StringIO()
        with redirect_stdout(out):
            run_source('pack x = 10', interp, snippet=True)
            run_source('carve x * 2', interp, snippet=True)
        self.assertEqual(out.getvalue(), "20\n")


class TestErrorReporting(unittest.TestCase):
    def test_syntax_error_has_line(self):
        try:
            compile_source('summit\npack = 5\nlodge')
            self.fail("expected syntax error")
        except SlopeSyntaxError as e:
            self.assertEqual(e.line, 2)

    def test_runtime_error_has_line(self):
        try:
            run(program('pack a = 1\ncarve missing'))
            self.fail("expected runtime error")
        except SlopeRuntimeError as e:
            self.assertEqual(e.line, 3)

    def test_unterminated_string(self):
        with self.assertRaises(SlopeSyntaxError) as ctx:
            compile_source('summit\ncarve "oops\nlodge')
        self.assertIn("closing quote", str(ctx.exception))

    def test_helpful_runout_hint(self):
        with self.assertRaises(SlopeSyntaxError) as ctx:
            compile_source('summit\nrunout\nlodge')
        self.assertIn("nothing to close", str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
