from abc import ABC, abstractmethod
from collections import defaultdict

from PSSimPy.account import Account

class AbstractCreditFacility(ABC):
    
    def __init__(self) -> None:
        super().__init__()
        self.total_credit = defaultdict(float)
        self.total_fee = defaultdict(float)
        
    def collect_all_repayment(self, accounts: list[Account]) -> None:
        """
        Collect all repayment of a list of accounts.

        :param accounts: List of participants' account
        """
        for account in accounts:
            self.collect_repayment(account=account)
        
    def get_total_credit(self, account: Account) -> float:
        """
        Obtain the total amount of credit lent to a participant.
               
        :param account: Participant's account
        :return: The total amount of credit
        """
        return self.total_credit[account.id]
    
    def get_total_fee(self, account: Account) -> float:
        """
        Obtain the total fee amount for a participant.
        
        :param account: Participant's account
        :return: The total fee amount
        """
        return self.total_fee[account.id]
    
    def get_total_credit_and_fee(self, account: Account) -> float:
        """
        Obtain the total amount of credit and fee for a participant.

        :param account: Participant's account
        :return: The total amount of credit and fee
        """
        return self.total_credit[account.id] + self.total_fee[account.id]
        
    @abstractmethod
    def lend_credit(self, account: Account, amount: float) -> None:
        """
        Lend a specified amount of credit to a participant.
        
        It should be implemented such that for a given account, the amount of total credit and total fee is added. No return is expected.
        
        :param account: Participant's account
        :param amount: The amount of credit to lend
        """
        pass
    
    @abstractmethod
    def collect_repayment(self, account: Account) -> None:
        """
        Collect repayment of a previously lent amount from a participant.
        
        It should be implemented such that for a given account, the amount of total credit and total fee is reduced. No return is expected.
        
        :param account: Participant's account
        :param amount: The amount of repayment to collect
        """
        pass
