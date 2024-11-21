# A Unified View on Data Object States - Prototypical Implementation

This repository contains the prototypical implementation of the data object state concept introduced in our paper, *"A Unified View on Data Object States."* This work bridges the gap between process control flow and data management by formalizing and generalizing the definition of data object states in business process models.


## Getting Started

### Prerequisites

Ensure you have the following installed:

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/WilliamBrandt/Data-Object-State-Abstraction.git
    cd Data-Object-State-Abstraction
    ```

2. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

---

## Project Structure

- **`data/`**: Contains the specifications required for evaluating Data Object States:
  - DMN tables for the `Order` and `Invoice` classes.
  - An OCEL log in two temporal variants (one includes an additional `Deliver Order` event).
  - A reference Order-to-Cash (O2C) BPMN process model, provided for illustrative purposes only (it does not affect the state evaluation).

- **`src/`**: Contains the prototype implementation:
  - **Parsing**:
    - `dmnParser.py`: Parses DMN tables.
    - `ocel2Parser.py`: Parses OCEL files.
  - **Utility Classes**: 
    - `dmnTable.py`, `dmnInputType.py`, and `genericObject.py` provide core classes for parsing and evaluation.
  - **Cyclical Dependency Check**: 
    - `dmnGraph.py` detects and handles cyclical dependencies.
  - **State Evaluation Logic**:
    - `dmnEvaluator.py` implements the logic for evaluating data object states.
  - `main.py`: Coordinates the entire process. This script serves as the entry point for testing and configurations.

- **`tests/`**: Contains unit tests:
  - `tests_dmnEvaluator.py`: Validates the correctness of state evaluation logic.
  - `test_dmnGraph.py`: Ensures proper functioning of cycle detection logic.

- **`requirements.txt`**: Specifies the Python dependencies for the project.


## Usage

1. **Run Tests**:
   Before executing `main.py`, it is recommended to run the unit tests to verify the setup:
    ```
    python .\tests_dmnEvaluator.py
    python .\tests_dmnGraph.py
    ```
2. **Execute the Prototype**: 
    Run main.py to evaluate the state of data objects:
    ```
    python .\main.py
    ```
    By default, the script reads the DMN tables for `Invoice` and `Order`, along with the first event log. It evaluates the states of the `Ord1` order.

## Execution Flow in `main.py`
1. Parse DMN tables and translate them into internal classes.
2. Read the OCEL log.
3. Initialize the evaluator and check for cyclical state dependencies. (Use the `debugging` attribute in the `DMNEvaluator` object to enable detailed evaluation logs.)
4. Evaluate the state of a data object from the log (default: the order with id `Ord1`).

If a cycle is detected in the DMN tables, the program terminates and outputs a state dependency graph to identify the issue. You can also manually generate the graph using: `evaluator.visualiseGraph()`:
<figure>
  <img src="data/demo-state-dependency-graph.png" alt="Image of a state dependency graph without cycle" width="500"/>
  <figcaption>Image of a state dependency graph without cycle</figcaption>
</figure>


## Limitations and Syntactic Sugar

This implementation serves as a visualization of the concepts presented in the paper. It differs in functionality and scope from the theoretical framework. Key aspects to highlight:

- **Nested State Definitions**: The `state` column at the beginning of the example DMN tables enables the construction of nested state definitions. In the paper, this corresponds to the helper function `s(s, state, o)`. This feature is provided as syntactic sugar; the same functionality can be achieved manually by incorporating the conditions of the nested states directly into the parent state definition.

- **Conditions on Links**: Currently, conditions on links are limited to the functionality of `amount()`—which calculates the number of existing links to objects of a class—and `amount('X')`—which calculates the number of existing links to objects of a class in a specific state X. More advanced functions, such as checking for existence or evaluating conditions across all links, are left for future development.

- **Conditions on Events**: Conditions on events allow checking the number of events of a specific type using ```amount('type')```. However, temporal ordering of events is not considered, and it is not currently possible to access the values associated with events. These limitations will also be addressed in future work.

## Example Output
By default, the system evaluates the states of the order with id `Ord1`.

**Initial State Evaluation:**
The system detects `Ord1` as being in the `valid`, `paid` and `ready` states.

**Adding an DeliverOrder Event:**
After appending an `deliverOrder` event linked to `Ord1` (by using the extended event log `O2C_event_log_with_DeliverOrder.json`) and reevaluating, the system places `Ord1`  in the `valid`, `paid`, and `sent` states.