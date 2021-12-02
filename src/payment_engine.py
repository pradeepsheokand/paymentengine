import sys
import csv
import numpy as np
import pandas as pd
from decimal import *

# Setting decimal precision to 4
getcontext().prec = 4

# Client class holds all the client related details
class Client:

    def __init__(self, client_id, available, held, total, locked):
        self.client_id = client_id
        self.available_balance = available
        self.held_amount = held
        self.total_amount = total
        self.disputed_transactions = set()
        self.locked = locked

    def deposit(self, amount):
        """Deposit given amount in clients account """
        if not self.locked:
            self.available_balance += Decimal(str(amount))
            self.total_amount += Decimal(str(amount))

    def withdrawal(self, amount):
        """Withdraw/Debit given amount from the clients account """
        if not self.locked and self.available_balance >= Decimal(str(amount)):
            self.available_balance -= Decimal(str(amount))
            self.total_amount -= Decimal(str(amount))

    def dispute(self, disputed_amount, txn_id):
        """When client raises a dispute for a specific transaction,the associated amount should be held.
        Clients available balance should decrease by the amount disputed but the total fund should remain the same until
        dispute resolved or charged back"""
        if not self.locked and self.available_balance >= Decimal(str(disputed_amount)):
            self.available_balance -= Decimal(str(disputed_amount))
            self.held_amount += Decimal(str(disputed_amount))
            self.disputed_transactions.add(txn_id)

    def resolve(self, disputed_amount, txn_id):
        """Resolve indicates resolution to a dispute and releases held amounts for the transaction.
        Disputed/held amount should move from held balance to available balances."""
        if not self.locked and txn_id in self.disputed_transactions:
            self.held_amount -= Decimal(disputed_amount)
            self.available_balance += Decimal(disputed_amount)
            self.disputed_transactions.remove(txn_id)

    def chargeback(self, disputed_amount, txn_id):
        """Chargeback indicates another final state of a disputed transaction.
        It represents the client reversing a transaction.Disputed amount should be removed from held amount
        and total balances should be reduced by disputed amount."""
        if not self.locked and txn_id in self.disputed_transactions:
            self.held_amount -= Decimal(disputed_amount)
            self.total_amount -= Decimal(disputed_amount)
            self.locked = True
            self.disputed_transactions.remove(txn_id)


# PaymentEngine class is the main class to process all transactions from transactions input file
class PaymentEngine:

    def __init__(self, transactions_file, client_details_file):
        self.transactions_df = pd.read_csv(transactions_file)
        self.output_file = None
        self.clients = {}
        df1 = pd.read_csv(client_details_file)
        df1['locked'] = df1['locked'].astype('bool')
        clients_dict = df1.set_index("client").to_dict("index")
        for key, value in clients_dict.items():
            self.clients[key] = Client(key, Decimal(value['available']), Decimal(value['held']),
                                       Decimal(value['total']), (value['locked']))

        self.txn_array = self.transactions_df[["txn"]].to_numpy(dtype=np.uint32)

    def process_transactions(self):
        """Process all transactions from input transactions file."""
        try:
            for idx, txn_data in self.transactions_df.iterrows():
                if txn_data["type"] == "deposit":
                    if not self.is_client_exists(txn_data["client"]):
                        self.create_client(txn_data["client"])
                    self.deposit(txn_data)

                if txn_data["type"] == "withdraw":
                    self.withdraw(txn_data)

                if txn_data["type"] == "dispute":
                    self.dispute(txn_data)

                if txn_data["type"] == "resolve":
                    self.resolve(txn_data)

                if txn_data["type"] == "chargeback":
                    self.chargeback(txn_data)
        except Exception as e:
            print(f"Exception: {e}")

    def create_client(self, client_id):
        """Create new client with given client_id"""
        self.clients[client_id] = Client(client_id, 0, 0, 0, False)

    def is_client_exists(self, client_id):
        """Check if a client exists"""
        if client_id in self.clients:
            return True
        return False

    def deposit(self, txn_data):
        """Deposit to client account and update the available
        and total balance of the client account."""
        client, amount = txn_data["client"], txn_data["amount"]
        client_data = self.clients[client]
        client_data.deposit(amount)

    def withdraw(self, txn_data):
        """Withdraw debit's from the client’s account and decrease the available and total balances."""
        client, amount = txn_data["client"], txn_data["amount"]
        client_data = self.clients[client]
        client_data.withdrawal(amount)

    def dispute(self, txn_data):
        """When client raises a dispute for a specific transaction for error or issue.
        Dispute has transaction id , amount picked from original transaction using transaction Id"""
        txn_id = txn_data["txn"]
        if txn_id in self.txn_array:
            client_txn_data = self.transactions_df.query('txn == @txn_id & type != "dispute"').iloc[0, :]
            if txn_data["client"] == client_txn_data["client"] \
                    and self.is_client_exists(txn_data["client"]) \
                    and client_txn_data['type'] == "deposit":
                client_data = self.clients[txn_data["client"]]
                client_data.dispute(client_txn_data["amount"], client_txn_data["txn"])

    def resolve(self, txn_data):
        """Resolve represents a resolution to a dispute. Resolve does not specify an amount just like dispute,
        it has transaction id which refers to transaction in dispute and now been resolved.
        Only action if transaction id exist else do nothing"""
        txn_id = txn_data["txn"]
        if txn_id in self.txn_array:
            client_txn_data = self.transactions_df.query('txn == @txn_id & type != "dispute"').iloc[0, :]
            if txn_data["client"] == client_txn_data["client"] \
                    and self.is_client_exists(txn_data["client"]) \
                    and client_txn_data["type"] == "deposit":
                client_data = self.clients[txn_data["client"]]
                client_data.resolve(client_txn_data["amount"],
                                    client_txn_data["txn"])

    def chargeback(self, txn_data):
        """Chargeback represents the client reversing a transaction. Chargeback does not specify an amount like dispute,
        it has transaction id which refers to transaction in dispute and now been resolved.
        Only action if transaction id exist else do nothing"""
        txn_id = txn_data["txn"]
        if txn_id in self.txn_array:
            client_txn_data = self.transactions_df.query('txn == @txn_id & type != "dispute"').iloc[0, :]
            if txn_data["client"] == client_txn_data["client"] \
                    and self.is_client_exists(txn_data["client"]) \
                    and client_txn_data["type"] == "deposit":
                client_data = self.clients[txn_data["client"]]
                client_data.chargeback(client_txn_data["amount"], client_txn_data["txn"])

    def write_results(self): # pragma: no cover
        header = ["client", "available", "held", "total", "locked"]
        self.output_file = csv.DictWriter(sys.stdout, header)
        self.output_file.writeheader()
        for client_id, client in self.clients.items():
            self.output_file.writerow({
                "client": client_id,
                "available": client.available_balance,
                "held": client.held_amount,
                "total": client.total_amount,
                "locked": client.locked
            })


if __name__ == '__main__': # pragma: no cover
    client_account_csv = 'src/client_accounts.csv'
    try:
        transactions_csv = sys.argv[1]
    except IndexError:
        transactions_csv = 'transactions.csv'
    payment_engine = PaymentEngine(transactions_csv, client_account_csv)
    payment_engine.process_transactions()
    payment_engine.write_results()
