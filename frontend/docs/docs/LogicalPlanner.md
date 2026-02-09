import { Icon, UI, Button } from '@site/src/components/UI'
import { StepList } from '@site/src/components/StepList'
import Zoom from 'react-medium-image-zoom'
import 'react-medium-image-zoom/dist/styles.css'
import Admonition from '@theme/Admonition'

import LPSeeImg from '@site/static/img/LP-see.png'
import LPSelectImg from '@site/static/img/LP-select.png'
import LPRunImg from '@site/static/img/LP-run.png'
import LPDiagramImg from '@site/static/img/LP-diagram.png'
import LPImg from '@site/static/img/LP.png'


# Logical planner
The logical planner aims to create complex analytical workflows from a given set of abstract plans and intent information.

In this window the user can decide on which abstract plans materialize to logical plans. To help the user decide, a set estimated metrics are provided on each abstract plan. These metrics are obtained using [Option Explorer API](http://194.249.3.27:8000/#introduction) and are based on the intent information. Additionally, it is also possible to individually [visualize the abstract plans](#visualize-abstract-plan).



:::info
If one of the abstract plans generation is restricted using one of the algorithm recommendation only one option will appear. Thus, no Option Explorer information will be present
:::

<Zoom>
<img
    src={LPImg}
    alt="Logical planner"
    style={{ width: 1921, borderRadius: 8, marginTop: 8 }}
    className="zoomable"
/>
</Zoom>

## Visualize abstract plan

<StepList
  steps={[
    { content: (
        <>
        Click <Button icon="eye-outline" iconSize="24px"  extra_class="eye-button"></Button> on the desired abstract plan.
        <Zoom>
        <img
            src={LPSeeImg}
            alt="Visualize Abstract plan"
            style={{ width: 921, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    },
    { content: (
        <>
        An interactive diagram should be displayed with the abstract plan components and relations.
        <Zoom>
        <img
            src={LPDiagramImg}
            alt="Abstract plan diagram"
            style={{ width: 1921, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
    )

    }
  ]}
/>


## Run logical planner

<StepList
  steps={[
    { content: (
        <>
        Select the abstract plans that will be used to generate more complex workflows (logical plans).
        This selection can be done by individually checking  <input type="checkbox" checked readOnly className="checkbox-large"/> abstract plans. 
        <br/>
        <br/>
        Alternatively, is it possible to select all plans at once using <Button extra_class="select-button">SELECT ALL</Button> and deselect all plans using <Button extra_class="select-button">SELECT NONE</Button>.
        <Zoom>
        <img
            src={LPSelectImg}
            alt="Select Abstract plan"
            style={{ width: 921, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    },
    { content: (
        <>
        Click <Button>RUN LOGICAL PLANNER</Button>.
        <Zoom>
        <img
            src={LPRunImg}
            alt="Run logical planner"
            style={{ width: 1921, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
    )
    },
    { content: (
        <>
        The generated plans will be displayed in <a href="/WorkflowPlanner">workflow planner</a> window.
        </>
        )
    },
  ]}
/>
