
import React, { useState } from 'react';
import { GraphState } from '../types';
import { Copy, Check } from 'lucide-react';

interface StateViewerProps {
    state: GraphState | null;
}

const StateViewer: React.FC<StateViewerProps> = ({ state }) => {
    const [copied, setCopied] = useState(false);
    const [filterMode, setFilterMode] = useState<'all' | 'extracted'>('all');

    const handleCopy = () => {
        if (state) {
            navigator.clipboard.writeText(JSON.stringify(state, null, 2));
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const getDisplayState = () => {
        if (!state) return null;
        if (filterMode === 'extracted') {
            return state.extraction || {};
        }
        return state;
    };

    return (
        <div className="flex flex-col h-full bg-slate-900 rounded-lg overflow-hidden text-slate-200 font-mono text-sm border border-slate-700 shadow-inner">
            <div className="flex items-center justify-between px-4 py-2 bg-slate-800 border-b border-slate-700">
                <span className="font-bold text-slate-400">STATE VIEWER</span>

                <div className="flex gap-2">
                    <div className="flex bg-slate-700 rounded p-0.5">
                        <button
                            onClick={() => setFilterMode('all')}
                            className={`px-2 py-0.5 text-xs rounded ${filterMode === 'all' ? 'bg-slate-500 text-white' : 'text-slate-400 hover:text-white'}`}
                        >
                            All
                        </button>
                        <button
                            onClick={() => setFilterMode('extracted')}
                            className={`px-2 py-0.5 text-xs rounded ${filterMode === 'extracted' ? 'bg-slate-500 text-white' : 'text-slate-400 hover:text-white'}`}
                        >
                            Extracted
                        </button>
                    </div>

                    <button
                        onClick={handleCopy}
                        className="p-1 hover:bg-slate-600 rounded text-slate-400 hover:text-white transition-colors"
                        title="Copy to clipboard"
                    >
                        {copied ? <Check size={14} /> : <Copy size={14} />}
                    </button>
                </div>
            </div>

            <div className="flex-1 overflow-auto p-4 custom-scrollbar">
                {state ? (
                    <pre className="text-xs leading-relaxed">
                        {JSON.stringify(getDisplayState(), null, 2)}
                    </pre>
                ) : (
                    <div className="h-full flex items-center justify-center text-slate-600 italic">
                        Waiting for session data...
                    </div>
                )}
            </div>
        </div>
    );
};

export default StateViewer;
