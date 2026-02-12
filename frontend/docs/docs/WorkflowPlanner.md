import { Icon, UI, Button } from '@site/src/components/UI'
import { StepList } from '@site/src/components/StepList'
import Zoom from 'react-medium-image-zoom'
import 'react-medium-image-zoom/dist/styles.css'
import Admonition from '@theme/Admonition'

import WPSeeImg from '@site/static/img/WP-see.png'
import WPSelectImg from '@site/static/img/WP-select.png'
import WPRunImg from '@site/static/img/WP-run.png'
import WPDiagramImg from '@site/static/img/WP-diagram.png'
import WPImg from '@site/static/img/WP.png'

# Workflow planner
In the workflow planner phase, the main goal is to select the logical plans that will be materialized into analytical pipelines. To do so, it is possible to individually [visualize the logical plans](#visualize-logical-plan).

<Zoom>
<img
    src={WPImg}
    alt="Workflow planner"
    style={{ width: 1921, borderRadius: 8, marginTop: 8 }}
    className="zoomable"
/>
</Zoom>

## Visualize logical plan
<StepList
  steps={[
    { content: (
        <>
        Click <Button icon="eye-outline" iconSize="24px"  extra_class="eye-button"></Button> on the desired logical plan
        <Zoom>
        <img
            src={WPSeeImg}
            alt="Visualize Logical plan"
            style={{ width: 921, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    },
    { content: (
        <>
        An interactive diagram should be displayed with the logical plan components and relations.
        <Zoom>
        <img
            src={WPDiagramImg}
            alt="Logical plan diagram"
            style={{ width: 1921, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
    )

    }
  ]}
/>

## Run workflow planner
<StepList
  steps={[
    { content: (
        <>
        Select the logical plans that will be materialized (i.e. the pipelines that the user wants to export). 
        This selection can be done by individually checking <input type="checkbox" checked readOnly className="checkbox-large"/> logical plans.
        <br/>
        <br/>
        Alternatively, is it possible to select all plans at once using <Button extra_class="select-button">SELECT ALL</Button> and deselect all plans using <Button extra_class="select-button">SELECT NONE</Button>.
        
        <Zoom>
        <img
            src={WPSelectImg}
            alt="Select Logical plan"
            style={{ width: 921, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    },
    { content: (
        <>
        Click <Button>SELECT PLANS</Button>.
        <Zoom>
        <img
            src={WPRunImg}
            alt="Run workflow planner"
            style={{ width: 1921, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
    )
    },
    { content: (
        <>
        The generated workflows be displayed in <a href="/WorkflowExporter">workflow exporter</a> window.
        </>
        )
    },
  ]}
/>