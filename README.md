# Intents2Workflows

### Prerequisites <a name="prerequisites"></a>

Before you begin, ensure that you have the following prerequisites installed:

- [Node.js](https://nodejs.org/) (version >=12.22.1)
- [NPM](https://docs.npmjs.com/cli/v8/commands/npm-install) (version >=6.14.12)
- [Yarn](https://classic.yarnpkg.com/lang/en/docs/install/#windows-stable) You can install it using `npm install -g yarn` (or on a macOS install it using Homebrew using `brew install yarn`)
- [Quasar](https://quasar.dev/) (CLI >= 2.0) You can install it using `npm install -g @quasar/cli`

Then, clone the repository:

   ```bash
   git clone https://github.com/dtim-upc/Intents2Workflows.git
   cd Intents2Workflows
   ```
   
### Configuration <a name="configuration"></a>

Lets ensemble everything to be able to compile and make run the code.

#### Backend <a name="backend-configuration"></a>

1. Go to `Intents2Workflows/api`. First install all the required libraries with the following command:

   ```bash
   pip install -r requirements.txt    
   ```
   Then, launch the API with the following line
   ```bash
   uvicorn main:app --port=8080     
   ```

##### GraphDB
To use the intent anticipation/generation module it is necessary to populate a GraphDB instance with an initial set of triples. To do so, go to the deployed GraphDB URL (by default, [localhost:7200](http://localhost:7200/)), select _import_ on the top left and then _upload RDF files_. Upload the following file: `backend/Modules/IntentAnticipation/read-write-graphdb/graphdb-import/KnowledgeBase.nt`

##### Intents modules <a name="intents-configuration"></a>
The intent-generation functionalities are separated into two different modules, which can be found in the backend folder. 
1. Go to `Intents2Workflows/modules/IntentSpecification2WorkflowGenerator`. First install all the required libraries with the following command:
   
   ```bash
   pip install -r requirements.txt    
   ```
   Then, launch the API with the following line
   ```bash
   flask --app api\api_main.py run --port=8000
   ```
2. Go to `Intents2Workflows/modules/IntentAnticipation`. First install all the required libraries with the following command:
   
   ```bash
   pip install -r requirements.txt    
   ```
   Then, launch the APIs (there are two) with the following line
   ```bash
   python .\start_apis.py  
   ```

#### Frontend <a name="frontend-configuration"></a>

1. Open in the terminal the `Intents2Workflows/frontend` folder.

2. Execute `npm install`.

3. Then, execute `yarn install` (on macOS it is possible you need to run `yarn install --ignore-engines`).

4. Finally, execute `quasar dev` (or on a macOS do it from the `node_modules` directory using `node_modules/@quasar/app-vite/bin/quasar dev`. This will open your browser with the URL http://localhost:9000/#/projects.

_Note: that you must have Quasar CLI as it's mentioned in the Prerequisites section. If there's an error like `Global Quasar CLI • ⚠️   Error  Unknown command "dev"`, it's because you are not in the correct path, or you don't have Quasar CLI installed._ 
