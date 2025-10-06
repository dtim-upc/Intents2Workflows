from common import *
from .knime_implementation import KnimeImplementation, KnimeBaseBundle, KnimeDefaultFeature
from .knime_parameter import KnimeNumericParameter, KnimeFactorParameter, KnimeTextParameter, KnimeSpecificParameter
from ..core.expression import AlgebraicExpression
from ..simple.svm import svm_learner_implementation, svm_predictor_implementation

svm_learner_implementation = KnimeImplementation(
    name='SVM Learner',
    base_implementation=svm_learner_implementation,
    parameters=[
        KnimeTextParameter('classcol', 
                           base_parameter=next((param for param in svm_learner_implementation.parameters.keys() if param.label == 'SVM Class column'),None),
                           default_value="$$LABEL_CATEGORICAL$$"),
        KnimeNumericParameter('c_parameter', XSD.double, 
                              expression=AlgebraicExpression(cb.COPY, next((param for param in svm_learner_implementation.parameters.keys() if param.label == 'Overlapping Penalty'),0)),
                              default_value=1.0),
        KnimeNumericParameter('kernel_param_Bias', XSD.double, 
                              expression=AlgebraicExpression(cb.COPY, next((param for param in svm_learner_implementation.parameters.keys() if param.label == 'Bias'),0)),
                              default_value=1.0),
        KnimeNumericParameter('kernel_param_Power', XSD.double,  
                              expression=AlgebraicExpression(cb.COPY, next((param for param in svm_learner_implementation.parameters.keys() if param.label == 'Power'),0)),
                              default_value=1.0),
        KnimeNumericParameter('kernel_param_Gamma', XSD.double,
                              expression=AlgebraicExpression(cb.COPY, next((param for param in svm_learner_implementation.parameters.keys() if param.label == 'Gamma'),0)),
                              default_value=1.0),
        KnimeNumericParameter('kernel_param_kappa', XSD.double,
                              expression=AlgebraicExpression(cb.COPY, next((param for param in svm_learner_implementation.parameters.keys() if param.label == 'Gamma'),0)),
                              default_value=0.1),
        KnimeNumericParameter('kernel_param_delta', XSD.double,
                              expression=AlgebraicExpression(cb.COPY, next((param for param in svm_learner_implementation.parameters.keys() if param.label == 'Bias'),0)),
                              default_value=0.5),
        KnimeNumericParameter('kernel_param_sigma', XSD.double,
                              expression=AlgebraicExpression(cb.SQRT, 
                                                             AlgebraicExpression(cb.DIV, 
                                                                                 1,
                                                                                 AlgebraicExpression(cb.MUL, 
                                                                                                     2, 
                                                                                                     next((param for param in svm_learner_implementation.parameters.keys() if param.label == 'Gamma'),0)
                                                                                                    )
                                                                                )
                                                            ),
                              default_value=0.1),
        KnimeFactorParameter('kernel_type', levels={"Polynomial":"Polynomial", "HyperTangent":"Sigmoid", "RBF":"RBF"},
                             base_parameter=next((param for param in svm_learner_implementation.parameters.keys() if param.label == 'Kernel type'),None),
                             default_value=None),
    ],
    knime_node_factory='org.knime.base.node.mine.svm.learner.SVMLearnerNodeFactory2',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature
) 

svm_predictor_implementation = KnimeImplementation(
    name='SVM Predictor',
    base_implementation=svm_predictor_implementation,
    parameters=[
        KnimeSpecificParameter('prediction column name', XSD.string, "Prediction ($$LABEL$$)"),
        KnimeSpecificParameter('change prediction', XSD.boolean, False),
        KnimeSpecificParameter('add probabilities', XSD.boolean, False),
        KnimeSpecificParameter('class probability suffix', XSD.string, ""),
    ],
    knime_node_factory='org.knime.base.node.mine.svm.predictor2.SVMPredictorNodeFactory',
    knime_bundle=KnimeBaseBundle,
    knime_feature=KnimeDefaultFeature,
)

