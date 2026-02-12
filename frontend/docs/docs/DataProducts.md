import { Icon, UI, Button } from '@site/src/components/UI'
import { StepList } from '@site/src/components/StepList'
import Zoom from 'react-medium-image-zoom'
import 'react-medium-image-zoom/dist/styles.css'
import Admonition from '@theme/Admonition'

import FileImg from '@site/static/img/Upload-file.png'
import FolderImg from '@site/static/img/Upload-folder.png'
import DDMImg from '@site/static/img/Upload-ddm.png'
import DDMSelectImg from '@site/static/img/ddm-select.png'
import DDMUploadImg from '@site/static/img/ddm-upload.png'
import DDMSelectTensorImg from '@site/static/img/ddm-select-tensor.png'
import DDMSelectTensorCheckImg from '@site/static/img/ddm-select-tensor-check.png'
import DDMSelectTensorImportImg from '@site/static/img/ddm-select-tensor-import.png'
import DataProductImg from '@site/static/img/DataProduct.png'
import DataProductFolderImg from '@site/static/img/DataProduct-Folder.png'
import DataProductDDMImg from '@site/static/img/DataProduct-ddm.png'
import DataProductTensorImg from '@site/static/img/DataProduct-Tensor.png'
import DataProductTensorDDMImg from '@site/static/img/DataProduct-Tensor-ddm.png'
import DataProductDeleteImg from '@site/static/img/DataProduct-Delete.png'
import ConfirmImg from '@site/static/img/Confirm.png' 
import DataProductDownloadImg from '@site/static/img/DataProduct-download.png'
import DPImg from '@site/static/img/DP.png'



# Data products
A data product is an internal structure that contains a dataset file(s) and the metadata related to it. It is a crucial part in the [intent definition](/IntentDefinition). It is possible to create new data products or delete already existent ones.

Two main types of data are supported in the generation of data products:
- [**Tabular data**](#create-data-product-with-tabular-data): Tabular data is data that is organized in a table format, consisting of rows and columns, where rows represent individual records or observations, columns represent attributes, variables, or fields. Thus, each cell contains a single value describing a specific attribute of a record. 
- [**Tensor data**](#create-data-product-with-tensor-data): Tensor data is data that is organized as a multi-dimensional array, extending beyond rows and columns to represent data across two or more dimensions (axes). 

After the dataset is imported, Intent2Workflows extracts information from the dataset (metadata, general metrics, column metrics, etc.). This extracted information can be [retrieved](#retrieve-dataset-annotations).

<Zoom>
<img
    src={DPImg}
    alt="Data Product"
    style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
    className="zoomable"
/>
</Zoom>

## Create data product with tabular data
This is the standard way of generating new data products, by importing tabular data files. To do so, the user must provide one or multiple dataset files([File import](#file-import)) or a folder([Folder import](#folder-import)) locally. Another option is to directly provide the data from [DDM](#ddm-import)

:::tip
The supported file formats are **CSV**(`.csv`), **Parquet**(`.parquet`) and **Laspy**(`.las`). Data files in the mentioned formats can also be provided compressed in a  **ZIP**(`.zip`) file.
:::


### File import

<StepList
  steps={[
    { content: (
        <>
        Select <UI icon="selection-search" size="24">Data Products</UI> in the left slide bar.
        </>
        )
    },
    { content: (
        <>
        <div>Click <Button>Upload file</Button>.</div>
        <Zoom>
        <img
            src={FileImg}
            alt="Upload file"
            style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    },
    { content: (
        <>
        Select the desired files.

        <Admonition type="note" title="Note">
        When importing multiple files using file import, I2WG will consider the data product as the union of all data files encoded in a supported format.
        </Admonition>

        <Admonition type="warning" title="Warning">
        Make sure all the imported files have the correct file extension. Otherwise, I2WG will ignore them.
        </Admonition>
        </>
        )
    },
    { content: (
        <>
        If all goes well, a new data product should be created.

        <Zoom>
        <img
            src={DataProductImg}
            alt="Download illustration"
            style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>

        <Admonition type="warning" title="Warning">
        Data product will not be created if one already exists with the same name.
        </Admonition>
        </>
        )
    },
  ]}
/>


### Folder import

<StepList
  steps={[
    { content: (
        <>
        Select <UI icon="selection-search" size="24">Data Products</UI> in the left slide bar.
        </>
        )
    },
    { content: (
        <>
        <div>Click <Button>Upload folder</Button>.</div>
        <Zoom>
        <img
            src={FolderImg}
            alt="Upload folder"
            style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    },
    { content: (
        <>
        Select the desired files

        <Admonition type="note" title="Note">
        I2WG will consider the data product as the union of all data files encoded in a supported format present in the uploaded folder.
        </Admonition>

        <Admonition type="warning" title="Warning">
        Make sure all the imported files have the correct file extension. Otherwise, I2WG will ignore them.
        </Admonition>
        </>
        )
    },
    { content: (
        <>
        If all goes well, a new data product should be created.

        <Zoom>
        <img
            src={DataProductFolderImg}
            alt="Download illustration"
            style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>

        <Admonition type="warning" title="Warning">
        Data product will not be created if one already exists with the same name.
        </Admonition>
        </>
        )
    },
  ]}
/>

### DDM import

<StepList
  steps={[
    { content: (
        <>
        Select <UI icon="selection-search" size="24">Data Products</UI> in the left slide bar.
        </>
        )
    },
    { content: (
        <>
        <div>Click <Button icon="cloud_download" size="24" type = "material-icons">Import from DDM</Button>.</div>
        <Zoom>
        <img
            src={DDMImg}
            alt="Upload from DDM"
            style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    },
    { content: (
        <>
        <div>Select either a file or a folder.</div>
        <Zoom>
        <img
            src={DDMSelectImg}
            alt="Select from DDM"
            style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>

        <Admonition type="tip" title="Tip">
        On the bottom left, the current selected item is shown.
        </Admonition>

        <Admonition type="warning" title="Warning">
        Make sure all the imported files have the correct file extension. 
        </Admonition>
        </>
        )
    },
    { content: (
        <>
        <div>Click <Button icon="cloud_download" size="24" type = "material-icons">IMPORT</Button>.</div>
        <Zoom>
        <img
            src={DDMUploadImg}
            alt="Upload from DDM"
            style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    },
    { content: (
        <>
        If all goes well, a new data product should be created.

        <Zoom>
        <img
            src={DataProductDDMImg}
            alt="DDM data product"
            style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>

        <Admonition type="warning" title="Warning">
        Data product will not be created if one already exists with the same name.
        </Admonition>
        </>
        )
    },
  ]}
/>


## Create data product with tensor data
Intent2Workflows offers a limited support for tensor data products. To import non-tabular data, the user must provide a **NumPyZip** file ([File import](#local-import)). Alternatively, it is possible to directly provide the data from [DDM](#ddm-import-1).

### Local import
<StepList
  steps={[
    { content: (
        <>
        Select <UI icon="selection-search" size="24">Data Products</UI> in the left slide bar.
        </>
        )
    },
    { content: (
        <>
        <div>Click <Button>Upload file</Button>.</div>
        <Zoom>
        <img
            src={FileImg}
            alt="Upload file"
            style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    },
    { content: (
        <>
        Select a <b>NumpyZip</b> file.

        <Admonition type="warning" title="Warning">
        <b>ONLY</b> NumPyZip files are supported.
        </Admonition>
        </>
        )
    },
    { content: (
        <>
        If all goes well, a new data product should be created.

        <Zoom>
        <img
            src={DataProductTensorImg}
            alt="Tensor data product"
            style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>

        <Admonition type="warning" title="Warning">
        Data product will not be created if one already exists with the same name.
        </Admonition>
        </>
        )
    },
  ]}
/>

### DDM import 

<StepList
  steps={[
    { content: (
        <>
        Select <UI icon="selection-search" size="24">Data Products</UI> in the left slide bar.
        </>
        )
    },
    { content: (
        <>
        <div>Click <Button icon="cloud_download" size="24" type = "material-icons">Import from DDM</Button>.</div>
        <Zoom>
        <img
            src={DDMImg}
            alt="Upload from DDM"
            style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    },
    { content: (
        <>
        <div>Select a folder.</div>
        <Zoom>
        <img
            src={DDMSelectTensorImg}
            alt="Select from DDM"
            style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>

        <Admonition type="tip" title="Tip">
        On the bottom left, the current selected item is shown.
        </Admonition>
        </>
        )
    },
    { content: (
        <>
        <div>Check <input type="checkbox" checked readOnly/><b>Tensor import</b>.</div>
        <Zoom>
        <img
            src={DDMSelectTensorCheckImg}
            alt="DDM Tensor check"
            style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        <Admonition type="tip" title="tip">
        Tensor import is expecting a folder with subfolders inside, where each subfolder contains tabular files. Hence, the subfolder structure is considered the 3rd dimension.
        </Admonition>
        </>
        )
    },
    { content: (
        <>
        <div>Click <Button icon="cloud_download" size="24" type = "material-icons">IMPORT</Button>.</div>
        <Zoom>
        <img
            src={DDMSelectTensorImportImg}
            alt="DDM Tensor import"
            style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    },
    { content: (
        <>
        If all goes well, a new data product should be created.

        <Zoom>
        <img
            src={DataProductTensorDDMImg}
            alt="DDM tensor data product"
            style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>

        <Admonition type="warning" title="Warning">
        Data product will not be created if one already exists with the same name.
        </Admonition>
        </>
        )
    },
  ]}
/>

## Delete data product
<StepList
  steps={[
    { content: (
        <>
        Select <UI icon="selection-search" size="24">Data Products</UI> in the left slide bar.
        </>
        )
    },
    { content: (
        <>
        <div>Choose one of the existent data products.</div>
        </>
        )
    },
    { content: (
        <>
        <div>Click <Icon name="delete" type="q-icon" color="#f44336" size="24px"  extra_class="q-btn-like"></Icon> on the chosen data product. </div> 
        <Zoom>
        <img
            src={DataProductDeleteImg}
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
        <div> Confirm the action in the confirmation popup. </div> 
        <Zoom>
        <img
            src={ConfirmImg}
            alt="Delete file confirm"
            style={{ width: 402, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    },
    { content: (
        <>
        <div> Now, the data product has been deleted and no longer will be present in the data product list. </div> 
        </>
        )
    },
    ]}
/>

## Retrieve Dataset annotations
<StepList
  steps={[
    { content: (
        <>
        Select <UI icon="selection-search" size="24">Data Products</UI> in the left slide bar.
        </>
        )
    },
    { content: (
        <>
        <div>Choose one of the existent data products.</div>
        </>
        )
    },
    { content: (
        <>
        <div>Click <Icon name="download" type="mdi" color="#4945FF" size="24px" extra_class="q-btn-like"></Icon> on the chosen data product. </div> 
        <Zoom>
        <img
            src={DataProductDownloadImg}
            alt="Download annotations"
            style={{ width: 1919, borderRadius: 8, marginTop: 8 }}
            className="zoomable"
        />
        </Zoom>
        </>
        )
    },
    { content: (
        <>
        <div> Open or save the annotations file generated. </div> 
        </>
        )
    },
    ]}
/>