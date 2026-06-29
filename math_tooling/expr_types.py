from __future__ import annotations
from abc import ABC, abstractmethod

class Expr(ABC):
    sub_nodes: list[Expr]

    @property
    @abstractmethod
    def precedence(self) -> int:
        ...

    @abstractmethod
    def diff(self, var) -> Expr:
        ...

    @abstractmethod
    def eval(self, var_dict) -> float:
        ...
    
    @abstractmethod
    def simplify(self) -> Expr:
        ...

    @abstractmethod
    def __str__(self):
        ...

    def get_var_dependencies(self) -> set[Expr]:
        if len(self.sub_nodes) == 0:
            return set()
        dependencies = self.sub_nodes[0].get_var_dependencies()
        for i in range(1, len(self.sub_nodes)):
            dependencies.update(self.sub_nodes[i].get_var_dependencies())
        return dependencies

    def __init__(self, *args: Expr):
        self.sub_nodes = list(args)
        

class Unary(Expr):
    precedence = 4

    def __init__(self, *args: Expr):
        super().__init__(*args)
        assert len(self.sub_nodes) == 1

class Binary(Expr):
    def __init__(self, *args: Expr):
        super().__init__(*args)
        assert len(self.sub_nodes) == 2

class Ternary(Expr):
    def __init__(self, *args: Expr):
        super().__init__(*args)
        assert len(self.sub_nodes) == 3