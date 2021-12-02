# payment_engine.py unit tests written using PyTest framework
import pytest
import pytest_html
from decimal import *
from io import StringIO
from src.payment_engine import PaymentEngine
import logging
import sys
import datetime

# Setting decimal precision to 4
getcontext().prec = 4

LOGGER = logging.getLogger('pytest.ini')

# Below test data represents Clients Accounts existing balance, this is created as a fixture and passed in other tests
@pytest.fixture
def client_csv():
    return StringIO(
        "client,available,held,total,locked\n"
        "1,10.0,0.0,10.0,0\n"
        "2,20.0,2.0,22.0,1\n"
        "3,30.0,0.0,30.0,0\n"
    )


# Test#1: deposit and withdrawal transactions that updates existing client accounts balances
@pytest.mark.smoke
def test_deposit_withdraw_transactions(client_csv):
    in_mem_transaction_csv = StringIO(
        "type,client,txn,amount\n"
        "deposit,1,1,1.0\n"
        "deposit,1,2,2.0\n"
        "withdraw,1,3,1.5\n"
        "deposit,11,12,2.0\n"
    )
    app = PaymentEngine(in_mem_transaction_csv, client_csv)
    app.process_transactions()
    client1 = app.clients[1]
    client11 = app.clients[11]
    LOGGER.info(f"client1 available balance: = {client1.available_balance}")
    LOGGER.info(f"client11 available balance: = {client11.available_balance}")
    assert client1.available_balance == Decimal(11.5)
    assert client11.available_balance == Decimal(2.0)


# Test#2: case when a disputed deposit transaction exist for a client
def test_dispute_transactions(client_csv):
    in_mem_transaction_csv = StringIO(
        "type,client,txn,amount\n"
        "deposit,1,1,3.0\n"
        "withdraw,1,2,1.0\n"
        "dispute,1,1\n"
    )
    app = PaymentEngine(in_mem_transaction_csv, client_csv)
    app.process_transactions()
    client1 = app.clients[1]
    LOGGER.info(f"client1 available balance: = {client1.available_balance}")
    LOGGER.info(f"client1 held balance: = {client1.held_amount}")
    LOGGER.info(f"client1 total balance: = {client1.total_amount}")
    assert client1.available_balance == Decimal(9.0)
    assert client1.held_amount == Decimal(3.0)
    assert client1.total_amount == Decimal(12.0)


# Test#3: case when disputed transaction exist for a client and available funds are less than disputed amount
def test_dispute_with_insufficient_available_balance(client_csv):
    in_mem_transaction_csv = StringIO(
        "type,client,txn,amount\n"
        "deposit,1,1,2.0\n"
        "withdraw,1,2,12.0\n"
        "dispute,1,1\n"
    )

    app = PaymentEngine(in_mem_transaction_csv, client_csv)
    app.process_transactions()
    client1 = app.clients[1]
    LOGGER.info(f"client1 available balance: = {client1.available_balance}")
    LOGGER.info(f"client1 held balance: = {client1.held_amount}")
    LOGGER.info(f"client1 total balance: = {client1.total_amount}")
    assert client1.available_balance == Decimal(0.0)
    assert client1.held_amount == Decimal(0.0)
    assert client1.total_amount == Decimal(0.0)


# Test#4: case when transaction is disputed and resolved
def test_txn_with_dispute_and_resolve(client_csv):
    in_mem_transaction_csv = StringIO(
        "type,client,txn,amount\n"
        "deposit,1,1,1.0\n"
        "deposit,1,2,2.0\n"
        "dispute,1,2\n"
        "resolve,1,2"
    )
    app = PaymentEngine(in_mem_transaction_csv, client_csv)
    app.process_transactions()
    client1 = app.clients[1]
    LOGGER.info(f"client1 available balance: = {client1.available_balance}")
    LOGGER.info(f"client1 held balance: = {client1.held_amount}")
    assert client1.available_balance == Decimal(13.0)
    assert client1.held_amount == Decimal(0.0)


# Test#5: case when a disputed txn is turned as a chargeback
def test_txn_with_chargeback(client_csv):
    in_mem_transaction_csv = StringIO(
        "type,client,txn,amount\n"
        "deposit,1,1,1.0\n"
        "deposit,1,2,2.0\n"
        "dispute,1,2\n"
        "chargeback,1,2"
    )
    app = PaymentEngine(in_mem_transaction_csv, client_csv)
    app.process_transactions()
    client1 = app.clients[1]
    LOGGER.info(f"client1 available balance: = {client1.available_balance}")
    LOGGER.info(f"client1 held balance: = {client1.held_amount}")
    LOGGER.info(f"client1 total balance: = {client1.total_amount}")
    assert client1.available_balance == Decimal(11.0)
    assert client1.held_amount == Decimal(0.0)
    assert client1.total_amount == Decimal(11.0)
    assert client1.locked is True


# Test#6: case when a chargeback occurs, and held amount is not sufficient
def test_chargeback_with_insufficient_funds(client_csv):
    in_mem_transaction_csv = StringIO(
        "type,client,txn,amount\n"
        "deposit,1,1,3.0\n"
        "deposit,1,2,2.0\n"
        "dispute,1,2\n"
        "chargeback,1,1"
    )
    app = PaymentEngine(in_mem_transaction_csv, client_csv)
    app.process_transactions()
    client1 = app.clients[1]
    LOGGER.info(f"client1 available balance: = {client1.available_balance}")
    LOGGER.info(f"client1 held balance: = {client1.held_amount}")
    LOGGER.info(f"client1 total balance: = {client1.total_amount}")
    assert client1.available_balance == Decimal(13.0)
    assert client1.held_amount == Decimal(2.0)
    assert client1.total_amount == Decimal(15.0)
    assert client1.locked is False


# Test#7: case when a client try to deposit on a locked account
def test_deposit_after_chargeback(client_csv):
    in_mem_transaction_csv = StringIO(
        "type,client,txn,amount\n"
        "deposit,1,1,3.0\n"
        "deposit,1,2,2.0\n"
        "dispute,1,1\n"
        "chargeback,1,1\n"
        "deposit,1,1,10.0\n"
    )
    app = PaymentEngine(in_mem_transaction_csv, client_csv)
    app.process_transactions()
    client1 = app.clients[1]
    LOGGER.info(f"client1 available balance: = {client1.available_balance}")
    LOGGER.info(f"client1 held balance: = {client1.held_amount}")
    LOGGER.info(f"client1 total balance: = {client1.total_amount}")
    assert client1.available_balance == Decimal(12.0)
    assert client1.held_amount == Decimal(0.0)
    assert client1.total_amount == Decimal(12.0)
    assert client1.locked is True


# Test#8: case when a client try to perform a withdrawal on locked account
def test_withdrawal_after_chargeback(client_csv):
    in_mem_transaction_csv = StringIO(
        "type,client,txn,amount\n"
        "deposit,1,1,3.0\n"
        "deposit,1,2,2.0\n"
        "dispute,1,1\n"
        "chargeback,1,1\n"
        "withdraw,1,1,1.5\n"
    )
    app = PaymentEngine(in_mem_transaction_csv, client_csv)
    app.process_transactions()
    client1 = app.clients[1]
    LOGGER.info(f"client1 available balance: = {client1.available_balance}")
    LOGGER.info(f"client1 held balance: = {client1.held_amount}")
    LOGGER.info(f"client1 total balance: = {client1.total_amount}")
    assert client1.available_balance == Decimal(12.0)
    assert client1.held_amount == Decimal(0.0)
    assert client1.total_amount == Decimal(12.0)
    assert client1.locked is True


# Test#9: case when there is a dispute on a withdrawal txn
def test_dispute_on_withdrawal(client_csv):
    in_mem_transaction_csv = StringIO(
        "type,client,txn,amount\n"
        "deposit,1,1,3.0\n"
        "deposit,1,2,2.0\n"
        "withdraw,1,3,1.5\n"
        "dispute,1,3\n"
    )
    app = PaymentEngine(in_mem_transaction_csv, client_csv)
    app.process_transactions()
    client1 = app.clients[1]
    LOGGER.info(f"client1 available balance: = {client1.available_balance}")
    LOGGER.info(f"client1 held balance: = {client1.held_amount}")
    LOGGER.info(f"client1 total balance: = {client1.total_amount}")
    assert client1.available_balance == Decimal(13.5)
    assert client1.held_amount == Decimal(0.0)
    assert client1.total_amount == Decimal(13.5)
    assert client1.locked is False


# Test#10: case when there is a dispute raised on a transaction that doesn't exist
def test_dispute_when_txn_not_exist(client_csv):
    in_mem_transaction_csv = StringIO(
        "type,client,txn,amount\n"
        "deposit,1,1,3.0\n"
        "deposit,1,2,2.0\n"
        "withdraw,1,3,1.5\n"
        "dispute,1,4\n"
    )
    app = PaymentEngine(in_mem_transaction_csv, client_csv)
    app.process_transactions()
    client1 = app.clients[1]
    LOGGER.info(f"client1 available balance: = {client1.available_balance}")
    LOGGER.info(f"client1 held balance: = {client1.held_amount}")
    LOGGER.info(f"client1 total balance: = {client1.total_amount}")
    assert client1.available_balance == Decimal(13.5)
    assert client1.held_amount == Decimal(0.0)
    assert client1.total_amount == Decimal(13.5)
    assert client1.locked is False


# Test#11: case when there is a resolve event when given transaction doesn't exist
def test_resolve_when_txn_not_exist(client_csv):
    in_mem_transaction_csv = StringIO(
        "type,client,txn,amount\n"
        "deposit,1,1,3.0\n"
        "deposit,1,2,2.0\n"
        "dispute,1,2\n"
        "resolve,1,4\n"
    )
    app = PaymentEngine(in_mem_transaction_csv, client_csv)
    app.process_transactions()
    client1 = app.clients[1]
    LOGGER.info(f"client1 available balance: = {client1.available_balance}")
    LOGGER.info(f"client1 held balance: = {client1.held_amount}")
    LOGGER.info(f"client1 total balance: = {client1.total_amount}")
    assert client1.available_balance == Decimal(13.0)
    assert client1.held_amount == Decimal(2.0)
    assert client1.total_amount == Decimal(15.0)
    assert client1.locked is False


# Test#12: case when client against which dispute is raised doesn't match with resolve client for same txn id
def test_when_dispute_client_not_match(client_csv):
    in_mem_transaction_csv = StringIO(
        "type,client,txn,amount\n"
        "deposit,1,1,3.0\n"
        "deposit,1,2,2.0\n"
        "dispute,12,2\n"
        "resolve,1,2\n"
    )
    app = PaymentEngine(in_mem_transaction_csv, client_csv)
    app.process_transactions()
    client1 = app.clients[1]
    LOGGER.info(f"client1 available balance: = {client1.available_balance}")
    LOGGER.info(f"client1 held balance: = {client1.held_amount}")
    LOGGER.info(f"client1 total balance: = {client1.total_amount}")
    assert client1.available_balance == Decimal(15.0)
    assert client1.held_amount == Decimal(0.0)
    assert client1.total_amount == Decimal(15.0)
    assert client1.locked is False


# Test#13: case when dispute and resolve clients do not match
def test_when_resolve_client_do_not_match(client_csv):
    in_mem_transaction_csv = StringIO(
        "type,client,txn,amount\n"
        "deposit,1,1,3.0\n"
        "deposit,1,2,2.0\n"
        "dispute,1,2\n"
        "resolve,12,2\n"
    )
    app = PaymentEngine(in_mem_transaction_csv, client_csv)
    app.process_transactions()
    client1 = app.clients[1]
    LOGGER.info(f"client1 available balance: = {client1.available_balance}")
    LOGGER.info(f"client1 held balance: = {client1.held_amount}")
    LOGGER.info(f"client1 total balance: = {client1.total_amount}")
    assert client1.available_balance == Decimal(13.0)
    assert client1.held_amount == Decimal(2.0)
    assert client1.total_amount == Decimal(15.0)
    assert client1.locked is False


# Test#14: case to check transactions decimal precision of 4
def test_txn_decimal_precision(client_csv):
    in_mem_transaction_csv = StringIO(
        "type,client,txn,amount\n"
        "deposit,11,1,1.1234\n"
        "deposit,11,2,2.1234\n"
    )
    app = PaymentEngine(in_mem_transaction_csv, client_csv)
    app.process_transactions()
    client11 = app.clients[11]
    assert client11.available_balance == round(Decimal(1.1234), 3) + round(Decimal(2.1234), 3)
