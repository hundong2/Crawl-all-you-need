import React from 'react';

interface CrawlerFormProps {
    url: string;
    setUrl: (url: string) => void;
    recursive: boolean;
    setRecursive: (recursive: boolean) => void;
    enhance: boolean;
    setEnhance: (enhance: boolean) => void;
    onSubmit: () => void;
    isLoading: boolean;
}

const CrawlerForm: React.FC<CrawlerFormProps> = ({ url, setUrl, recursive, setRecursive, enhance, setEnhance, onSubmit, isLoading }) => {
    return (
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
            <h2 className="text-xl font-bold mb-4">1. Crawl Documentation</h2>
            <div className="flex flex-col gap-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700">Site URL</label>
                    <input
                        type="url"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="https://example.com/docs"
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                    />
                </div>
                <div className="flex items-center">
                    <input
                        type="checkbox"
                        checked={recursive}
                        onChange={(e) => setRecursive(e.target.checked)}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 block text-sm text-gray-900">
                        Recursive Crawl (Depth limited)
                    </label>
                </div>
                <div className="flex items-center">
                    <input
                        type="checkbox"
                        checked={enhance}
                        onChange={(e) => setEnhance(e.target.checked)}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 block text-sm text-gray-900">
                        Enhance with AI (Design & Refactor using Gemini)
                    </label>
                </div>
                <button
                    onClick={onSubmit}
                    disabled={isLoading || !url}
                    className={`inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white ${isLoading ? 'bg-gray-400' : 'bg-indigo-600 hover:bg-indigo-700'} focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
                >
                    {isLoading ? 'Crawling...' : 'Start Crawling'}
                </button>
            </div>
        </div>
    );
};

export default CrawlerForm;
