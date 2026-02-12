import { Icon, UI, Button } from '@site/src/components/UI'
import { StepList } from '@site/src/components/StepList'
import Zoom from 'react-medium-image-zoom'
import 'react-medium-image-zoom/dist/styles.css'
import Admonition from '@theme/Admonition'

import ApRunImg from '@site/static/img/AP-run.png'
import ApRestrictGif from '@site/static/img/AP-restrict-chill-small.gif'
import ApImg from '@site/static/img/AP.png'

# Abstract Planner
The aim of the abstract planner phase is to obtain a high-level representation of the workflows that will be produced in the next steps with the information present in the user intent.

In this page the users see a summary of the intent information and can choose to [restrict the generation of abstract plans by algorithm](#algorithm-restriction) or either generate all possibilities.

<Zoom>
<img
    src={ApImg}
    alt="Abstract Planner"
    style={{ width: 1900, borderRadius: 8, marginTop: 8 }}
    className="zoomable"
/>
</Zoom>


## Algorithm restriction


<StepList
  steps={[
    { content: (
        <>
        Choose one algorithm from the slide bar.
        <Zoom>
        <img
            src={ApRestrictGif}
            alt="Restrict algorithm"
            style={{ width: 500, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>

        <Admonition type="tip" title="tip">Restrict algorithm slide gives the user recommendations of what algorithm to choose base on past experiences on similar problems and user profiles. Each recommendation contains a short justification.</Admonition>
        </>
        )
    },
    { content: (
        <>
        <a href="#run-abstract-planner">Run abstract planner</a>.
        </>
    )

    }
  ]}
/>



## Run abstract planner
<StepList
  steps={[
    { content: (
        <>
        Click <Button>RUN ABSTRACT PLANNER</Button>.
        <Zoom>
        <img
            src={ApRunImg}
            alt="RUN ABSTRACT PLANNER"
            style={{ width: 1500, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    },
    { content: (
        <>
        The generated results can be seen on the <a href="/LogicalPlanner">logical planner</a> window.
        </>
        )
    },
  ]}
/>




