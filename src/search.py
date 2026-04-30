class SearchEngine:
    def __init__(self, index):
        self.index = index

    def find(self, query):
        """
        Find pages containing all words in the query.
        Returns a list of URLs.
        """
        words = query.lower().split()
        if not words:
            return []

        # Start with the set of URLs for the first word
        first_word = words[0]
        if first_word not in self.index:
            return []
        
        result_urls = set(self.index[first_word].keys())

        # Intersect with URLs of subsequent words
        for word in words[1:]:
            if word not in self.index:
                return []  # One of the words not found, so intersection is empty
            result_urls.intersection_update(self.index[word].keys())

        return list(result_urls)

    def print_word_info(self, word):
        """
        Return the inverted index entry for a word as a string.
        """
        word = word.lower()
        if word not in self.index:
            return f"Word '{word}' not found in index."
        
        entry = self.index[word]
        output = [f"Inverted index for '{word}':"]
        for url, stats in entry.items():
            output.append(f"  URL: {url}")
            output.append(f"    Frequency: {stats['frequency']}")
            output.append(f"    Positions: {stats['positions']}")
        
        return "\n".join(output)
