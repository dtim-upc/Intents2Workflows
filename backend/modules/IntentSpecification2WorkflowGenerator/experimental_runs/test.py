from openml import tasks, OpenMLDataset, study, OpenMLClassificationTask, evaluations, OpenMLEvaluation
import pandas as pd



s = study.get_suite(271)
for task_id in s.tasks:
    task:OpenMLClassificationTask = tasks.get_task(task_id)
    #data = task.get_dataset()
    #X, y, categorical_indicator, attribute_names= data.get_data()

    #print(X, y, categorical_indicator, attribute_names)
    evals = evaluations.list_evaluations(
    function="area_under_roc_curve",
    tasks=[task_id])

    result = pd.DataFrame([
    {"run_id": v.run_id, "value": v.value}
    for v in evals.values()
    ])
    print("RUNS",len(evals))

    if len(evals) > 0:
        print(result.sort_values("value", ascending=False).head())

