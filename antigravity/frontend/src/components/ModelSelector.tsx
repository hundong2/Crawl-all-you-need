import React from 'react';

interface ModelSelectorProps {
    provider: string;
    setProvider: (provider: string) => void;
    model: string;
    setModel: (model: string) => void;
    instruction: string;
    setInstruction: (instruction: string) => void;
    onProcess: () => void;
    isLoading: boolean;
    availableModels: Record<string, string[]>;
    canProcess: boolean;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({
    provider, setProvider, model, setModel, instruction, setInstruction, onProcess, isLoading, availableModels, canProcess
}) => {
    return (
        <div className={`bg-white p-6 rounded-lg shadow-md mb-6 ${!canProcess ? 'opacity-50 pointer-events-none' : ''}`}>
            <h2 className="text-xl font-bold mb-4">2. Process with LLM</h2>
            <div className="flex flex-col gap-4">
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Provider</label>
                        <select
                            value={provider}
                            onChange={(e) => {
                                setProvider(e.target.value);
                                setModel(availableModels[e.target.value]?.[0] || '');
                            }}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                        >
                            <option value="">Select Provider</option>
                            {Object.keys(availableModels).map((p) => (
                                <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700">Model</label>
                        <select
                            value={model}
                            onChange={(e) => setModel(e.target.value)}
                            disabled={!provider}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                        >
                            {availableModels[provider]?.map((m) => (
                                <option key={m} value={m}>{m}</option>
                            ))}
                        </select>
                    </div>
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700">Instruction/Prompt</label>
                    <textarea
                        value={instruction}
                        onChange={(e) => setInstruction(e.target.value)}
                        placeholder="e.g., Summarize this documentation into a single markdown file suitable for LLM context."
                        rows={3}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
                    />
                </div>
                <button
                    onClick={onProcess}
                    disabled={isLoading || !canProcess || !provider || !model}
                    className={`inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white ${isLoading ? 'bg-gray-400' : 'bg-green-600 hover:bg-green-700'} focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500`}
                >
                    {isLoading ? 'Processing...' : 'Process Content'}
                </button>
            </div>
        </div>
    );
};

export default ModelSelector;
