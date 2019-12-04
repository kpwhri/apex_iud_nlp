# Background

NLP code used to identify various IUD-related events in clinical text.

# Usage

1. Use `example/example_config.py` to build a configuration file. See instruction therein.
2. Run `apex/main.py` or `apex/__main__.py`'
    * `set/export PYTHONPATH=path/to/src`
    * `python -m apex config.py` or `python path/to/src/apex/main.py`

## Configuration
Configuration is provided by a Python file, a json file, or a yaml file. An example Python config file is provided (please note that the print statement at the end is required).

Input can be specified as lists of directories and database connections.

## Running the Application
0. Build `config.py` file
1. Set the environment variable PYTHONPATH to the apex_iud_nlp/src directory
    * Windows: `set PYTHONPATH=C:\apex_iud_nlp\src`
    * Unix: `export PYTHONPATH=/usr/apex_iud_nlp/src`
2. Run the program...either:
    * `python -m apex config.py`
    * `python path/to/apex_iud_nlp/src/apex/main.py config.py`

## Updating the Algorithms

It is unlikely that this algorithm will work without local modifications to account for variations in language use at different sites. Nevertheless, it should serve as a useful starting point.

1. Open the python file related to the algorithm under consideration
2. Update the regular expressions (at the top) or add a new one
    * `negates` argument: list of regular expressions that will exclude the pattern from matching
    * Add/run tests to confirm performance
3. Organize the patterns/regular expressions in the algorithm function

## Post-processing
This application will produce an output file (or database table) containing the id of the note under consideration, as well as all relevant events/findings. These can then be used to develop an algorithm to determine the status in each of these cases.

1. Review the results and the relevant text to validate performance
2. Improve the regular expressions or pattern logic
3. Aggregate/organize results into an algorithm to determine events/event date

## Reviewing Snippets/Samples
The file apex/anlz/summary.py is provided for analyzing results along with the relevant snippets which triggered the event/finding. This will require the `docx` library (`pip install python-docx`; for Windows, install can use wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/, search "docx").

# Support
This package was originally written as part of a larger project looking at potential risks of IUD usage while breast-feeding. Funding for this study was provided by Bayer.
