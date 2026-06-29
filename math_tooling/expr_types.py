from __future__ import annotations
from abc import ABC, abstractmethod

class Expr(ABC):
    sub_nodes: list[Expr]

    @property
    @abstractmethod
    def precedence(self) -> int:
        ...

    @abstractmethod
    def diff(self) -> Expr:
        ...

    @abstractmethod
    def eval(self, point: float, var) -> float:
        ...
    
    @abstractmethod
    def simplify(self) -> Expr:
        ...

    @abstractmethod
    def __str__(self):
        ...

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