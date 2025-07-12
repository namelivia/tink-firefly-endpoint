class Summary:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Summary, cls).__new__(cls)
            cls._instance.data = []
        return cls._instance

    def add(self, item):
        self.data.append(item)

    def get(self):
        return self.data
