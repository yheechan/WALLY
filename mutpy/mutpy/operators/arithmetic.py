import ast

from mutpy.operators.base import MutationResign, MutationOperator, AbstractUnaryOperatorDeletion


class ArithmeticOperatorDeletion(AbstractUnaryOperatorDeletion):
    def get_operator_type(self):
        return ast.UAdd, ast.USub


class AbstractArithmeticOperatorReplacement(MutationOperator):
    def should_mutate(self, node):
        raise NotImplementedError()

    # name of the method changed from mutate_Add
    def mutate_Add_to_Sub(self, node):
        if self.should_mutate(node):
            return ast.Sub()
        raise MutationResign()

    # name of the method changed from mutate_Sub
    def mutate_Sub_to_Add(self, node):
        if self.should_mutate(node):
            return ast.Add()
        raise MutationResign()

    def mutate_Mult_to_Div(self, node):
        if self.should_mutate(node):
            return ast.Div()
        raise MutationResign()

    def mutate_Mult_to_FloorDiv(self, node):
        if self.should_mutate(node):
            return ast.FloorDiv()
        raise MutationResign()

    def mutate_Mult_to_Pow(self, node):
        if self.should_mutate(node):
            return ast.Pow()
        raise MutationResign()

    def mutate_Div_to_Mult(self, node):
        if self.should_mutate(node):
            return ast.Mult()
        raise MutationResign()

    def mutate_Div_to_FloorDiv(self, node):
        if self.should_mutate(node):
            return ast.FloorDiv()
        raise MutationResign()

    def mutate_FloorDiv_to_Div(self, node):
        if self.should_mutate(node):
            return ast.Div()
        raise MutationResign()

    def mutate_FloorDiv_to_Mult(self, node):
        if self.should_mutate(node):
            return ast.Mult()
        raise MutationResign()

    # name of the method changed from mutate_Mod
    def mutate_Mod_to_Mult(self, node):
        if self.should_mutate(node):
            return ast.Mult()
        raise MutationResign()

    # name of the method changed from mutate_Pow
    def mutate_Pow_to_Mult(self, node):
        if self.should_mutate(node):
            return ast.Mult()
        raise MutationResign()
    
     # The following methods are added to include the remaining arithmetic operators
    def mutate_Add_to_Mul(self, node):
        if self.should_mutate(node):
            return ast.Mult()
        raise MutationResign()
    
    def mutate_Add_to_Div(self, node):
        if self.should_mutate(node):
            return ast.Div()
        raise MutationResign()
    
    def mutate_Add_to_FloorDiv(self, node):
        if self.should_mutate(node):
            return ast.FloorDiv()
        raise MutationResign()
    
    def mutate_Add_to_Mod(self, node):
        if self.should_mutate(node):
            return ast.Mod()
        raise MutationResign()
    
    def mutate_Add_to_Pow(self, node):
        if self.should_mutate(node):
            return ast.Pow()
        raise MutationResign()
    
    def mutate_Sub_to_Mul(self, node):
        if self.should_mutate(node):
            return ast.Mult()
        raise MutationResign()
    
    def mutate_Sub_to_Div(self, node):
        if self.should_mutate(node):
            return ast.Div()
        raise MutationResign()
    
    def mutate_Sub_to_FloorDiv(self, node):
        if self.should_mutate(node):
            return ast.FloorDiv()
        raise MutationResign()
    
    def mutate_Sub_to_Mod(self, node):
        if self.should_mutate(node):
            return ast.Mod()
        raise MutationResign()
    
    def mutate_Sub_to_Pow(self, node):
        if self.should_mutate(node):
            return ast.Pow()
        raise MutationResign()
    
    def mutate_Mult_to_Add(self, node):
        if self.should_mutate(node):
            return ast.Add()
        raise MutationResign()
    
    def mutate_Mult_to_Sub(self, node):
        if self.should_mutate(node):
            return ast.Sub()
        raise MutationResign()
    
    def mutate_Mult_to_FloorDiv(self, node):
        if self.should_mutate(node):
            return ast.FloorDiv()
        raise MutationResign()
    
    def mutate_Mult_to_Mod(self, node):
        if self.should_mutate(node):
            return ast.Mod()
        raise MutationResign()
    
    def mutate_Mult_to_Pow(self, node):
        if self.should_mutate(node):
            return ast.Pow()
        raise MutationResign()
    
    def mutate_Div_to_Add(self, node):
        if self.should_mutate(node):
            return ast.Add()
        raise MutationResign()
    
    def mutate_Div_to_Sub(self, node):
        if self.should_mutate(node):
            return ast.Sub()
        raise MutationResign()
    
    def mutate_Div_to_Mod(self, node):
        if self.should_mutate(node):
            return ast.Mod()
        raise MutationResign()
    
    def mutate_Div_to_Pow(self, node):
        if self.should_mutate(node):
            return ast.Pow()
        raise MutationResign()
    
    def mutate_FloorDiv_to_Add(self, node):
        if self.should_mutate(node):
            return ast.Add()
        raise MutationResign()
    
    def mutate_FloorDiv_to_Sub(self, node):
        if self.should_mutate(node):
            return ast.Sub()
        raise MutationResign()
    
    def mutate_FloorDiv_to_Mod(self, node):
        if self.should_mutate(node):
            return ast.Mod()
        raise MutationResign()
    
    def mutate_FloorDiv_to_Pow(self, node):
        if self.should_mutate(node):
            return ast.Pow()
        raise MutationResign()
    
    def mutate_Mod_to_Add(self, node):
        if self.should_mutate(node):
            return ast.Add()
        raise MutationResign()
    
    def mutate_Mod_to_Sub(self, node):
        if self.should_mutate(node):
            return ast.Sub()
        raise MutationResign()
    
    def mutate_Mod_to_Mult(self, node):
        if self.should_mutate(node):
            return ast.Mult()
        raise MutationResign()
    
    def mutate_Mod_to_Div(self, node):
        if self.should_mutate(node):
            return ast.Div()
        raise MutationResign()
    
    def mutate_Mod_to_Pow(self, node):
        if self.should_mutate(node):
            return ast.Pow()
        raise MutationResign()
    
    def mutate_Pow_to_Add(self, node):
        if self.should_mutate(node):
            return ast.Add()
        raise MutationResign()
    
    def mutate_Pow_to_Sub(self, node):
        if self.should_mutate(node):
            return ast.Sub()
        raise MutationResign()
    
    def mutate_Pow_to_Mult(self, node):
        if self.should_mutate(node):
            return ast.Mult()
        raise MutationResign()
    
    def mutate_Pow_to_Div(self, node):
        if self.should_mutate(node):
            return ast.Div()
        raise MutationResign()
    
    def mutate_Pow_to_FloorDiv(self, node):
        if self.should_mutate(node):
            return ast.FloorDiv()
        raise MutationResign()
    
    def mutate_Pow_to_Mod(self, node):
        if self.should_mutate(node):
            return ast.Mod()
        raise MutationResign()



class ArithmeticOperatorReplacement(AbstractArithmeticOperatorReplacement):
    def should_mutate(self, node):
        return not isinstance(node.parent, ast.AugAssign)

    def mutate_USub(self, node):
        return ast.UAdd()

    def mutate_UAdd(self, node):
        return ast.USub()
