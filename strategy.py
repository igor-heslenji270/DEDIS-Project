from abc import ABC, abstractmethod
from typing import List
from . import models


class SearchStrategy(ABC):
    # Abstract base class for search strategies
    
    @abstractmethod
    def search(self, query: str, samples: List[models.Sample]) -> List[models.Sample]:
        pass


class ExactMatchStrategy(SearchStrategy):
    # Search for exact matches in taxonomy
    
    def search(self, query: str, samples: List[models.Sample]) -> List[models.Sample]:
        query_lower = query.lower()
        return [s for s in samples if query_lower in s.taxonomy.lower()]


class ApproximateMatchStrategy(SearchStrategy):
    # Search using approximate matching (allows small differences)
    
    def search(self, query: str, samples: List[models.Sample]) -> List[models.Sample]:
        from difflib import SequenceMatcher
        
        query_lower = query.lower()
        threshold = 0.6  # Similarity threshold
        results = []
        
        for sample in samples:
            similarity = SequenceMatcher(None, query_lower, sample.taxonomy.lower()).ratio()
            if similarity >= threshold:
                results.append(sample)
        
        return results


class HierarchicalMatchStrategy(SearchStrategy):
   # Search by taxonomic hierarchy (Bacteria;Proteobacteria;Gammaproteobacteria)
    
    def search(self, query: str, samples: List[models.Sample]) -> List[models.Sample]:
        query_parts = [part.strip().lower() for part in query.split(';')]
        results = []
        
        for sample in samples:
            taxonomy_parts = [part.strip().lower() for part in sample.taxonomy.split(';')]
            
            # Check if query parts match the beginning of taxonomy hierarchy
            if len(query_parts) <= len(taxonomy_parts):
                if all(q in t for q, t in zip(query_parts, taxonomy_parts)):
                    results.append(sample)
        
        return results


class AbundanceFilterStrategy(SearchStrategy):
    # Filter samples by abundance threshold
    
    def __init__(self, min_abundance: float = 0.0, max_abundance: float = 100.0):
        self.min_abundance = min_abundance
        self.max_abundance = max_abundance
    
    def search(self, query: str, samples: List[models.Sample]) -> List[models.Sample]:
        filtered = [s for s in samples 
                   if self.min_abundance <= s.abundance <= self.max_abundance]
        
        if query:
            query_lower = query.lower()
            filtered = [s for s in filtered if query_lower in s.taxonomy.lower()]
        
        return filtered


class SearchContext:
    # Context class that uses a search strategy
    
    def __init__(self, strategy: SearchStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: SearchStrategy):
        self._strategy = strategy
    
    def execute_search(self, query: str, samples: List[models.Sample]) -> List[models.Sample]:
        return self._strategy.search(query, samples)