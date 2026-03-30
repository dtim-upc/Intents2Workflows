import inspect
import numpy
from sklearn.utils import all_estimators, get_tags
from sklearn.utils._param_validation import Interval, Options, Hidden, MissingValues, HasMethods, _InstancesOf,_NanConstraint, _NoneConstraint, _PandasNAConstraint
from sklearn.utils._tags import Tags,TargetTags, ClassifierTags, RegressorTags, TransformerTags, InputTags
import json


def get_classification_tags(classifier_tags:ClassifierTags):
    if not classifier_tags is None:
        tags =  {
                "multi_class": classifier_tags.multi_class,
                "multi_label": classifier_tags.multi_label,
                "poor_score": classifier_tags.poor_score
                }
        return tags
    return None

def get_regression_tags(regressor_tags:RegressorTags):
    if not regressor_tags is None:
        tags =  {
                "poor_score": regressor_tags.poor_score,
                }
        return tags
    return None

def get_transformation_tags(transformation_tags:TransformerTags):
    if not transformation_tags is None:
        tags = {
            "preserves_dtype": transformation_tags.preserves_dtype,
        }
        return tags
    return None

def get_input_tags(input_tags:InputTags):
    if not input_tags is None:
        tags = {
            "one_d_array":input_tags.one_d_array,
            "two_d_array":input_tags.two_d_array,
            "three_d_array":input_tags.three_d_array,
            "sparse": input_tags.sparse,
            "categorical": input_tags.categorical,
            "positive_only": input_tags.positive_only,
            "allow_nan": input_tags.allow_nan,
        }
        return tags
    return None

def get_class_string(object):
    if not object is None:
        return str(object)
    
    return None


def get_constraints(EstimatorClass):
    constr = {}
    try:
        constr = EstimatorClass._parameter_constraints
    except Exception as e:
        print("error",f"Could not inspect: {e}")
    finally:
        return constr

def get_estimator_tags(EstimatorClass,params):
    tags = None
    #print(params)
    kwargs = {k:v['value'] for k,v in params.items()}

    try:
        tags = get_tags(EstimatorClass(**kwargs))
    except Exception as e:
        print("error",f"Unable to load tags: {e}")
        print(kwargs)
    
    return tags

def extract_constraint(constraint):
    options_cleaned = []

    for option in constraint:
        if isinstance(option,Hidden):
            op = None
        
        elif isinstance(option, Options):

            levels = []

            for o in option.options:
                levels.append(extract_constraint([o])[0])
            

            op = {
                "type": "Factor",
                "dtype": option.type.__name__,
                "levels": levels
            }

        elif isinstance(option, Interval):
            op = {
                "type": "Numeric",
                "dtype": option.type.__name__,
            }

        elif isinstance(option, str):
            if option == "verbose":
                op = {
                    "type":"Text",
                    "dtype":"str"
                }
            
            elif option == "boolean":
                op = {
                    "type": "Numeric",
                    "dtype": "bool",
                }
            
            elif option == "nan":
                op = {
                    "type": "Null",
                    "dtype": "numpy.nan"
                }
            
            else:
                op = {
                    "type":"Complex",
                    "dtype":str(option)
                }

        elif isinstance(option,HasMethods):
            op = {
                "type":"Methods",
                "dtype":"str",
                "methods":[m for m in option.methods]
            }

        elif isinstance(option, _NanConstraint) or isinstance(option, _NoneConstraint) or isinstance(option, _PandasNAConstraint):
             op = {
                "type":"Null",
                "dtype":str(option)
            }

        
        elif option is None:
            op = {
                "type": "Null",
                "dtype": "None"
            }

        elif isinstance(option,_InstancesOf):
            op = {
                "type":"Datatype",
                "dtype":option.type.__name__
            }
        
        elif isinstance(option,type):
            op = {
                "type": "Datatype",
                "dtype": option.__name__
            }

        elif callable(option):
            op = {
                "type":"Custom_code",
                "dtype":option.__name__
            }

        else:
            print("unkknown variable",option,type(option))
            op = {
                "type":"unknown",
                "dtype":str(option).replace("'","")
            }
        

        if isinstance(option, MissingValues):
            options_cleaned.extend(extract_constraint(option._constraints))
        elif not op is None:
            options_cleaned.append(op)
    
    return options_cleaned
    

def get_all_estimators(estimator_type='transformer'):
    all_params = {}

    for name, EstimatorClass in all_estimators(estimator_type):

        print(f"#############################\t{name}\t################################")
        default_nonexistant = False
        try:
            # Use inspect to get constructor signature
            sig = inspect.signature(EstimatorClass.__init__)
            constraints = get_constraints(EstimatorClass)
            params = {}
            module = (EstimatorClass.__module__).split('.')
            if len(module) > 1:
                    module = module[1]

            #print("Estimator: ", name)
            for k, v in sig.parameters.items():
                if k != "self" and k != "args" and k != "kwargs":
                    #print("\tParameter: ", k, v)
                    
                    value = None
                    if v.default is not inspect.Parameter.empty:
                        if type(v.default).__module__ != "builtins" or callable(v.default):
                            value=str(v.default)
                        elif isinstance(v.default, float) and (v.default==float('inf') or v.default == float('-inf')):
                            value = str(v.default)
                        elif isinstance(v.default, float) and numpy.isnan(v.default):
                            value = str(v.default)
                        else:
                            value = v.default
                    else:
                        default_nonexistant = True
                            
                    #print(value, type(value))

                    params[k] = {'value': value,
                                'specification': extract_constraint(constraints.get(k,[]))}
                    

        except Exception as e:
            print("error",f"Could not inspect: {e}")
            raise Exception()

        tags = get_estimator_tags(EstimatorClass, params)
        doc = ""
        if tags.estimator_type in ["transformer", None]:
            if hasattr(EstimatorClass, "transform"):
                doc = EstimatorClass.transform.__doc__
            elif hasattr(EstimatorClass, "fit_transform"):
                doc = EstimatorClass.fit_transform.__doc__
        
        else:
            if hasattr(EstimatorClass, "predict"):
                doc = EstimatorClass.predict.__doc__
            elif hasattr(EstimatorClass, "fit_predict"):
                doc = EstimatorClass.fit_predict.__doc__
        #doc = doc[doc.find("Returns"):]

        target_tags = tags.target_tags
        classifier_tags = get_classification_tags(tags.classifier_tags)
        regressor_tags = get_regression_tags(tags.regressor_tags)
        transformer_tags = get_transformation_tags(tags.transformer_tags)
        input_tags = get_input_tags(tags.input_tags)


        info = {
                "name":name,
                "module":module,
                "needs_parameter_specification": default_nonexistant,
                "parameters":params,
                "estimator_type": estimator_type,
                "non_deterministic": tags.non_deterministic,
                "requires_fit": tags.requires_fit,
                "has_fit": hasattr(EstimatorClass, "fit"),
                "has_predict": hasattr(EstimatorClass, "predict"),
                "has_transform": hasattr(EstimatorClass, "transform"),
                "has_fitpredict": hasattr(EstimatorClass, "fit_predict"),
                "has_fittransform": hasattr(EstimatorClass, "fit_transform"),
                "target_tags": {
                    "required":target_tags.required,
                    "one_d_labels":target_tags.one_d_labels,
                    "two_d_labels":target_tags.two_d_labels,
                    "positive_only":target_tags.positive_only,
                    "single_output":target_tags.single_output,
                    "multi_output":target_tags.multi_output,
                },
                "classifier_tags": classifier_tags,
                "regressor_tags": regressor_tags,
                "transformer_tags": transformer_tags,
                "input_tags": input_tags,
                "return":doc
        }
        
        #print(params)
        #json.dumps(params)

        all_params[name] = info

    #print(all_params)
    return all_params


estimators_transf = get_all_estimators()
estimators_classification = get_all_estimators('classifier')
estimators_reg = get_all_estimators('regressor')
estimators_clus = get_all_estimators("cluster")

estimators = estimators_transf | estimators_classification | estimators_reg | estimators_clus


with open('./sklearn_miner.json',mode='w') as f:
    json.dump(estimators,f)


