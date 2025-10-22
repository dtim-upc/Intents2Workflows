from typing import Union
from rdflib import Literal, URIRef
from .parameter import LiteralValue, Parameter
from common import *


class AlgebraicExpression:
    def __init__(self, operation: URIRef, term1: Union[Parameter, 'AlgebraicExpression', LiteralValue], 
                 term2:  Union[Parameter, 'AlgebraicExpression', LiteralValue] = None, namespace: Namespace = cb):
        self.operation = operation
        self.term1 = term1
        self.term2 = term2
        urlname = f"algebraic-expression-{hash(self.term1)}-{hash(self.term2)}-{self.operation.fragment}"
        self.uri_ref = namespace[urlname]

    def add_to_graph(self, g: Graph):

        def term_to_uri(term):

            if term is None:
                return cb.NONE
            elif isinstance(term, AlgebraicExpression):
                return term.add_to_graph(g)
            elif isinstance(term, Parameter):
                return term.uri_ref
            elif isinstance(term, LiteralValue):
                return Literal(term)
            else:
                print(term)
                raise Exception("invalid term type")

        expr = self.uri_ref
        g.add((expr,RDF.type,tb.AlgebraicExpression))
        g.add((expr, tb.hasOperation, self.operation))
        
        term1_uri = term_to_uri(self.term1)
        g.add((expr,tb.hasTerm1, term1_uri))
        
        if not self.term2 is None:
            term2_uri = term_to_uri(self.term2)
            g.add((expr,tb.hasTerm2, term2_uri))
        
        return expr