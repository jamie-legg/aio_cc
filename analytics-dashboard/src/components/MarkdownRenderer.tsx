import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content, className = '' }) => {
  return (
    <div className={`prose prose-lg max-w-none dark:prose-invert ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={{
          // Custom styling for code blocks
          code: ({ node, className, children, ...props }) => {
            const match = /language-(\w+)/.exec(className || '');
            const isInline = !match;
            return !isInline ? (
              <pre className="bg-gray-900 border border-gray-700 rounded-xl p-6 overflow-x-auto shadow-lg">
                <code className={className} {...props}>
                  {children}
                </code>
              </pre>
            ) : (
              <code className="bg-gray-800 text-terminal-green px-2 py-1 rounded-md text-sm font-mono border border-gray-700">
                {children}
              </code>
            );
          },
          // Custom styling for headings
          h1: ({ children }) => (
            <h1 className="text-4xl font-bold text-white mb-8 mt-12 border-b-2 border-terminal-green pb-4 bg-gradient-to-r from-terminal-green to-terminal-blue bg-clip-text text-transparent">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-3xl font-semibold text-terminal-green mb-6 mt-10 flex items-center">
              <span className="w-2 h-8 bg-terminal-green mr-3 rounded-full"></span>
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-2xl font-semibold text-terminal-blue mb-4 mt-8 flex items-center">
              <span className="w-1.5 h-6 bg-terminal-blue mr-3 rounded-full"></span>
              {children}
            </h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-xl font-medium text-terminal-yellow mb-3 mt-6">
              {children}
            </h4>
          ),
          // Custom styling for paragraphs
          p: ({ children }) => (
            <p className="text-gray-300 mb-6 leading-relaxed text-lg">
              {children}
            </p>
          ),
          // Custom styling for lists
          ul: ({ children }) => (
            <ul className="list-none mb-6 text-gray-300 space-y-3">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="list-none mb-6 text-gray-300 space-y-3">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="flex items-start">
              <span className="w-2 h-2 bg-terminal-green rounded-full mt-2 mr-3 flex-shrink-0"></span>
              <span className="text-gray-300 leading-relaxed">{children}</span>
            </li>
          ),
          // Custom styling for blockquotes
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-terminal-blue pl-6 py-4 mb-6 bg-gray-800/50 text-gray-300 italic rounded-r-lg">
              <div className="flex items-start">
                <span className="text-terminal-blue text-2xl mr-3">"</span>
                <div>{children}</div>
              </div>
            </blockquote>
          ),
          // Custom styling for tables
          table: ({ children }) => (
            <div className="overflow-x-auto mb-8 rounded-xl border border-gray-700 shadow-lg">
              <table className="min-w-full bg-gray-900">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-gray-800">
              {children}
            </thead>
          ),
          th: ({ children }) => (
            <th className="px-6 py-4 text-left font-semibold text-terminal-green border-b border-gray-700">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-6 py-4 text-gray-300 border-b border-gray-800">
              {children}
            </td>
          ),
          // Custom styling for links
          a: ({ children, href }) => (
            <a 
              href={href} 
              className="text-terminal-blue hover:text-terminal-green underline decoration-terminal-blue hover:decoration-terminal-green transition-colors duration-200"
              target={href?.startsWith('http') ? '_blank' : undefined}
              rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
            >
              {children}
            </a>
          ),
          // Custom styling for horizontal rules
          hr: () => (
            <hr className="my-12 border-gray-700" />
          ),
          // Custom styling for strong/bold text
          strong: ({ children }) => (
            <strong className="text-terminal-yellow font-semibold">
              {children}
            </strong>
          ),
          // Custom styling for emphasis/italic text
          em: ({ children }) => (
            <em className="text-terminal-blue italic">
              {children}
            </em>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MarkdownRenderer;
