# Add a new implementation engine to the ontology

## Information needed


* Parameters and format specific to the implementation engine

## Steps

1. Define the new engine in the [CBOX](../ontology_populator/cbox_generator.py#L41-L48)
2. Create a new folder named as the new engine on [`ontology_populator/implementations`](../ontology_populator/implementations/)
3. In this new folder, create `<engine name>_implementation.py`.
4. Create new classes tha inherit from [EngineImplementation](../ontology_populator/implementations/core/engine_implementation.py) and [EngineParameter](../ontology_populator/implementations/core/engine_parameter.py) that fullfil the needs of the new engine. Use [`knime_implementation.py`](../ontology_populator/implementations/knime/knime_implementation.py) and ['knime_parameter.py'](../ontology_populator/implementations/knime/knime_parameter.py) as a reference.
5. In `ontology_populator/implementations/<engine name>/`, create the script `__init__.py` and leave it empty.
6. [Add new algorithms](createNewAlgorithm.md) specific to the engine.
7. Import the new implementations to [cbox_generator.py](../ontology_populator/cbox_generator.py#L9-L13)
8. Execute the following command to regenerate the cbox:
    ```bash
    python cbox_generator.py  
    ```
9. Create a new folder named as the new engine on [`pipeline_translator`](../pipeline_translator/)
10. In this new folder, create `<engine name>_pipeline_translator.py`.
11. Generate the script and all the resources to translate workflow graphs to the new engine supported format.