import event

class Expression:
    def __init__(self, untyped_expr: str) -> None:
        self.expr = untyped_expr
        self.type = None

    def __str__(self) -> str:
        return self.expr

    def __eq__(self, __o: object) -> bool:
        pass

    def type(self) -> str:
        return self.type

    def conjuncts(self):
        pass

    def var(self):
        pass
    
    def get_event(self):
        pass

    def bound(self):
        pass

    def op_str(self):
        pass

    # def format(self):
    #     pass

class TrueExpression(Expression):
    def __init__(self, expr: str) -> None:
        super().__init__(expr)
        assert self.expr == 'True'
        self.type = 'True'

    def __eq__(self, __o: object) -> bool:
        if type(__o) == TrueExpression:
            return self.expr == __o.expr 
        else:
            return False

   
    def conjuncts(self):
        return []

    def var(self):
        return None
    
    def get_event(self):
        raise TypeError('expression.py: event not defined for TrueExpression')

    def bound(self):
        return self.value

    def op_str(self):
        raise TypeError('expression.py: op_str not defined for TrueExpression')

class IntExpression(Expression):
    def __init__(self, v: int) -> None:
        super().__init__(str(v))
        if type(v) != int:
            raise TypeError("expected integer as an input")
        self.value = v
        self.type = 'int'

    def __eq__(self, __o: object) -> bool:
        # assert type(__o) == IntExpression
        if type(__o) == IntExpression:
            return self.value == __o.value
        else:
            return False

    def conjuncts(self):
        raise TypeError('expression.py: conjuncts not defined for IntExpression')
    
    def var(self):
        return None
    
    def get_event(self):
        raise TypeError('expression.py: event not defined for IntExpression')

    def bound(self):
        return self.value

    def op_str(self):
        raise TypeError('expression.py: op_str not defined for IntExpression')


class VarExpression(Expression):
    def __init__(self, v: str) -> None:
        super().__init__(v)
        if type(v) != str:
            raise TypeError("expected string as an input")
        self.type = 'str'
    
    def __eq__(self, __o: object) -> bool:
        if type(__o) == VarExpression:
            return self.expr == __o.expr
        else:
            return False

    def conjuncts(self):
        raise TypeError('expression.py: conjuncts not defined for VarExpression')

    def var(self):
        return event.Event(self.expr)
    
    def get_event(self):
        pass

    def bound(self):
        raise TypeError('expression.py: bound not defined for VarExpression')

    def op_str(self):
        raise TypeError('expression.py: op_str not defined for VarExpression')
    

class SimpleExpression(Expression):
    def __init__(self, v: str) -> None:
        super().__init__(v)
        if '<=' in v:
            self.cmp = 'le'
            v_str = v.split('<=')
        elif '<' in v:
            self.cmp = 'lt'
            v_str = v.split('<')
        elif '>=' in v:
            self.cmp = 'ge'
            v_str = v.split('>=')
        elif '>' in v:
            self.cmp = 'gt'
            v_str = v.split('>')
        elif '==' in v:
            self.cmp = 'eq'
            v_str = v.split('==')
        else:
            # print(v)
            raise ValueError('expression.py: no eligible operator found')

        try:
            self.event, self.value = event.Event(v_str[0]), IntExpression(int(v_str[1]))
        except:
            self.event, self.value = event.Event(v_str[1]), IntExpression(int(v_str[0]))
                
        self.type = 'simple-constraint'
    
    
    def __eq__(self, __o: object) -> bool:
        if type(__o) == SimpleExpression:
            return self.get_event() == __o.get_event() and self.op_str() == __o.op_str() and self.bound() == __o.bound()
        elif type(__o) == ConjExpression:
            for j in range(__o.nconjuncts):
                if not self == __o.list_of_constraints[j]:
                    return False
            else:
                return True
        else:
            return False


    def conjuncts(self):
        return [self]

    def var(self):
        return self.event

    def get_event(self):
        return self.event

    def bound(self):
        return self.value.value #returns an integer

    def op_str(self):
        return self.cmp


class ConjExpression(Expression):
    def __init__(self, v) -> None:
        self.type = 'conjunctive-constraint'
        self.list_of_constraints = []
        if type(v) == str:
            super().__init__(v)
            v_str = v.split('&&')
            for each in v_str:
                self.list_of_constraints.append(SimpleExpression(each))
        elif type(v) == tuple:
            self.type = 'conjunctive-constraint'
            # v here will be a tuple of simple constraints
            for r in v:
                if r.type == 'simple-constraint':
                    self.list_of_constraints.append(r)
                else:
                    r_str = str(r).split('&&')
                    if len(r_str) == 0:
                        raise TypeError('r must be a conjunction')
                    for region in r_str:
                        self.list_of_constraints.append(SimpleExpression(region)) 
            self.expr = '&&'.join(list(map(str, self.list_of_constraints)))
        self.nconjuncts = len(self.list_of_constraints)

    def __iter__(self):
        return SimpleExpressionIter(self)    

    def __eq__(self, __o: object) -> bool:
        if type(__o) == ConjExpression:
            for i in range(self.nconjuncts):
                for j in range(__o.nconjuncts):
                    if self.list_of_constraints[i] == __o.list_of_constraints[j]:
                        break
                else:
                    return False
            return True
        elif type(__o) == SimpleExpression:
            for i in range(self.nconjuncts):
                if self.list_of_constraints[i] != __o:
                    return False
            return True
        else:
            return False
    
    def conjuncts(self):
        return self.list_of_constraints

    def var(self):
        raise TypeError('expression.py: var not defined for ConjExpression')
    
    def get_event(self):
        raise TypeError("expression.py: get_event not defined for ConjExpression")

    def bound(self):
        raise TypeError("expression.py: bound not defined for ConjExpression")

    def op_str(self):
        raise TypeError("expression.py: op_str not defined for ConjExpression")


class SimpleExpressionIter:
    def __init__(self, conj: ConjExpression) -> None:
        self._list_of_conjuncts = conj.list_of_constraints
        self.len = conj.nconjuncts
        self._current_index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._current_index < self.len:
            member = self._list_of_conjuncts[self._current_index]
            self._current_index += 1
            return member

        raise StopIteration


def typecheck(g: str) -> Expression:
    if g == 'True':
        return TrueExpression(g)
    elif '&&' in g:
        return ConjExpression(g)
    elif '<' in g or '>' in g or '=' in g:
        return SimpleExpression(g)
    else:
        try:
            return IntExpression(int(g))
        except:
            return VarExpression(g)


