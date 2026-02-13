import React from 'react';
import ReactMarkdown from 'react-markdown';
import { getDownloadUrl } from '../api';

interface ResultDisplayProps {
    contentId: string;
    originalContent: string;
    processedContent: string | null;
}

const ResultDisplay: React.FC<ResultDisplayProps> = ({ contentId, originalContent, processedContent }) => {
    const contentToShow = processedContent || originalContent;
    const isProcessed = !!processedContent;

    if (!contentId) return null;

    return (
        <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">3. Result Preview ({isProcessed ? 'Processed' : 'Original'})</h2>
                <div className="space-x-2">
                    <a
                        href={getDownloadUrl(contentId, 'original')}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                        Download Original
                    </a>
                    {isProcessed && (
                        <a
                            href={getDownloadUrl(contentId, 'processed')}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center px-3 py-2 border border-transparent shadow-sm text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        >
                            Download Processed
                        </a>
                    )}
                </div>
            </div>
            <div className="bg-gray-100 p-4 rounded-md overflow-auto max-h-[500px] text-sm prose max-w-none">
                <ReactMarkdown>{contentToShow.substring(0, 5000)}</ReactMarkdown>
                {contentToShow.length > 5000 && <p className="text-gray-500 italic mt-2">... (truncated for preview)</p>}
            </div>
        </div>
    );
};

export default ResultDisplay;
