from multiprocessing import Queue, Process


class PlayerProcessing(Process):
    def __init__(self, ai_cls):
        super().__init__()
        self.queue = Queue()

