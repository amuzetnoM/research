class QueryEngine:
    def __init__(self, db, ai_module=None):
        self.db = db
        self.ai = ai_module

    def search_by_hash(self, memory_hash):
        return self.db.get_memory(memory_hash)

    def search_by_summary(self, summary):
        # Placeholder: search summaries in db
        return []

    def semantic_search(self, query):
        if self.ai:
            return self.ai.semantic_search(query, self.db)
        return []
