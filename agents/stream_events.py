class RunItemStreamEvent:
    def __init__(self, item=None):
        self.item = item

class RawResponsesStreamEvent:
    def __init__(self, data=None):
        self.data = data

class AgentUpdatedStreamEvent:
    def __init__(self, new_agent=None):
        self.new_agent = new_agent
