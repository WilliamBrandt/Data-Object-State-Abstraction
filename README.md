# A Unified View on Data Object States - Implementation

This repository contains the prototypical implementation of the data object state concept introduced in our paper, "A Unified View on Data Object States". The work bridges the gap between process control flow and data management by formalizing and generalizing the definition of data object states in business process models.

## Getting Started:
### Prerequisites
Ensure you have the following installed:

- Python 3.8 or higher
- pip (Python package installer)

### Installation
1. Clone the Repository:

    ```sh
    git clone https://github.com/WilliamBrandt/Data-Object-State-Abstraction.git
    cd Data-Object-State-Abstraction
    ```

2. Install Dependencies:

    To install all necessary requirements run: 
    ```sh
    pip install -r ./requirements.txt
    ```

## Project Structure
-   ```data/```: This directory contains the specifications required for evaluating Data Object States. Specifically, it includes the DMN tables for the ```Order``` and ```Invoice``` classes, as well as an OCEL log provided in two temporal variants. In the second variant, an event of type ```Deliver Order``` is added to demonstrate its impact. For reference, the directory also includes our example Order-to-Cash (O2C) BPMN process model. Note that the process model itself does not influence the Data Object State evaluation directly but is provided for illustrative purposes.
-   ```src/```:
    This folder contains the prototype implementation, organized into four main categories:

    - Parsing: The scripts ```dmnParser.py``` and ```ocel2Parser.py``` handle parsing of the DMN tables and OCEL files, respectively, as specified in ```main.py```. These files should be located in the ```data/``` folder.
    - Utility Classes: The files ```dmnTable.py```, ```dmnInputType.py```, and ```genericObject.py``` provide utility classes to facilitate parsing and evaluation processes.
    - Cyclical Dependency Check: The logic to detect and handle cyclical dependencies is implemented in ```dmnGraph.py```.
    - Evaluation Logic: The state evaluation logic is implemented in ```dmnEvaluator.py```.

    The script ```main.py``` serves as the entry point for coordinating the entire process. It handles configuration and is required to test the implementation.
-   ```tests/```: This directory contains the unit tests for the project. The file ```tests_dmnEvaluator.py``` includes tests to verify the correctness of the state evaluation logic. The file ```test_dmnGraph.py``` contains tests to ensure the proper functioning of the cycle detection logic.
-   ```requirements.txt```: Lists the Python dependencies.

## Usage
Before running ```main.py```, it is recommended to execute the test scripts to ensure the project is set up correctly. The ```main.py``` script is configured to read the DMN tables for the ```Invoice``` and ```Order``` classes, along with the first event log. By default, it evaluates the states for the ```Ord1``` order.

The execution flow in ```main.py``` is as follows:

- Parsing the DMN tables and translating them into internal classes.
- Reading the OCEL log.
- Initializing the evaluator and checking for cyclical state dependencies. The debugging attribute of the ```DMNEvaluator``` object (enabled by default) provides a detailed evaluation log for ```debugging``` and understanding the functionality.
- Evaluating the state of an object from the log (by default, the ```Ord1``` order).

If a cycle is detected in the DMN tables, the program will terminate and automatically output a state dependency graph to help identify the issue. Additionally, the state dependency graph can be generated manually using ```evaluator.visualiseGraph()```.
<figure>
  <img src="data/demo-state-dependency-graph.png" alt="Image of a state dependency graph without cycle" width="500"/>
  <figcaption>Image of a state dependency graph without cycle</figcaption>
</figure>


## Limitations and Syntactic Sugar

This prototypical implementation serves as a visualization of the Data Object State concept presented in the paper “A Unified View on Data Object States.” It is important to note that the implementation differs in functionality and scope from the conceptual framework outlined in the paper. Key aspects to highlight include:

- Nested State Definitions: The ```state``` column at the beginning of the example DMN tables enables the construction of nested state definitions. In the paper, this corresponds to the helper function ```s(s, state, o)```. This feature is provided as syntactic sugar; the same functionality can be achieved manually by incorporating the conditions of the nested states directly into the parent state definition.

- Conditions on Links: Currently, conditions on links are limited to the functionality of ```amount()```—which calculates the number of existing links to objects of a class—and ```amount('X')```—which calculates the number of existing links to objects of a class in a specific state X. More advanced functions, such as checking for existence or evaluating conditions across all links, are left for future development.

- Conditions on Events: Conditions on events allow checking the number of events of a specific type using ```amount('type')```. However, temporal ordering of events is not considered, and it is not currently possible to access the values associated with events. These limitations will also be addressed in future work.

