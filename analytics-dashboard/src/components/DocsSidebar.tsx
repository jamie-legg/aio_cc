import React, { useState } from 'react';
import { ChevronDown, ChevronRight, FileText, Search } from 'lucide-react';

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

interface DocsSidebarProps {
  docsIndex: DocsIndex;
  selectedCategory: string | null;
  selectedDoc: string | null;
  onCategorySelect: (category: string) => void;
  onDocSelect: (category: string, doc: string) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

const DocsSidebar: React.FC<DocsSidebarProps> = ({
  docsIndex,
  selectedCategory,
  selectedDoc,
  onCategorySelect,
  onDocSelect,
  searchQuery,
  onSearchChange,
}) => {
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set([selectedCategory || 'getting-started'])
  );

  const toggleCategory = (categoryKey: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(categoryKey)) {
      newExpanded.delete(categoryKey);
    } else {
      newExpanded.add(categoryKey);
    }
    setExpandedCategories(newExpanded);
  };

  const filteredCategories = Object.entries(docsIndex.categories).filter(([_, category]) => {
    if (!searchQuery) return true;
    return category.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
           category.docs.some(doc => 
             doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
             doc.description.toLowerCase().includes(searchQuery.toLowerCase())
           );
  });

  return (
    <div className="w-80 bg-gray-900/95 backdrop-blur-sm border-r border-gray-700/50 flex flex-col h-full shadow-2xl">
      {/* Search */}
      <div className="p-6 border-b border-gray-700/50">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-terminal-green w-5 h-5" />
          <input
            type="text"
            placeholder="Search documentation..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-gray-800/50 border border-gray-700/50 rounded-xl focus:ring-2 focus:ring-terminal-green focus:border-terminal-green focus:bg-gray-800 text-white placeholder-gray-400 transition-all duration-200"
          />
        </div>
      </div>

      {/* Categories */}
      <div className="flex-1 overflow-y-auto">
        <nav className="p-6">
          {filteredCategories.map(([categoryKey, category]) => {
            const isExpanded = expandedCategories.has(categoryKey);
            const isSelected = selectedCategory === categoryKey;

            return (
              <div key={categoryKey} className="mb-2">
                <button
                  onClick={() => {
                    toggleCategory(categoryKey);
                    if (!isExpanded) {
                      onCategorySelect(categoryKey);
                    }
                  }}
                  className={`w-full flex items-center justify-between p-4 rounded-xl text-left transition-all duration-200 ${
                    isSelected 
                      ? 'bg-terminal-green/20 text-terminal-green border border-terminal-green/30 shadow-lg' 
                      : 'hover:bg-gray-800/50 text-gray-300 hover:text-white border border-transparent hover:border-gray-700/50'
                  }`}
                >
                  <div className="flex items-center">
                    {isExpanded ? (
                      <ChevronDown className="w-5 h-5 mr-3 text-terminal-green" />
                    ) : (
                      <ChevronRight className="w-5 h-5 mr-3 text-gray-400" />
                    )}
                    <span className="font-semibold text-lg">{category.name}</span>
                  </div>
                </button>

                {isExpanded && (
                  <div className="ml-8 mt-3 space-y-2">
                    {category.docs.map((doc) => {
                      const isDocSelected = selectedCategory === categoryKey && selectedDoc === doc.filename;
                      return (
                        <button
                          key={doc.filename}
                          onClick={() => onDocSelect(categoryKey, doc.filename)}
                          className={`w-full flex items-start p-3 rounded-xl text-left transition-all duration-200 ${
                            isDocSelected
                              ? 'bg-terminal-blue/20 text-terminal-blue border border-terminal-blue/30 shadow-md'
                              : 'hover:bg-gray-800/50 text-gray-400 hover:text-white border border-transparent hover:border-gray-700/30'
                          }`}
                        >
                          <FileText className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0 text-terminal-green" />
                          <div className="min-w-0">
                            <div className="font-semibold text-sm">{doc.title}</div>
                            <div className="text-xs text-gray-400 mt-1 line-clamp-2">
                              {doc.description}
                            </div>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </nav>
      </div>
    </div>
  );
};

export default DocsSidebar;
