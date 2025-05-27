def get(url, timeout=10):
    class Resp:
        status_code = 200
        def raise_for_status(self):
            pass
        def json(self):
            return {"RelatedTopics": []}
        @property
        def text(self):
            return ""
    return Resp()
