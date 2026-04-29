import React, { useState } from 'react';
import { ShieldAlert, ShieldCheck, Activity, BrainCircuit, AlertCircle, Loader2 } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface EvaluationResult {
  hallucination_detected?: boolean;
  error_type?: string | null;
  reasoning?: string;
  error?: string;
}

function App() {
  const [context, setContext] = useState('');
  const [answer, setAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [connError, setConnError] = useState<string | null>(null);

  const handleEvaluate = async () => {
    if (!context.trim() || !answer.trim()) return;
    
    setIsLoading(true);
    setResult(null);
    setConnError(null);

    try {
      const response = await fetch('http://localhost:8000/evaluate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer sk-adv-rag-eval-enterprise-777'
        },
        body: JSON.stringify({ context, answer }),
      });

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error("Access Denied: Invalid API Key");
        }
        throw new Error(`Server returned status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setConnError(error instanceof Error ? error.message : 'Failed to connect to backend.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-50 font-sans p-6 md:p-12">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex items-center space-x-4 border-b border-zinc-800 pb-6">
          <div className="p-3 bg-zinc-900 rounded-xl border border-zinc-700 shadow-inner">
            <BrainCircuit className="w-8 h-8 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">Adv-RAG-Eval Cloud Engine</h1>
            <p className="text-zinc-400 text-sm mt-1">Enterprise Phase 3B - Automated Hallucination Detection</p>
          </div>
        </header>

        {/* Connection Error Toast */}
        {connError && (
          <div className="bg-red-950/50 border border-red-900 text-red-400 p-4 rounded-xl flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-medium">Connection Error</h3>
              <p className="text-sm mt-1 text-red-400/80">{connError}</p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Cards */}
          <div className="space-y-6">
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 shadow-xl transition-all focus-within:border-indigo-500/50 focus-within:ring-1 focus-within:ring-indigo-500/50">
              <label htmlFor="context" className="block text-sm font-medium text-zinc-300 mb-2">Ground Truth Context</label>
              <textarea
                id="context"
                className="w-full bg-zinc-950/50 border border-zinc-800 rounded-xl p-4 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 resize-none transition-all h-48"
                placeholder="Enter the factual reference text..."
                value={context}
                onChange={(e) => setContext(e.target.value)}
              />
            </div>

            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-5 shadow-xl transition-all focus-within:border-indigo-500/50 focus-within:ring-1 focus-within:ring-indigo-500/50">
              <label htmlFor="answer" className="block text-sm font-medium text-zinc-300 mb-2">LLM Generated Answer</label>
              <textarea
                id="answer"
                className="w-full bg-zinc-950/50 border border-zinc-800 rounded-xl p-4 text-sm text-zinc-100 placeholder-zinc-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 resize-none transition-all h-48"
                placeholder="Enter the LLM's response to evaluate..."
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
              />
            </div>

            <button
              onClick={handleEvaluate}
              disabled={isLoading || !context.trim() || !answer.trim()}
              className={cn(
                "w-full py-4 px-6 rounded-xl font-semibold flex items-center justify-center space-x-2 transition-all duration-300 relative overflow-hidden group",
                (isLoading || !context.trim() || !answer.trim()) 
                  ? "bg-zinc-800 text-zinc-500 cursor-not-allowed" 
                  : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-[0_0_20px_rgba(79,70,229,0.3)] hover:shadow-[0_0_25px_rgba(79,70,229,0.5)]"
              )}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Evaluating...</span>
                </>
              ) : (
                <>
                  <Activity className="w-5 h-5 group-hover:scale-110 transition-transform" />
                  <span>Run Evaluation</span>
                </>
              )}
              {/* Glowing overlay */}
              {!isLoading && context.trim() && answer.trim() && (
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]" />
              )}
            </button>
          </div>

          {/* Results Card */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 shadow-xl h-full flex flex-col relative overflow-hidden">
            {/* Background ambient glow based on result */}
            {result && (
              <div className={cn(
                "absolute -top-24 -right-24 w-64 h-64 rounded-full blur-[100px] opacity-20 pointer-events-none transition-colors duration-1000",
                result.error ? "bg-red-500" :
                result.hallucination_detected ? "bg-rose-500" : "bg-emerald-500"
              )} />
            )}
            
            <h2 className="text-lg font-semibold text-white mb-6 flex items-center justify-between border-b border-zinc-800 pb-4 relative z-10">
              Evaluation Results
              {result && !result.error && (
                <span className={cn(
                  "px-3 py-1 text-xs rounded-full font-medium flex items-center space-x-1",
                  result.hallucination_detected 
                    ? "bg-rose-500/10 text-rose-400 border border-rose-500/20" 
                    : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                )}>
                  {result.hallucination_detected ? (
                    <><ShieldAlert className="w-3 h-3 mr-1" /> Hallucination Detected</>
                  ) : (
                    <><ShieldCheck className="w-3 h-3 mr-1" /> Clean</>
                  )}
                </span>
              )}
            </h2>

            <div className="flex-1 flex flex-col justify-center relative z-10">
              {!result && !isLoading && (
                <div className="text-center text-zinc-500 space-y-4">
                  <div className="w-16 h-16 rounded-full bg-zinc-800/50 flex items-center justify-center mx-auto mb-4 border border-zinc-800">
                    <Activity className="w-6 h-6 text-zinc-600" />
                  </div>
                  <p>Awaiting inputs for evaluation.</p>
                </div>
              )}

              {isLoading && (
                <div className="text-center space-y-4 text-indigo-400 animate-pulse">
                  <div className="w-16 h-16 rounded-full bg-indigo-500/10 flex items-center justify-center mx-auto mb-4 border border-indigo-500/20">
                    <BrainCircuit className="w-6 h-6 animate-bounce" />
                  </div>
                  <p className="font-medium text-indigo-300">Analyzing semantic fidelity...</p>
                  <p className="text-xs text-zinc-500">Processing via adv-rag-judge model</p>
                </div>
              )}

              {result && (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                  {result.error ? (
                    <div className="p-4 bg-red-950/30 border border-red-900/50 rounded-xl text-red-400">
                      <p className="font-medium mb-1">Execution Error</p>
                      <p className="text-sm opacity-80">{result.error}</p>
                    </div>
                  ) : (
                    <>
                      <div className={cn(
                        "p-5 rounded-xl border transition-colors",
                        result.hallucination_detected 
                          ? "bg-rose-950/20 border-rose-900/50" 
                          : "bg-emerald-950/20 border-emerald-900/50"
                      )}>
                        <h3 className={cn(
                          "text-sm font-medium mb-2",
                          result.hallucination_detected ? "text-rose-400" : "text-emerald-400"
                        )}>
                          Reasoning
                        </h3>
                        <p className="text-zinc-300 text-sm leading-relaxed">
                          {result.reasoning || "No reasoning provided."}
                        </p>
                      </div>
                      
                      {result.hallucination_detected && result.error_type && (
                        <div className="p-4 bg-zinc-950/50 border border-zinc-800 rounded-xl">
                          <h3 className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-1">Error Classification</h3>
                          <p className="text-rose-300 font-medium">{result.error_type}</p>
                        </div>
                      )}
                      
                      <div className="mt-8 pt-4 border-t border-zinc-800">
                        <h3 className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-3">Raw JSON Response</h3>
                        <pre className="text-xs bg-zinc-950 p-4 rounded-xl text-zinc-400 overflow-x-auto border border-zinc-800/50 shadow-inner">
                          {JSON.stringify(result, null, 2)}
                        </pre>
                      </div>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
