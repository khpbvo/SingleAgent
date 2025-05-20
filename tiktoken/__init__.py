class DummyEncoding:
    def encode(self, text):
        return text.split()

def encoding_for_model(model):
    return DummyEncoding()
