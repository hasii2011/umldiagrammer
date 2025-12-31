# UI Test Automation Suite

This directory contains a suite of UI automation tests for the UML Diagrammer application. These tests use the `pyautogui` library to simulate user interactions and verify the correctness of the application's behavior.

## Test Scripts

The main test scripts are:

- **`checkAggregation.py`**: This test automates the creation of a UML aggregation relationship between two classes. It verifies that the resulting project file contains the correct XML structure for the aggregation.
- **`checkclass.py`**: This test automates the creation of a UML class, including adding methods and fields. It verifies that the class is created with the correct properties and that the project file is saved correctly.
- **`checkComposition.py`**: This test automates the creation of a UML composition relationship between two classes. It verifies that the resulting project file contains the correct XML structure for the composition.
- **`checkInheritance.py`**: This test automates the creation of a UML inheritance relationship between two classes. It verifies that the resulting project file contains the correct XML structure for the inheritance.

Each of these test scripts performs the following steps:
1. Checks if the UML Diagrammer application is running.
2. Activates the application window.
3. Simulates user clicks and keyboard input to create UML elements.
4. Saves the created diagram as a project file (`.udt`).
5. Decompresses the project file (which is zlib compressed) to get the raw XML data.
6. Compares the generated XML with a "golden" XML string defined within the script. This comparison ignores unique IDs to focus on the structural correctness of the XML.
7. Displays a success or failure message to the user.

## Common Library

- **`common.py`**: This file contains a library of helper functions used by the test scripts. These functions encapsulate common tasks such as:
    - Checking if the application is running.
    - Activating the application window.
    - Saving a project.
    - Decompressing project files.
    - Comparing generated XML with a golden version.
    - Displaying test results.

## Utility Scripts

- **`FixIDRegExTest.py`**: A small utility script for testing and debugging the regular expression used to remove unique IDs from the generated XML files during the comparison process.
- **`trackmouse.py`**: A simple script that prints the current mouse coordinates to the console. This is useful for finding the screen coordinates needed for the `pyautogui` test scripts.

## Running the Tests

To run these tests, you need to have the UML Diagrammer application running. Then, you can execute each test script from your terminal. For example:

```bash

# from the project root
cd tests/uitests
uv run checkclass.py

```

**Note:** These tests are highly dependent on screen resolution and window placement. The current tests were record on a screen size of width=2560, height=1440.  The coordinates in the scripts may need to be adjusted for your specific environment. The `trackmouse.py` utility can be used to find the correct coordinates.
