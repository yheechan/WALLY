import random
import sys
import os
import time
from copy import deepcopy

from mutpy import views, utils


class TestsFailAtOriginal(Exception):

    def __init__(self, result=None):
        self.result = result


class MutationScore:

    def __init__(self):
        self.killed_mutants = 0
        self.timeout_mutants = 0
        self.incompetent_mutants = 0
        self.survived_mutants = 0
        self.covered_nodes = 0
        self.all_nodes = 0

    def count(self):
        bottom = self.all_mutants - self.incompetent_mutants
        return (((self.killed_mutants + self.timeout_mutants) / bottom) * 100) if bottom else 0

    def inc_killed(self):
        self.killed_mutants += 1

    def inc_timeout(self):
        self.timeout_mutants += 1

    def inc_incompetent(self):
        self.incompetent_mutants += 1

    def inc_survived(self):
        self.survived_mutants += 1

    def update_coverage(self, covered_nodes, all_nodes):
        self.covered_nodes += covered_nodes
        self.all_nodes += all_nodes

    @property
    def all_mutants(self):
        return self.killed_mutants + self.timeout_mutants + self.incompetent_mutants + self.survived_mutants


class MutationController(views.ViewNotifier):

    def __init__(self, runner_cls, project_dir, target_loader, test_loader, views, mutant_generator, pytest_function_timeout, pytest_session_timeout,
                 timeout_factor=5, disable_stdout=False, mutate_covered=False, mutation_number=None, test_results=None,
                 ):
        super().__init__(views)
        self.project_dir = project_dir
        self.target_loader = target_loader
        self.test_loader = test_loader
        self.mutant_generator = mutant_generator
        self.timeout_factor = timeout_factor
        self.stdout_manager = utils.StdoutManager(disable_stdout)
        self.mutation_number = mutation_number
        self.runner = runner_cls(self.test_loader, self.timeout_factor, self.stdout_manager, mutate_covered)
        self.runner.set_function_timeout(pytest_function_timeout)
        self.runner.set_session_timeout(pytest_session_timeout)
        self.test_results = test_results
        # key: filename1
            # lineno: 
                # m1: p2f f2p
                # m2: p2f f2p
                # ...
            # lineno: ...
        # filename2 ...
        self.mbfl_results = {}

        # GET LINES EXECUTED BY FAILING TCS PER EACH TARGET SOURCE CODE FILES
        self.failing_lines = {}
        self.og_passing_tcs = []
        self.og_failing_tcs = []
        for tc_result in test_results:
            tc_outcome = test_results[tc_result]
        
            # ORGANIZE PASSING AND FAILING TCS
            if tc_outcome['test result'] == 'P':
                self.og_passing_tcs.append(
                    (tc_outcome['test_file'],
                    tc_outcome['test function'])
                )
                continue

            self.og_failing_tcs.append(
                (tc_outcome['test_file'],
                tc_outcome['test function'])
            )

            tc_coverage = tc_outcome['coverage']
            for filename in tc_coverage['files']:
                if filename not in self.failing_lines:
                    self.failing_lines[filename] = set()
                
                for line in tc_coverage['files'][filename]['executed_lines']:
                    self.failing_lines[filename].add(line)
        


    def run(self):
        self.notify_initialize(self.target_loader.names, self.test_loader.names)
        try:
            timer = utils.Timer()
            self.run_mutation_process()
            self.notify_end(self.score, timer.stop())
        except TestsFailAtOriginal as error:
            self.notify_original_tests_fail(error.result)
            sys.exit(-1)
        except utils.ModulesLoaderException as error:
            self.notify_cant_load(error.name, error.exception)
            sys.exit(-2)
        
        return self.mbfl_results

    def run_mutation_process(self):
        try:
            test_modules, total_duration, number_of_tests = self.load_and_check_tests()

            self.notify_passed(test_modules, number_of_tests)
            self.notify_start()

            self.score = MutationScore()

            for target_module, to_mutate in self.target_loader.load([module for module, *_ in test_modules]):
                self.mutate_module(target_module, to_mutate, total_duration)
        except KeyboardInterrupt:
            pass

    def load_and_check_tests(self):
        test_modules = []
        number_of_tests = 0
        total_duration = 0
        for test_module, target_test in self.test_loader.load():
            result, duration = self.run_test(test_module, target_test)
            if result.was_successful():
                test_modules.append((test_module, target_test, duration))
            # else:
            #     raise TestsFailAtOriginal(result)
            number_of_tests += result.tests_run()
            total_duration += duration

        return test_modules, total_duration, number_of_tests

    def run_test(self, test_module, target_test):
        return self.runner.run_test(test_module, target_test)

    @utils.TimeRegister
    def mutate_module(self, target_module, to_mutate, total_duration):
        target_ast = self.create_target_ast(target_module)
        coverage_injector, coverage_result = self.inject_coverage(target_ast, target_module)
        if coverage_injector:
            self.score.update_coverage(*coverage_injector.get_result())
        
        # STOP HERE AND ACCUMULATE MUTANTS
        # SHUFFLE THE MUTANTS
        mutant_list = []
        for mutations, mutant_ast in self.mutant_generator.mutate(target_ast, to_mutate, coverage_injector,
                                                                  module=target_module, failing_lines=self.failing_lines):
            mutant_list.append((mutations, deepcopy(mutant_ast)))
        random.shuffle(mutant_list)

        # line2mutants = {}
        # run the mutants
        for mutations, mutant_ast in mutant_list:
            # # THIS CODE LIMITS MUTATION TESTING ON A SINGLE LINE TO MAX_NUM_MUTANTS_PER_LINE
            # if mutant_lineno not in line2mutants:
            #     line2mutants[mutant_lineno] = 0
            # line2mutants[mutant_lineno] += 1
            # if line2mutants[mutant_lineno] > 5:
            #     continue


            mutation_number = self.score.all_mutants + 1
            if self.mutation_number and self.mutation_number != mutation_number:
                self.score.inc_incompetent()
                continue
            self.notify_mutation(mutation_number, mutations, target_module, mutant_ast)
            mutant_module = self.create_mutant_module(target_module, mutant_ast)
            if mutant_module:
                self.run_tests_with_mutant(total_duration, mutant_module, mutations, coverage_result)
            else:
                self.score.inc_incompetent()

    def inject_coverage(self, target_ast, target_module):
        return self.runner.inject_coverage(target_ast, target_module)

    @utils.TimeRegister
    def create_target_ast(self, target_module):
        with open(target_module.__file__) as target_file:
            return utils.create_ast(target_file.read())

    @utils.TimeRegister
    def create_mutant_module(self, target_module, mutant_ast):
        try:
            with self.stdout_manager:
                return utils.create_module(
                    ast_node=mutant_ast,
                    module_name=target_module.__name__
                )
        except BaseException as exception:
            self.notify_incompetent(0, exception, tests_run=0)
            return None

    def run_tests_with_mutant(self, total_duration, mutant_module, mutations, coverage_result):
        result, duration = self.runner.run_tests_with_mutant(total_duration, mutant_module, mutations, coverage_result)

        if result == None:
            self.update_score_and_notify_views(None, duration)
            return

        # RECORD P2F AND F2P OF THIS MUTANT
        # IN WHICH THE MUTANT IS OF A CERTAIN LINENO OF A CERTAIN FILE
        mutant_lineno = mutations[0].node.lineno
        mutant_filename = mutant_module.__file__
        if mutant_filename not in self.mbfl_results:
            self.mbfl_results[mutant_filename] = {}
            self.mbfl_results[mutant_filename]["lines"] = {}

        if mutant_lineno not in self.mbfl_results[mutant_filename]["lines"]:
            self.mbfl_results[mutant_filename]["lines"][mutant_lineno] = {}
            self.mbfl_results[mutant_filename]["lines"][mutant_lineno]['mutants'] = []
            self.mbfl_results[mutant_filename]["lines"][mutant_lineno]['total_features'] = {
                'total_p2f': 0,
                'total_f2p': 0
            }
            self.mbfl_results[mutant_filename]["lines"][mutant_lineno]['total_features']['mutant_cnt'] = 0
        
        # CALCULATE P2F AND F2P
        p2f = 0
        f2p = 0
        p2p = 0
        f2f = 0
        for passing in result.passings:
            #print("passing case: ", passing.name)
            info = passing.name.split('::')
            passing_file_list = (info[0].split('/'))[1:]
            p_filename = os.path.join(self.project_dir, *passing_file_list)
            #P_filename = os.path.abspath(info[0])
            p_funcname = info[1]

            for og_passing in self.og_passing_tcs:
                # if p_filename == og_passing[0] and p_funcname == og_passing[1]:
                if (p_filename in og_passing[0] or p_filename == og_passing[0]) and p_funcname == og_passing[1]:
                    p2p += 1
                    break
            
            for og_failing in self.og_failing_tcs:
                # if p_filename == og_failing[0] and p_funcname == og_failing[1]:
                if (p_filename in og_failing[0] or p_filename == og_failing[0]) and p_funcname == og_failing[1]:
                    f2p += 1
                    break
        
        for failing in result.failings:
            #print("failing case: ", failing.name)
            info = failing.name.split('::')
            failing_file_list = (info[0].split('/'))[1:]
            f_filename = os.path.join(self.project_dir, *failing_file_list)
            #f_filename = os.path.abspath(info[0])
            f_funcname = info[1]

            for og_passing in self.og_passing_tcs:
                # if f_filename == og_passing[0] and f_funcname == og_passing[1]:
                if (f_filename in og_passing[0] or f_filename == og_passing[0]) and f_funcname == og_passing[1]:
                    p2f += 1
                    break
            
            for og_failing in self.og_failing_tcs:
                # if f_filename == og_failing[0] and f_funcname == og_failing[1]:
                if (f_filename in og_failing[0] or f_filename == og_failing[0]) and f_funcname == og_failing[1]:
                    f2f += 1
                    break
        
        self.mbfl_results[mutant_filename]["lines"][mutant_lineno]['mutants'].append({
            'p2f': p2f,
            'f2p': f2p,
            'p2p': p2p,
            'f2f': f2f
        })

        self.mbfl_results[mutant_filename]["lines"][mutant_lineno]['total_features']['total_p2f'] += p2f
        self.mbfl_results[mutant_filename]["lines"][mutant_lineno]['total_features']['total_f2p'] += f2p
        self.mbfl_results[mutant_filename]["lines"][mutant_lineno]['total_features']['mutant_cnt'] += 1

        self.update_score_and_notify_views(result, duration)

    def update_score_and_notify_views(self, result, mutant_duration):
        if not result:
            self.update_timeout_mutant(mutant_duration)
        elif result.is_incompetent:
            self.update_incompetent_mutant(result, mutant_duration)
        elif result.is_survived:
            self.update_survived_mutant(result, mutant_duration)
        else:
            self.update_killed_mutant(result, mutant_duration)

    def update_timeout_mutant(self, duration):
        self.notify_timeout(duration)
        self.score.inc_timeout()

    def update_incompetent_mutant(self, result, duration):
        self.notify_incompetent(duration, result.exception, result.tests_run)
        self.score.inc_incompetent()

    def update_survived_mutant(self, result, duration):
        self.notify_survived(duration, result.tests_run)
        self.score.inc_survived()

    def update_killed_mutant(self, result, duration):
        self.notify_killed(duration, result.killer, result.exception_traceback, result.tests_run)
        self.score.inc_killed()


class HOMStrategy:

    def __init__(self, order=2):
        self.order = order

    def remove_bad_mutations(self, mutations_to_apply, available_mutations, allow_same_operators=True):
        for mutation_to_apply in mutations_to_apply:
            for available_mutation in available_mutations[:]:
                if mutation_to_apply.node == available_mutation.node or \
                        mutation_to_apply.node in available_mutation.node.children or \
                        available_mutation.node in mutation_to_apply.node.children or \
                        (not allow_same_operators and mutation_to_apply.operator == available_mutation.operator):
                    available_mutations.remove(available_mutation)


class FirstToLastHOMStrategy(HOMStrategy):
    name = 'FIRST_TO_LAST'

    def generate(self, mutations):
        mutations = mutations[:]
        while mutations:
            mutations_to_apply = []
            index = 0
            available_mutations = mutations[:]
            while len(mutations_to_apply) < self.order and available_mutations:
                try:
                    mutation = available_mutations.pop(index)
                    mutations_to_apply.append(mutation)
                    mutations.remove(mutation)
                    index = 0 if index == -1 else -1
                except IndexError:
                    break
                self.remove_bad_mutations(mutations_to_apply, available_mutations)
            yield mutations_to_apply


class EachChoiceHOMStrategy(HOMStrategy):
    name = 'EACH_CHOICE'

    def generate(self, mutations):
        mutations = mutations[:]
        while mutations:
            mutations_to_apply = []
            available_mutations = mutations[:]
            while len(mutations_to_apply) < self.order and available_mutations:
                try:
                    mutation = available_mutations.pop(0)
                    mutations_to_apply.append(mutation)
                    mutations.remove(mutation)
                except IndexError:
                    break
                self.remove_bad_mutations(mutations_to_apply, available_mutations)
            yield mutations_to_apply


class BetweenOperatorsHOMStrategy(HOMStrategy):
    name = 'BETWEEN_OPERATORS'

    def generate(self, mutations):
        usage = {mutation: 0 for mutation in mutations}
        not_used = mutations[:]
        while not_used:
            mutations_to_apply = []
            available_mutations = mutations[:]
            available_mutations.sort(key=lambda x: usage[x])
            while len(mutations_to_apply) < self.order and available_mutations:
                mutation = available_mutations.pop(0)
                mutations_to_apply.append(mutation)
                if not usage[mutation]:
                    not_used.remove(mutation)
                usage[mutation] += 1
                self.remove_bad_mutations(mutations_to_apply, available_mutations, allow_same_operators=False)
            yield mutations_to_apply


class RandomHOMStrategy(HOMStrategy):
    name = 'RANDOM'

    def __init__(self, *args, shuffler=random.shuffle, **kwargs):
        super().__init__(*args, **kwargs)
        self.shuffler = shuffler

    def generate(self, mutations):
        mutations = mutations[:]
        self.shuffler(mutations)
        while mutations:
            mutations_to_apply = []
            available_mutations = mutations[:]
            while len(mutations_to_apply) < self.order and available_mutations:
                try:
                    mutation = available_mutations.pop(0)
                    mutations_to_apply.append(mutation)
                    mutations.remove(mutation)
                except IndexError:
                    break
                self.remove_bad_mutations(mutations_to_apply, available_mutations)
            yield mutations_to_apply


hom_strategies = [
    BetweenOperatorsHOMStrategy,
    EachChoiceHOMStrategy,
    FirstToLastHOMStrategy,
    RandomHOMStrategy,
]


class FirstOrderMutator:

    def __init__(self, operators, percentage=100):
        self.operators = operators
        self.sampler = utils.RandomSampler(percentage)

    def mutate(self, target_ast, to_mutate=None, coverage_injector=None, module=None, failing_lines=None):
        for op in utils.sort_operators(self.operators):
            for mutation, mutant in op().mutate(target_ast, to_mutate, self.sampler, coverage_injector, module=module, failing_lines=failing_lines):
                yield [mutation], mutant


class HighOrderMutator(FirstOrderMutator):

    def __init__(self, *args, hom_strategy=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.hom_strategy = hom_strategy or FirstToLastHOMStrategy(order=2)

    def mutate(self, target_ast, to_mutate=None, coverage_injector=None, module=None):
        mutations = self.generate_all_mutations(coverage_injector, module, target_ast, to_mutate)
        for mutations_to_apply in self.hom_strategy.generate(mutations):
            generators = []
            applied_mutations = []
            mutant = target_ast
            for mutation in mutations_to_apply:
                generator = mutation.operator().mutate(
                    mutant,
                    to_mutate=to_mutate,
                    sampler=self.sampler,
                    coverage_injector=coverage_injector,
                    module=module,
                    only_mutation=mutation,
                )
                try:
                    new_mutation, mutant = generator.__next__()
                except StopIteration:
                    assert False, 'no mutations!'
                applied_mutations.append(new_mutation)
                generators.append(generator)
            yield applied_mutations, mutant
            self.finish_generators(generators)

    def generate_all_mutations(self, coverage_injector, module, target_ast, to_mutate):
        mutations = []
        for op in utils.sort_operators(self.operators):
            for mutation, _ in op().mutate(target_ast, to_mutate, None, coverage_injector, module=module):
                mutations.append(mutation)
        return mutations

    def finish_generators(self, generators):
        for generator in reversed(generators):
            try:
                generator.__next__()
            except StopIteration:
                continue
            assert False, 'too many mutations!'
