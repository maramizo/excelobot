class IndexedMessage:
    def __init__(self, index, max_index, author, channel):
        self.index = index
        self.max_index = max_index
        self.author = author
        self.channel = channel

    def next(self):
        if self.index < (self.max_index - 1):
            self.index += 1
        return self.index

    def prev(self):
        if self.index > 0:
            self.index -= 1
        return self.index
