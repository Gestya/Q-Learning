from collections import deque


class MsgQueue:
    def __init__(self):
        self.inbox = deque()
        self.outbox = deque()

    def push_to_inbox(self, msg):
        self.inbox.append(msg)

    def pop_from_inbox(self):
        if len(self.inbox):
            return self.inbox.popleft()
        else:
            return ''

    def push_to_outbox(self, msg):
        self.outbox.append(msg)

    def pop_from_outbox(self):
        if len(self.outbox):
            return self.outbox.popleft()
        else:
            return ''
