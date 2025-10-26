import React from 'react';
import DocsSidebar from './DocsSidebar';
import MarkdownRenderer from './MarkdownRenderer';
import { DocumentationLoading } from './LoadingSpinner';
import { AlertCircle } from 'lucide-react';

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

interface DocsLayoutProps {
  docsIndex: DocsIndex | null;
  selectedCategory: string | null;
  selectedDoc: string | null;
  docContent: string | null;
  isLoading: boolean;
  error: string | null;
  onCategorySelect: (category: string) => void;
  onDocSelect: (category: string, doc: string) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

const DocsLayout: React.FC<DocsLayoutProps> = ({
  docsIndex,
  selectedCategory,
  selectedDoc,
  docContent,
  isLoading,
  error,
  onCategorySelect,
  onDocSelect,
  searchQuery,
  onSearchChange,
}) => {
  if (!docsIndex) {
    return <DocumentationLoading fullScreen />;
  }

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <DocsSidebar
        docsIndex={docsIndex}
        selectedCategory={selectedCategory}
        selectedDoc={selectedDoc}
        onCategorySelect={onCategorySelect}
        onDocSelect={onDocSelect}
        searchQuery={searchQuery}
        onSearchChange={onSearchChange}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {error ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-4" />
              <p className="text-red-600 mb-2">Error loading documentation</p>
              <p className="text-gray-500 text-sm">{error}</p>
            </div>
          </div>
        ) : isLoading ? (
          <DocumentationLoading />
        ) : docContent ? (
          <div className="flex-1 overflow-y-auto bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
            <div className="max-w-6xl mx-auto p-12">
              <div className="bg-gray-800/40 backdrop-blur-sm rounded-3xl p-12 border border-gray-700/50 shadow-2xl">
                <MarkdownRenderer content={docContent} />
              </div>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-terminal-green to-terminal-blue rounded-full flex items-center justify-center mx-auto mb-6 shadow-2xl">
                <span className="text-3xl">📚</span>
              </div>
              <h3 className="text-2xl font-bold text-white mb-4 bg-gradient-to-r from-terminal-green to-terminal-blue bg-clip-text text-transparent">
                Welcome to Documentation
              </h3>
              <p className="text-gray-300 max-w-md text-lg leading-relaxed">
                Select a category from the sidebar to start exploring our comprehensive documentation.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocsLayout;
