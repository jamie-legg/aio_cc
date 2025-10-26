import React, { useState, useEffect } from 'react';
import DocsLayout from '../components/DocsLayout';

interface Doc {
  filename: string;
  title: string;
  description: string;
}

interface Category {
  name: string;
  description: string;
  docs: Doc[];
}

interface DocsIndex {
  categories: Record<string, Category>;
}

interface SearchResult {
  category: string;
  category_name: string;
  filename: string;
  title: string;
  description: string;
  snippet: string;
}

const DOCS_API_BASE_URL = 'http://localhost:8001';

const DocsPage: React.FC = () => {
  const [docsIndex, setDocsIndex] = useState<DocsIndex | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null);
  const [docContent, setDocContent] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [showSearchResults, setShowSearchResults] = useState(false);

  // Load docs index on component mount
  useEffect(() => {
    const loadDocsIndex = async () => {
      try {
        const response = await fetch(`${DOCS_API_BASE_URL}/api/docs`);
        if (!response.ok) {
          throw new Error('Failed to load documentation index');
        }
        const index = await response.json();
        setDocsIndex(index);
        
        // Auto-select first category and first doc
        const firstCategory = Object.keys(index.categories)[0];
        if (firstCategory && index.categories[firstCategory]?.docs.length > 0) {
          setSelectedCategory(firstCategory);
          setSelectedDoc(index.categories[firstCategory].docs[0].filename);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setIsLoading(false);
      }
    };

    loadDocsIndex();
  }, []);

  // Load doc content when selection changes
  useEffect(() => {
    if (selectedCategory && selectedDoc) {
      const loadDocContent = async () => {
        setIsLoading(true);
        setError(null);
        try {
          const response = await fetch(`${DOCS_API_BASE_URL}/api/docs/${selectedCategory}/${selectedDoc}`);
          if (!response.ok) {
            throw new Error('Failed to load document');
          }
          const data = await response.json();
          setDocContent(data.content);
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
          setIsLoading(false);
        }
      };

      loadDocContent();
    }
  }, [selectedCategory, selectedDoc]);

  // Handle search
  useEffect(() => {
    if (searchQuery.trim()) {
      const performSearch = async () => {
        try {
          const response = await fetch(`${DOCS_API_BASE_URL}/api/docs/search?query=${encodeURIComponent(searchQuery)}`);
          if (response.ok) {
            const data = await response.json();
            setSearchResults(data.results);
            setShowSearchResults(true);
          }
        } catch (err) {
          console.error('Search error:', err);
        }
      };

      const timeoutId = setTimeout(performSearch, 300);
      return () => clearTimeout(timeoutId);
    } else {
      setShowSearchResults(false);
      setSearchResults([]);
    }
  }, [searchQuery]);

  const handleCategorySelect = (category: string) => {
    setSelectedCategory(category);
    if (docsIndex && docsIndex.categories[category] && docsIndex.categories[category].docs.length > 0) {
      setSelectedDoc(docsIndex.categories[category].docs[0].filename);
    }
    setShowSearchResults(false);
  };

  const handleDocSelect = (category: string, doc: string) => {
    setSelectedCategory(category);
    setSelectedDoc(doc);
    setShowSearchResults(false);
  };

  const handleSearchResultClick = (result: SearchResult) => {
    setSelectedCategory(result.category);
    setSelectedDoc(result.filename);
    setShowSearchResults(false);
    setSearchQuery('');
  };

  return (
    <div className="h-full">
      <DocsLayout
        docsIndex={docsIndex}
        selectedCategory={selectedCategory}
        selectedDoc={selectedDoc}
        docContent={docContent}
        isLoading={isLoading}
        error={error}
        onCategorySelect={handleCategorySelect}
        onDocSelect={handleDocSelect}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />

      {/* Search Results Overlay */}
      {showSearchResults && searchResults.length > 0 && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-start justify-center pt-20">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-96 overflow-y-auto">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold">Search Results</h3>
              <p className="text-sm text-gray-500">
                {searchResults.length} result{searchResults.length !== 1 ? 's' : ''} found
              </p>
            </div>
            <div className="p-4 space-y-3">
              {searchResults.map((result, index) => (
                <button
                  key={index}
                  onClick={() => handleSearchResultClick(result)}
                  className="w-full text-left p-3 hover:bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="font-medium text-gray-900">{result.title}</div>
                  <div className="text-sm text-gray-600 mt-1">{result.category_name}</div>
                  <div className="text-sm text-gray-500 mt-2 line-clamp-2">
                    {result.snippet}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocsPage;
