import { Icon, UI, Button } from '@site/src/components/UI'
import { StepList } from '@site/src/components/StepList'
import Zoom from 'react-medium-image-zoom'
import 'react-medium-image-zoom/dist/styles.css'
import Admonition from '@theme/Admonition'

import IntentAddImg from '@site/static/img/Intent-add.png'
import IntentNameGif from '@site/static/img/Intent-name2.gif' 
import IntentDpGif from '@site/static/img/Intent-dp2.gif'
import IntentProblemGif from '@site/static/img/Intent-problem.gif'
import IntentInferGif from '@site/static/img/Intent-infer-fast.gif'

import IntentTargetImg from '@site/static/img/Intent-target.png'
import IntentOkImg from '@site/static/img/Intent-ok.png'
import IntentImg from '@site/static/img/Intent.png'

# Intents
A user intent is a structure that encapsulates the user's analytical intentions. More precisely, it contains a dataset, defines a procedure that should be applied to the data (i.e., classification, clustering, visualization, etc.) and specifies a set of constraints that should be followed. Intent information is crucial to generate suitable analytical workflows.

<Zoom>
<img
    src={IntentImg}
    alt="Intent definition"
    style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
    className="zoomable"
/>
</Zoom>

## Create Intent
<StepList
  steps={[
    { content: (
        <>
        Select <UI icon="thought-bubble" size="24">Intents</UI> in the left slide bar.
        </>
        )
    },
    { content: (
        <>
        <div>Click <Button icon="add" type="q-icon" extra_class="add-button" iconSize="24px"></Button>.</div>
        <Zoom>
        <img
            src={IntentAddImg}
            alt="Delete file"
            style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    },
    { content: (
        <>
        <div> Write a unique name for the intent. </div> 
        <Zoom>
        <img
            src={IntentNameGif}
            alt="Add intent name"
            style={{ width: 800, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        <Admonition type="warning" title="Warning">
        Intent name must not contain spaces.
        </Admonition>
        </>
        )
    },
    { content: (
        <>
        <div> Choose a data product. If the one you want does not appear, you can <a href="/DataProducts">create it</a>.</div> 
        <Zoom>
        <img
            src={IntentDpGif}
            alt="Add intent data product"
            style={{ width: 800, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    },
    { content: (
        <>
        <div> Choose a problem to solve. You have two options:</div>
        <details>
        <summary>Choose one from the slide</summary>
        <Zoom>
        <img
            src={IntentProblemGif}
            alt="Select problem"
            style={{ width: 800, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </details>
        <details>
        <summary>Infer it by providing a textual description on the analytical goals</summary>
        <Zoom>
        <img
            src={IntentInferGif}
            alt="Infer problem"
            style={{ width: 800, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </details>
        </>
        )
    },
    { content: (
        <>
        <div>If the chosen problem is classification, select the target variable.</div> 
        <Zoom>
        <img
            src={IntentTargetImg}
            alt="Select target"
            style={{ width: 1500, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    },
    { content: (
        <>
        <div>Click <Button>SUGGEST PARAMETERS</Button> to create the intent.</div> 
        <Zoom>
        <img
            src={IntentOkImg}
            alt="Suggest parameters"
            style={{ width: 1900, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    },
    ]}
/>

When the intent is properly created, you will be automatically redirected to the [Abstract planner](AbstractPlanner) window.




