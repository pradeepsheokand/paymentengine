Payment Engine
Dummy payment engine that reads a series of transactions from a CSV, updates client accounts, handles disputes and chargebacks, and then outputs the state of clients accounts as a CSV.

Packages to install
pip install -r requirements.txt

Run program
Clone the github repo- https://github.com/pradeepsheokand/paymentengine.git and from CLI execute following command to run the engine.

python payment_engine.py transactions.csv > client_accounts.csv

Input file: transactions.csv

Output file: client_accounts.csv (Output is generated on the stdout. In the command above it is redirected to client_accounts.csv file)

Instructions to Run the Python Testing Framework (PyTest):

Clone the GitHub Repo: https://github.com/pradeepsheokand/paymentengine.git to your local directory
If not already installed, Install Python version > 3.4
Create a virtual env using this python command: python -m venv c:\path\to\myenv
Activate above virtual env: \path\to\myenv\Scripts\activate
Install dependencies using this command (requirements.txt file below has complete dependencies for this project): pip install -r /path/to/requirements.txt requirements.txt
Set working directory as PYTHONPATH so that if you have modules in sub-directories then pytest can identify: set PYTHONPATH=\path\to\project;%PYTHONPATH%
Run this command to execute tests: pytest -vv testfactorialcalculator.py --html=reports/testreport.html
Run this command to find unit testing coverage: coverage run --source=src/ -m pytest -v tests/ && coverage report -m

