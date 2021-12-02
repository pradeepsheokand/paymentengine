# Payment Engine

Dummy payment engine that reads a series of transactions from a CSV, updates client accounts, handles disputes and chargebacks, and then outputs the state of clients accounts as a CSV.


## Instructions to Run the Source Code and Tests based on Python Testing Framework (PyTest):

1. Clone the GitHub Repo: https://github.com/pradeepsheokand/paymentengine.git to your local directory
2. If not already installed, Install Python version > 3.4
3. Create a virtual env using this python command: python -m venv c:\path\to\myenv
4. Activate above virtual env: \path\to\myenv\Scripts\activate
5. Install dependencies using this command (requirements.txt file below has complete dependencies for this project): pip install -r /path/to/requirements.txt requirements.txt
6. Set working directory as PYTHONPATH so that if you have modules in sub-directories then pytest can identify: set PYTHONPATH=\path\to\project;%PYTHONPATH%
7. Please include this file- src/clients_existing_accounts_balances.csv when you clone the repo and keep it in same directory as payment_engine.py and transactions file. This **should NOT** be passed as a parameter (command line parameter) to the payment_engine.py as program includes it by default. Only transactions.csv is required to be passed in the parameter.
8. Run this command to execute source code: python src/payment_engine.py src/transactions.csv > output/client_accounts.csv
9. Run this command to execute tests: pytest -vv testfactorialcalculator.py --html=reports/testreport.html
10. Run this command to find unit testing coverage: coverage run --source=src/ -m pytest -v tests/ && coverage report -m

## Continuous Integration :
CircleCI config is set-up in this repo for Continuous Integration and performs these steps (results from the circleci build runs are attached in the output and test-execution-reports folders):
- Spin up a VM (ubuntu machine) and build a docker image with python 3.9 version installed on it
- Checkout code and install dependencies using requirements.txt
- Run source code i.e. payment_engine.py using transactions.csv as input and redirect the output to client_accounts.csv file, output file generated is attached in the output folder
- Run tests using pytest framework, generate test execution output in a HTML report attached in test-execution-reports folder
- Run unit testing coverage, output is generated along with the tests run and attached under test-execution-reports -> test-console-logs folder (Note: Python Main function is excluded from the coverage report). Coverage is found to be 95% . Missing Coverage is in the function that writes csv as output.  

