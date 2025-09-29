from typing import List, Union, Optional

from common import *
from ontology_populator.implementations.core.engine_implementation import EngineImplementation
from ontology_populator.implementations.core.implementation import Implementation

from .knime_parameter import KnimeParameter


class KnimeImplementation(EngineImplementation):

    def __init__(self, name: str, base_implementation: Implementation, parameters: List[KnimeParameter],
                 knime_node_factory: str, knime_bundle: 'KnimeBundle', knime_feature: 'KnimeFeature', namespace = cb) -> None:
        
        super().__init__(name, "KNIME", base_implementation, parameters, namespace)
        self.knime_node_factory = knime_node_factory
        self.knime_bundle = knime_bundle
        self.knime_feature = knime_feature

    def add_to_graph(self, g: Graph):
        g.add((self.uri_ref, tb.term('knime-node-name'), Literal(self.name)))

        # Node Factory
        g.add((self.uri_ref, tb.term('knime-factory'), Literal(self.knime_node_factory)))

        # Bundle
        g.add((self.uri_ref, tb.term('knime-node-bundle-name'), Literal(self.knime_bundle.name)))
        g.add((self.uri_ref, tb.term('knime-node-bundle-symbolic-name'), Literal(self.knime_bundle.symbolic_name)))
        g.add((self.uri_ref, tb.term('knime-node-bundle-vendor'), Literal(self.knime_bundle.vendor)))
        g.add((self.uri_ref, tb.term('knime-node-bundle-version'), Literal(self.knime_bundle.version)))

        # Feature
        g.add((self.uri_ref, tb.term('knime-node-feature-name'), Literal(self.knime_feature.name)))
        g.add((self.uri_ref, tb.term('knime-node-feature-symbolic-name'), Literal(self.knime_feature.symbolic_name)))
        g.add((self.uri_ref, tb.term('knime-node-feature-vendor'), Literal(self.knime_feature.vendor)))
        g.add((self.uri_ref, tb.term('knime-node-feature-version'), Literal(self.knime_feature.version)))

        # Parameters
        for parameter in self.parameters:
            if isinstance(parameter, KnimeParameter):
                path_value = Literal(parameter.path) if parameter.path is not None else cb.NONE
                g.add((parameter.uri_ref, tb.knime_path, path_value))

        return super().add_to_graph(g)


class KnimeBundle:

    def __init__(self, name: str, symbolic_name: str, vendor: str, version: str) -> None:
        super().__init__()
        self.name = name
        self.symbolic_name = symbolic_name
        self.vendor = vendor
        self.version = version

KnimeBaseBundle = KnimeBundle('KNIME Base Nodes', 'org.knime.base', 'KNIME AG, Zurich, Switzerland',
                              "4.7.0.v202301251625")
KnimeDynamicBundle = KnimeBundle('D3 Samples for KNIME Dynamic JavaScript Node Generation',
                               'org.knime.dynamic.js.base', 'KNIME AG, Zurich, Switzerland',
                               '4.7.0.v202211082357')
KnimeJSBundle = KnimeBundle('KNIME JavaScript Base Views', 'org.knime.js.views', 'KNIME AG, Zurich, Switzerland',
                            '4.7.0.v202211091556') 

KnimeXGBoostBundle = KnimeBundle('XGBoost Linear Model Learner', 'org.knime.xgboost', 'KNIME AG, Zurich, Switzerland',
                                 '5.4.0.v202411131247')

class KnimeFeature:
    def __init__(self, name: str, symbolic_name: str, vendor: str, version: str) -> None:
        super().__init__()
        self.name = name
        self.symbolic_name = symbolic_name
        self.vendor = vendor
        self.version = version

KnimeDefaultFeature = KnimeFeature('', '', '', '0.0.0')
KnimeJSViewsFeature = KnimeFeature('KNIME JavaScript Views', 'org.knime.features.js.views.feature.group',
                                   'KNIME AG, Zurich, Switzerland', '4.7.0.v202211091556')
KnimeXGBoostFeature = KnimeFeature("KNIME XGBoost Integration", "org.knime.features.xgboost.feature.group",
                                   "KNIME AG, Zurich, Switzerland", "5.4.0.v202411131247")