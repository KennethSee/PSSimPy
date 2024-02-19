import unittest
from PSSimPy.queues.direct_queue import DirectQueue
from PSSimPy.transaction import Transaction

class TestQueue(unittest.TestCase):
    
    # Set up your test environment before each test method
    def setUp(self):
        self.q = DirectQueue()
        self.txn1 = Transaction('test1', 'test2', 1)
        self.txn2 = Transaction('test2', 'test1', 2)
    
    # Tear down your test environment after each test method
    def tearDown(self):
        # Clean up (if necessary)
        pass

    def test_enqueue(self):
        initial_size = len(self.q.queue)
        self.q.enqueue(self.txn1)
        self.assertEqual(len(self.q.queue), initial_size + 1, "Enqueue should increase queue size by 1.")

    def test_dequeue(self):
        current_period = self.q.period_counter
        self.q.enqueue(self.txn1)
        self.q.dequeue((self.txn1, current_period))
        self.assertEqual(len(self.q.queue), 0, "Dequeue should remove transaction from queue")


if __name__ == '__main__':
    unittest.main()