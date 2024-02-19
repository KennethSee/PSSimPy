import unittest
from PSSimPy.queues import DirectQueue, FIFOQueue, PriorityQueue
from PSSimPy import Transaction
from PSSimPy import Account

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

    def test_sorting_logic(self):
        acc1 = Account('acc1', None, 1)
        acc2 = Account('acc2', None, 1)
        txn1 = Transaction(acc1, acc2, 1)
        txn2 = Transaction(acc2, acc1, 1)
        fifo_queue = FIFOQueue()
        fifo_queue.enqueue(txn1)
        fifo_queue.next_period()
        fifo_queue.enqueue(txn2)
        dequeued_txns = fifo_queue.begin_dequeueing()
        self.assertEqual(len(dequeued_txns), 2, "Both transactions should have been dequeued")
        self.assertEqual(dequeued_txns[0].sender_account.id, 'acc1', "Wrong order of dequeueing")

    def test_dequeue_condition(self):
        acc1 = Account('acc1', None, 0)
        acc2 = Account('acc2', None, 1)
        txn1 = Transaction(acc1, acc2, 1)
        txn2 = Transaction(acc2, acc1, 1)
        fifo_queue = FIFOQueue()
        fifo_queue.enqueue(txn1)
        fifo_queue.next_period()
        fifo_queue.enqueue(txn2)
        dequeued_txns = fifo_queue.begin_dequeueing()
        self.assertEqual(len(dequeued_txns), 1, "Only one transaction should have been eligible to be dequeued")
        self.assertEqual(dequeued_txns[0].sender_account.id, 'acc2', "Wrong transaction dequeued")


if __name__ == '__main__':
    unittest.main()