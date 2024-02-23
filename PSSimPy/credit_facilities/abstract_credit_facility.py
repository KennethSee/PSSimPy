from abc import ABC, abstractmethod
from collections import defaultdict

from PSSimPy.account import Account

class AbstractCreditFacility(ABC):
    
    def __init__(self) -> None:
        super().__init__()
        self.used_credit = defaultdict(list)
        
    def collect_all_repayment(self, accounts: list[Account]) -> None:
        """
        Collect all repayment of a list of accounts.

        :param accounts: List of participants' account
        """
        for account in accounts:
            self.collect_repayment(account=account)
            
    @abstractmethod
    def calculate_fee(self) -> float:
        """
        Calculate the fee amount for a credit lent to a participant.

        :return: The fee amount
        """
        pass
        
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

    def get_total_credit(self, account: Account) -> float:
        """
        Obtain the total amount of credit lent to a participant.
               
        :param account: Participant's account
        :return: The total amount of credit
        """
        return sum(self.used_credit[account.id])

    def get_total_fee(self, account: Account) -> float:
        """
        Obtain the total fee amount for a participant.
        
        :param account: Participant's account
        :return: The total fee amount
        """
        return sum([self.calculate_fee(x) for x in self.used_credit[account.id]])
    
    def get_total_credit_and_fee(self, account: Account) -> float:
        """
        Obtain the total amount of credit and fee for a participant.

        :param account: Participant's account
        :return: The total amount of credit and fee
        """
        return self.get_total_credit(account) + self.get_total_fee(account)