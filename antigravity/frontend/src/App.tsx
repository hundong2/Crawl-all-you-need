import { useState, useEffect } from 'react';
import { crawlSite, processContent, getModels } from './api';
import CrawlerForm from './components/CrawlerForm';
import ModelSelector from './components/ModelSelector';
import ResultDisplay from './components/ResultDisplay';

function App() {
  const [url, setUrl] = useState('');
  const [recursive, setRecursive] = useState(false);
  const [enhance, setEnhance] = useState(false);
  const [contentId, setContentId] = useState('');
  const [originalContent, setOriginalContent] = useState('');
  const [processedContent, setProcessedContent] = useState<string | null>(null);
  const [provider, setProvider] = useState('');
  const [model, setModel] = useState('');
  const [instruction, setInstruction] = useState('Summarize this documentation into a single markdown file suitable for LLM context.');

  const [availableModels, setAvailableModels] = useState<Record<string, string[]>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState('');

  useEffect(() => {
    getModels().then(setAvailableModels).catch(console.error);
  }, []);

  const handleCrawl = async () => {
    setIsLoading(true);
    setStatus(`Crawling${enhance ? ' & Enhancing' : ''}...`);
    try {
      const result = await crawlSite(url, recursive, 10, enhance);
      setContentId(result.id);
      setOriginalContent(result.content);
      setProcessedContent(null);
      setStatus('Crawling complete.');
    } catch (error) {
      console.error(error);
      setStatus('Error crawling site.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleProcess = async () => {
    setIsLoading(true);
    setStatus('Processing with LLM...');
    try {
      const result = await processContent(contentId, provider, model, instruction);
      setProcessedContent(result.content);
      setStatus('Processing complete.');
    } catch (error) {
      console.error(error);
      setStatus('Error processing content.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-extrabold text-gray-900 text-center mb-8">
          Documentation Crawler & Converter
        </h1>

        {status && (
          <div className={`mb-4 p-4 rounded-md ${status.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}`}>
            {status}
          </div>
        )}

        <CrawlerForm
          url={url}
          setUrl={setUrl}
          recursive={recursive}
          setRecursive={setRecursive}
          enhance={enhance}
          setEnhance={setEnhance}
          onSubmit={handleCrawl}
          isLoading={isLoading}
        />

        <ModelSelector
          provider={provider}
          setProvider={setProvider}
          model={model}
          setModel={setModel}
          instruction={instruction}
          setInstruction={setInstruction}
          onProcess={handleProcess}
          isLoading={isLoading}
          availableModels={availableModels}
          canProcess={!!contentId}
        />

        {(originalContent || processedContent) && (
          <ResultDisplay
            contentId={contentId}
            originalContent={originalContent}
            processedContent={processedContent}
          />
        )}
      </div>
    </div>
  );
}

export default App;
