"""
expr_types.py

Defines the abstract syntax tree (AST) used by the symbolic mathematics engine.

Every symbolic expression inherits from ``Expr``. Expressions are immutable
conceptually (although some simplification routines may construct new nodes)
and are composed recursively through child expressions stored in ``sub_nodes``.

This module also provides helper base classes for expressions with fixed
arities (Unary, Binary, and Ternary).
"""

from __future__ import annotations
from abc import ABC, abstractmethod


class Expr(ABC):
    """
    Base class for every symbolic expression.

    Each expression is represented as a node in an abstract syntax tree (AST).
    Child expressions are stored in ``sub_nodes`` and may themselves contain
    additional expressions.

    Every subclass must implement symbolic differentiation, numerical
    evaluation, simplification, string formatting, and define its operator
    precedence.
    """

    sub_nodes: list[Expr]

    @property
    @abstractmethod
    def precedence(self) -> int:
        """
        Operator precedence used when converting an expression to a string.

        Higher values bind more tightly and therefore require fewer
        parentheses when printed.
        """
        ...

    @abstractmethod
    def diff(self, var) -> Expr:
        """
        Computes the symbolic derivative of this expression with respect to
        ``var``.

        Parameters
        ----------
        var : Var
            Variable to differentiate with respect to.

        Returns
        -------
        Expr
            Symbolic derivative.
        """
        ...

    @abstractmethod
    def eval(self, var_dict) -> float:
        """
        Evaluates the expression numerically.

        Parameters
        ----------
        var_dict : dict[Var, float]
            Mapping from variables to numerical values.

        Returns
        -------
        float
            Numerical value of the expression.
        """
        ...

    @abstractmethod
    def simplify(self) -> Expr:
        """
        Returns a simplified version of the expression.

        Simplification may include constant folding, removing neutral
        elements, or other algebraic reductions.

        Returns
        -------
        Expr
            Simplified expression.
        """
        ...

    @abstractmethod
    def __str__(self):
        """
        Returns a human-readable mathematical representation of the
        expression.
        """
        ...

    def get_var_dependencies(self) -> set[Expr]:
        """
        Computes every variable appearing in the expression.

        Returns
        -------
        set[Var]
            Set containing all variables the expression depends on.
        """
        if len(self.sub_nodes) == 0:
            return set()

        dependencies = self.sub_nodes[0].get_var_dependencies()

        for i in range(1, len(self.sub_nodes)):
            dependencies.update(self.sub_nodes[i].get_var_dependencies())

        return dependencies

    def __init__(self, *args: Expr):
        """
        Constructs an expression node.

        Parameters
        ----------
        *args : Expr
            Child expressions.
        """
        self.sub_nodes = list(args)


class Unary(Expr):
    """
    Base class for unary operators.

    Unary expressions always contain exactly one child.
    """

    precedence = 4

    def __init__(self, argument: Expr):
        super().__init__(argument)


class Binary(Expr):
    """
    Base class for binary operators.

    Binary expressions always contain exactly two children.
    """

    def __init__(self, *args: Expr):
        super().__init__(*args)
        assert len(self.sub_nodes) == 2


class Ternary(Expr):
    """
    Base class for ternary operators.

    Ternary expressions always contain exactly three children.
    """

    def __init__(self, *args: Expr):
        super().__init__(*args)
        assert len(self.sub_nodes) == 3