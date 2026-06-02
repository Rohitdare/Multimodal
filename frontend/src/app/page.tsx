"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Upload,
  Search,
  History as HistoryIcon,
  Brain,
  FileJson,
  Eye,
  Terminal,
  Zap,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Trash2,
  X,
  Check,
  Star,
  Bookmark,
  ListTodo,
  HelpCircle,
  Tags,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ─── Types ───────────────────────────────────────────────────────────────────
interface HistoryItem {
  id: number;
  image_name: string;
  question: string;
  result: Record<string, unknown>;
  task_type: string;
  ocr_text: string;
  created_at: string;
}

interface AnalysisResult {
  task_type: string;
  ocr_text: string;
  output: {
    result?: Record<string, unknown>;
    error?: string;
    raw?: unknown;
  };
}

// ─── Utilities ───────────────────────────────────────────────────────────────
function cn(...classes: (string | boolean | undefined | null)[]) {
  return classes.filter(Boolean).join(" ");
}

// ─── Component ───────────────────────────────────────────────────────────────
export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [question, setQuestion] = useState(
    "Extract information from this image."
  );
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [activeTab, setActiveTab] = useState<"result" | "ocr">("result");
  const [clearingHistory, setClearingHistory] = useState(false);
  const [dragging, setDragging] = useState(false);

  // ── Fetch history ──────────────────────────────────────────────────────────
  const fetchHistory = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/history/`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setHistory(Array.isArray(data) ? data : []);
    } catch {
      setHistory([]);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  // ── File handling ──────────────────────────────────────────────────────────
  const applyFile = (f: File) => {
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setError(null);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) applyFile(e.target.files[0]);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped && dropped.type.startsWith("image/")) applyFile(dropped);
  };

  const clearFile = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
  };

  // ── Analysis ───────────────────────────────────────────────────────────────
  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setResult(null);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("question", question);

    try {
      const res = await fetch(`${API_BASE}/analyze/`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail ?? `HTTP ${res.status}`);
      }
      const data: AnalysisResult = await res.json();
      setResult(data);
      fetchHistory();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  // ── Clear history ──────────────────────────────────────────────────────────
  const handleClearHistory = async () => {
    setClearingHistory(true);
    try {
      await fetch(`${API_BASE}/history/`, { method: "DELETE" });
      setHistory([]);
    } finally {
      setClearingHistory(false);
    }
  };

  // ─────────────────────────────────────────────────────────────────────────
  return (
    <div className="flex h-screen w-full bg-[#0a0a0a] text-white overflow-hidden">
      {/* ── Sidebar ── */}
      <aside className="w-72 border-r border-white/5 bg-[#0d0d0d] flex flex-col shrink-0">
        {/* Logo */}
        <div className="p-5 border-b border-white/5 flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-lg shrink-0">
            <Zap className="w-4 h-4" />
          </div>
          <h1 className="text-lg font-bold tracking-tight">VisionAgent</h1>
        </div>

        {/* History list */}
        <div className="flex-1 overflow-y-auto p-3 space-y-3">
          <div className="flex items-center justify-between px-2 text-[10px] font-semibold text-zinc-500 uppercase tracking-widest">
            <span className="flex items-center gap-1.5">
              <HistoryIcon className="w-3 h-3" /> Recent Activity
            </span>
            {history.length > 0 && (
              <button
                onClick={handleClearHistory}
                disabled={clearingHistory}
                title="Clear history"
                className="text-zinc-600 hover:text-red-400 transition-colors"
              >
                {clearingHistory ? (
                  <Loader2 className="w-3 h-3 animate-spin" />
                ) : (
                  <Trash2 className="w-3 h-3" />
                )}
              </button>
            )}
          </div>

          {history.length === 0 ? (
            <div className="text-center py-10 text-zinc-600">
              <p className="text-xs">No history yet</p>
            </div>
          ) : (
            history.map((item) => (
              <div
                key={item.id}
                onClick={() => {
                  setQuestion(item.question);
                  setResult({
                    task_type: item.task_type || "general",
                    ocr_text: item.ocr_text || "",
                    output: {
                      result: item.result,
                    },
                  });
                  setActiveTab("result");
                }}
                className="p-3 rounded-xl hover:bg-white/5 border border-transparent hover:border-white/5 transition-all cursor-pointer"
              >
                <p className="text-xs font-medium truncate">{item.image_name}</p>
                <p className="text-[11px] text-zinc-500 truncate mt-0.5">
                  {item.question}
                </p>
                <p className="text-[10px] text-zinc-700 mt-1">
                  {new Date(item.created_at).toLocaleDateString()}
                </p>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* ── Main ── */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {/* Header */}
        <header className="h-14 border-b border-white/5 bg-black/20 backdrop-blur-xl flex items-center justify-between px-8 shrink-0">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse block" />
            <span className="text-sm text-zinc-400">System Ready</span>
          </div>
          <div className="flex items-center gap-3 text-sm text-zinc-500">
            <span className="px-2.5 py-1 rounded-full bg-white/5 text-xs">
              FastAPI + Next.js
            </span>
          </div>
        </header>

        {/* Workspace */}
        <div className="flex-1 overflow-y-auto p-8 space-y-8">
          <div className="max-w-5xl mx-auto w-full space-y-8">
            {/* Upload + Input */}
            <section className="grid grid-cols-1 lg:grid-cols-5 gap-6">
              {/* Drop Zone */}
              <div className="lg:col-span-3 space-y-4">
                <div
                  className={cn(
                    "relative group aspect-video rounded-3xl border-2 border-dashed transition-all flex flex-col items-center justify-center overflow-hidden bg-zinc-900/50",
                    dragging
                      ? "border-blue-500 bg-blue-500/5"
                      : preview
                      ? "border-blue-500/50 shadow-2xl shadow-blue-500/5"
                      : "border-white/10 hover:border-white/20"
                  )}
                  onDragOver={(e) => {
                    e.preventDefault();
                    setDragging(true);
                  }}
                  onDragLeave={() => setDragging(false)}
                  onDrop={handleDrop}
                >
                  {preview ? (
                    <>
                      <img
                        src={preview}
                        className="absolute inset-0 w-full h-full object-contain"
                        alt="Preview"
                      />
                      <button
                        onClick={clearFile}
                        className="absolute top-3 right-3 p-1.5 bg-black/60 hover:bg-black/80 rounded-full transition-colors z-10"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </>
                  ) : (
                    <>
                      <div className="p-4 rounded-2xl bg-white/5 mb-3 group-hover:scale-110 transition-transform">
                        <Upload className="w-7 h-7 text-zinc-400" />
                      </div>
                      <p className="text-zinc-400 text-sm font-medium">
                        Drop image here or{" "}
                        <span className="text-blue-500 underline cursor-pointer">
                          browse
                        </span>
                      </p>
                      <p className="text-zinc-600 text-xs mt-1">
                        JPG, PNG, WebP — up to 10 MB
                      </p>
                    </>
                  )}
                  <input
                    type="file"
                    className="absolute inset-0 opacity-0 cursor-pointer"
                    onChange={handleFileChange}
                    accept="image/jpeg,image/png,image/webp"
                  />
                </div>

                {/* Question + Analyze */}
                <div className="space-y-2">
                  <label className="text-xs font-semibold text-zinc-400 flex items-center gap-1.5 px-1">
                    <Terminal className="w-3.5 h-3.5" /> Question / Instruction
                  </label>
                  <div className="relative">
                    <textarea
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      className="w-full bg-zinc-900 border border-white/10 rounded-2xl p-4 pb-14 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all min-h-[110px] resize-none"
                      placeholder="Ask anything about the image…"
                    />
                    <button
                      onClick={handleAnalyze}
                      disabled={!file || loading}
                      className="absolute bottom-3 right-3 bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-800 disabled:text-zinc-600 text-white px-5 py-2 rounded-xl text-sm font-bold flex items-center gap-2 transition-all active:scale-95 shadow-lg shadow-blue-900/20"
                    >
                      {loading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Zap className="w-4 h-4" />
                      )}
                      Analyze
                    </button>
                  </div>
                </div>

                {/* Error banner */}
                {error && (
                  <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-sm text-red-400">
                    <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                    <span>{error}</span>
                  </div>
                )}
              </div>

              {/* Status panel */}
              <div className="lg:col-span-2">
                <div className="p-5 rounded-3xl bg-zinc-900/50 border border-white/5 space-y-4">
                  <h3 className="text-sm font-bold flex items-center gap-2">
                    <Brain className="w-4 h-4 text-blue-500" /> Intelligence Status
                  </h3>
                  <div className="space-y-2">
                    {[
                      { label: "OCR Engine", status: "Off", color: "text-red-500" },
                      { label: "Vector Memory", status: "Persistent", color: "text-blue-500" },
                      { label: "LLM (Groq)", status: "Primary", color: "text-indigo-400" },
                      { label: "Fallback", status: "OpenRouter", color: "text-yellow-500" },
                    ].map(({ label, status, color }) => (
                      <div
                        key={label}
                        className="flex items-center justify-between p-2.5 rounded-xl bg-white/5 border border-white/5"
                      >
                        <span className="text-xs text-zinc-400">{label}</span>
                        <span className={cn("text-[10px] font-bold uppercase", color)}>
                          {status}
                        </span>
                      </div>
                    ))}
                  </div>

                  {result && (
                    <div className="pt-2 border-t border-white/5">
                      <p className="text-[11px] text-zinc-500">
                        Last task:{" "}
                        <span className="text-blue-400 font-semibold capitalize">
                          {result.task_type}
                        </span>
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </section>

            {/* Results */}
            {result && (
              <section className="space-y-4 pb-20">
                {/* Tabs */}
                <div className="flex items-center gap-2 border-b border-white/5 pb-3">
                  {(["result", "ocr"] as const).map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={cn(
                        "px-4 py-1.5 rounded-lg text-sm font-bold transition-all",
                        activeTab === tab
                          ? "bg-white text-black"
                          : "text-zinc-500 hover:text-white"
                      )}
                    >
                      {tab === "result" ? "Structured Result" : "Raw OCR"}
                    </button>
                  ))}
                </div>

                {/* Structured result */}
                {activeTab === "result" && (() => {
                  const data = (result.output?.result ?? result.output?.raw ?? result.output) as Record<string, any> | null;
                  const hasError = !!result.output?.error;
                  
                  const renderVisualizer = () => {
                    if (!data || typeof data !== "object") return null;

                    switch (result.task_type) {
                      case "receipt":
                        return (
                          <div className="space-y-4">
                            <div className="flex items-center justify-between p-4 bg-blue-500/10 border border-blue-500/20 rounded-2xl">
                              <div>
                                <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">Store</p>
                                <h5 className="text-lg font-bold text-white">{data.store || "Unknown Store"}</h5>
                              </div>
                              <div className="text-right">
                                <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">Total Spent</p>
                                <span className="text-2xl font-black text-blue-400 font-mono">
                                  ${typeof data.total_spent === 'number' ? data.total_spent.toFixed(2) : data.total_spent || '0.00'}
                                </span>
                              </div>
                            </div>

                            {data.largest_category && (
                              <div className="p-3 bg-zinc-900/80 border border-white/5 rounded-xl flex items-center justify-between">
                                <span className="text-xs text-zinc-400">Largest Category:</span>
                                <span className="text-xs font-bold text-zinc-200 capitalize bg-white/5 px-2.5 py-1 rounded-full border border-white/5">
                                  {data.largest_category}
                                </span>
                              </div>
                            )}

                            {data.expensive_items && Array.isArray(data.expensive_items) && data.expensive_items.length > 0 && (
                              <div className="space-y-2">
                                <p className="text-xs font-bold text-zinc-400 flex items-center gap-1.5 px-1">
                                  <Tags className="w-3.5 h-3.5 text-blue-400" /> Expensive Items
                                </p>
                                <div className="flex flex-wrap gap-2">
                                  {data.expensive_items.map((item: string, idx: number) => (
                                    <span key={idx} className="text-xs font-medium bg-red-500/10 text-red-400 px-3 py-1.5 rounded-xl border border-red-500/20">
                                      {item}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}

                            {data.verdict && (
                              <div className="p-4 bg-indigo-500/5 border border-indigo-500/15 rounded-2xl space-y-1">
                                <span className="text-[10px] text-indigo-400 uppercase tracking-wider font-bold">Verdict / Insights</span>
                                <p className="text-xs text-zinc-300 leading-relaxed font-medium">{data.verdict}</p>
                              </div>
                            )}
                          </div>
                        );

                      case "product":
                        const scoreVal = typeof data.score === 'number' ? data.score : parseInt(data.score) || 0;
                        const isBuy = data.buy === true || String(data.buy).toLowerCase() === 'true';
                        return (
                          <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                              <div className="p-4 bg-zinc-900/80 border border-white/5 rounded-2xl flex flex-col justify-between">
                                <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">Recommendation</span>
                                <div className="mt-2 flex items-center gap-2">
                                  {isBuy ? (
                                    <div className="bg-green-500/10 text-green-400 border border-green-500/20 px-3 py-1 rounded-xl text-xs font-black flex items-center gap-1">
                                      <Check className="w-3.5 h-3.5" /> BUY
                                    </div>
                                  ) : (
                                    <div className="bg-red-500/10 text-red-400 border border-red-500/20 px-3 py-1 rounded-xl text-xs font-black flex items-center gap-1">
                                      <X className="w-3.5 h-3.5" /> AVOID
                                    </div>
                                  )}
                                </div>
                              </div>

                              <div className="p-4 bg-zinc-900/80 border border-white/5 rounded-2xl flex flex-col justify-between">
                                <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">Product Score</span>
                                <div className="mt-2 flex items-center gap-2">
                                  <div className="flex items-center text-yellow-400 gap-0.5">
                                    <Star className="w-4 h-4 fill-current" />
                                    <span className="text-lg font-black font-mono">{scoreVal}/10</span>
                                  </div>
                                </div>
                              </div>
                            </div>

                            <div className="space-y-1">
                              <div className="flex justify-between text-[10px] text-zinc-500 font-bold uppercase px-1">
                                <span>Quality Score</span>
                                <span>{scoreVal * 10}%</span>
                              </div>
                              <div className="w-full bg-zinc-950 border border-white/5 rounded-full h-2.5 overflow-hidden">
                                <div 
                                  className="bg-gradient-to-r from-blue-500 to-indigo-500 h-full rounded-full transition-all duration-500"
                                  style={{ width: `${Math.min(100, Math.max(0, scoreVal * 10))}%` }}
                                />
                              </div>
                            </div>

                            {data.best_for && (
                              <div className="p-3 bg-zinc-900/80 border border-white/5 rounded-xl flex items-center justify-between">
                                <span className="text-xs text-zinc-400">Best For:</span>
                                <span className="text-xs font-bold text-blue-400 bg-blue-500/5 px-2.5 py-1 rounded-full border border-blue-500/10">
                                  {data.best_for}
                                </span>
                              </div>
                            )}

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {data.pros && Array.isArray(data.pros) && data.pros.length > 0 && (
                                <div className="p-3 bg-green-500/5 border border-green-500/10 rounded-2xl space-y-2">
                                  <span className="text-[10px] text-green-400 uppercase tracking-wider font-bold">Pros</span>
                                  <ul className="space-y-1.5">
                                    {data.pros.map((p: string, idx: number) => (
                                      <li key={idx} className="text-xs text-zinc-300 flex items-start gap-1.5">
                                        <span className="text-green-400 font-bold shrink-0 mt-0.5">✓</span>
                                        <span>{p}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}

                              {data.cons && Array.isArray(data.cons) && data.cons.length > 0 && (
                                <div className="p-3 bg-red-500/5 border border-red-500/10 rounded-2xl space-y-2">
                                  <span className="text-[10px] text-red-400 uppercase tracking-wider font-bold">Cons</span>
                                  <ul className="space-y-1.5">
                                    {data.cons.map((c: string, idx: number) => (
                                      <li key={idx} className="text-xs text-zinc-300 flex items-start gap-1.5">
                                        <span className="text-red-400 font-bold shrink-0 mt-0.5">✕</span>
                                        <span>{c}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>

                            {data.verdict && (
                              <div className="p-4 bg-zinc-900/80 border border-white/5 rounded-2xl space-y-1">
                                <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-bold">Detailed Verdict</span>
                                <p className="text-xs text-zinc-300 leading-relaxed font-medium">{data.verdict}</p>
                              </div>
                            )}
                          </div>
                        );

                      case "notes":
                        return (
                          <div className="space-y-4">
                            {data.topic && (
                              <div className="p-4 bg-zinc-900/80 border border-white/5 rounded-2xl flex items-center gap-3">
                                <Bookmark className="w-5 h-5 text-indigo-400" />
                                <div>
                                  <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">Topic</p>
                                  <h5 className="text-sm font-bold text-white">{data.topic}</h5>
                                </div>
                              </div>
                            )}

                            {data.key_points && Array.isArray(data.key_points) && data.key_points.length > 0 && (
                              <div className="p-4 bg-zinc-900/50 border border-white/5 rounded-2xl space-y-2">
                                <span className="text-[10px] text-indigo-400 uppercase tracking-wider font-bold flex items-center gap-1">
                                  <CheckCircle2 className="w-3.5 h-3.5" /> Key Points
                                </span>
                                <ul className="space-y-2">
                                  {data.key_points.map((pt: string, idx: number) => (
                                    <li key={idx} className="text-xs text-zinc-300 flex items-start gap-2">
                                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 shrink-0 mt-1.5" />
                                      <span>{pt}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {data.action_items && Array.isArray(data.action_items) && data.action_items.length > 0 && (
                              <div className="p-4 bg-green-500/5 border border-green-500/10 rounded-2xl space-y-2">
                                <span className="text-[10px] text-green-400 uppercase tracking-wider font-bold flex items-center gap-1">
                                  <ListTodo className="w-3.5 h-3.5" /> Action Items
                                </span>
                                <ul className="space-y-2">
                                  {data.action_items.map((act: string, idx: number) => (
                                    <li key={idx} className="text-xs text-zinc-300 flex items-start gap-2 bg-black/20 p-2.5 rounded-xl border border-white/5">
                                      <input type="checkbox" readOnly checked className="mt-0.5 border-white/20 accent-green-500 rounded" />
                                      <span>{act}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {data.open_questions && Array.isArray(data.open_questions) && data.open_questions.length > 0 && (
                              <div className="p-4 bg-amber-500/5 border border-amber-500/10 rounded-2xl space-y-2">
                                <span className="text-[10px] text-amber-400 uppercase tracking-wider font-bold flex items-center gap-1">
                                  <HelpCircle className="w-3.5 h-3.5" /> Open Questions
                                </span>
                                <ul className="space-y-2">
                                  {data.open_questions.map((q: string, idx: number) => (
                                    <li key={idx} className="text-xs text-zinc-300 flex items-start gap-2 italic">
                                      <span className="text-amber-400 font-bold">?</span>
                                      <span>{q}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        );

                      case "documents":
                        return (
                          <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                              <div className="p-4 bg-zinc-900/80 border border-white/5 rounded-2xl">
                                <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">Document Type</span>
                                <h5 className="text-xs font-bold text-white capitalize mt-1">{data.document_type || "General Document"}</h5>
                              </div>
                              <div className="p-4 bg-zinc-900/80 border border-white/5 rounded-2xl">
                                <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">Main Subject</span>
                                <h5 className="text-xs font-bold text-white truncate mt-1">{data.subject || "Not Specified"}</h5>
                              </div>
                            </div>

                            {data.summary && (
                              <div className="p-4 bg-zinc-900/50 border border-white/5 rounded-2xl space-y-1">
                                <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-bold">Document Summary</span>
                                <p className="text-xs text-zinc-300 leading-relaxed font-medium">{data.summary}</p>
                              </div>
                            )}

                            {data.entities && Array.isArray(data.entities) && data.entities.length > 0 && (
                              <div className="p-4 bg-zinc-900/80 border border-white/5 rounded-2xl space-y-3">
                                <span className="text-[10px] text-blue-400 uppercase tracking-wider font-bold flex items-center gap-1">
                                  <Tags className="w-3.5 h-3.5" /> Extracted Entities
                                </span>
                                <div className="grid grid-cols-1 gap-2">
                                  {data.entities.map((ent: any, idx: number) => {
                                    if (!ent || typeof ent !== 'object') return null;
                                    const entityType = ent.type || "unknown";
                                    let badgeColor = "bg-zinc-800 text-zinc-400 border-zinc-700/50";
                                    if (entityType.match(/person|reviewer|user|contributor/i)) badgeColor = "bg-blue-500/10 text-blue-400 border-blue-500/20";
                                    else if (entityType.match(/company|org/i)) badgeColor = "bg-purple-500/10 text-purple-400 border-purple-500/20";
                                    else if (entityType.match(/file|doc/i)) badgeColor = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
                                    else if (entityType.match(/date|time/i)) badgeColor = "bg-amber-500/10 text-amber-400 border-amber-500/20";

                                    return (
                                      <div key={idx} className="flex items-center justify-between p-2.5 bg-black/20 rounded-xl border border-white/5">
                                        <span className="text-xs font-bold text-white">{ent.name || ent.value || ent.entity || ""}</span>
                                        <div className="flex items-center gap-2">
                                          <span className={`text-[10px] px-2 py-0.5 rounded-full border ${badgeColor} capitalize`}>
                                            {entityType}
                                          </span>
                                          {ent.confidence !== undefined && ent.confidence !== null && (
                                            <span className="text-[10px] font-mono text-zinc-500">
                                              {Math.round(ent.confidence * 100)}%
                                            </span>
                                          )}
                                        </div>
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                            )}
                          </div>
                        );

                      case "screenshots":
                        return (
                          <div className="space-y-4">
                            {data.application && (
                              <div className="p-4 bg-zinc-900/80 border border-white/5 rounded-2xl">
                                <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">Application / Website</span>
                                <h5 className="text-sm font-bold text-white mt-1">{data.application}</h5>
                              </div>
                            )}

                            {data.context && (
                              <div className="p-4 bg-zinc-900/50 border border-white/5 rounded-2xl space-y-1">
                                <span className="text-[10px] text-indigo-400 uppercase tracking-wider font-bold">Screenshot Context</span>
                                <p className="text-xs text-zinc-300 leading-relaxed font-medium">{data.context}</p>
                              </div>
                            )}

                            {data.ui_elements && Array.isArray(data.ui_elements) && data.ui_elements.length > 0 && (
                              <div className="space-y-2">
                                <p className="text-xs font-bold text-zinc-400 flex items-center gap-1.5 px-1">
                                  <Terminal className="w-3.5 h-3.5 text-zinc-400" /> UI Elements Detected
                                </p>
                                <div className="flex flex-wrap gap-2">
                                  {data.ui_elements.map((el: string, idx: number) => (
                                    <span key={idx} className="text-xs font-semibold bg-white/5 text-zinc-300 px-3 py-1.5 rounded-xl border border-white/5">
                                      {el}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}

                            {data.text_content && (
                              <div className="p-4 bg-black/40 border border-white/5 rounded-2xl space-y-1.5">
                                <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-bold">Key Text Content</span>
                                <p className="text-xs text-zinc-400 leading-relaxed max-h-[150px] overflow-y-auto font-mono whitespace-pre-wrap">
                                  {data.text_content}
                                </p>
                              </div>
                            )}
                          </div>
                        );

                      default:
                        return (
                          <div className="bg-zinc-900/50 border border-white/5 rounded-2xl p-4 space-y-3">
                            <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-bold">Properties</span>
                            <div className="space-y-2">
                              {Object.entries(data).map(([key, val]) => {
                                if (key === "error" || key === "raw") return null;
                                return (
                                  <div key={key} className="flex flex-col gap-1 p-2.5 bg-black/20 rounded-xl border border-white/5">
                                    <span className="text-[10px] text-zinc-500 capitalize font-bold">{key.replace(/_/g, " ")}</span>
                                    <span className="text-xs text-zinc-200">
                                      {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                                    </span>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        );
                    }
                  };

                  return (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
                      <div className="bg-zinc-900/50 border border-blue-500/20 p-5 rounded-3xl flex flex-col">
                        <div className="flex items-center justify-between mb-3 shrink-0">
                          <h4 className="text-xs font-bold text-blue-400 flex items-center gap-2 uppercase tracking-widest">
                            <FileJson className="w-3.5 h-3.5" /> JSON Output
                          </h4>
                          <CheckCircle2 className="w-4 h-4 text-green-500" />
                        </div>
                        <pre className="text-xs bg-black/40 p-4 rounded-xl overflow-x-auto text-blue-100/80 font-mono leading-relaxed max-h-[500px] overflow-y-auto flex-1">
                          {JSON.stringify(data, null, 2)}
                        </pre>
                      </div>

                      <div className="space-y-6">
                        <div className="bg-zinc-900 border border-white/5 p-5 rounded-3xl space-y-4">
                          <div className="flex items-center justify-between">
                            <h4 className="text-xs font-bold text-zinc-500 uppercase tracking-widest">
                              Analysis Summary
                            </h4>
                            <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-blue-600/10 text-blue-400 border border-blue-500/20 capitalize font-bold">
                              {result.task_type}
                            </span>
                          </div>
                          
                          {renderVisualizer()}

                          {hasError && (
                            <div className="flex items-start gap-2 text-xs text-red-400 bg-red-500/10 p-3 rounded-xl border border-red-500/20">
                              <AlertCircle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                              <div className="space-y-1">
                                <p className="font-bold">Validation Warning</p>
                                <p className="text-[11px] leading-relaxed">{result.output.error}</p>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })()}

                {/* OCR tab */}
                {activeTab === "ocr" && (
                  <div className="bg-zinc-900/50 border border-white/5 p-5 rounded-3xl">
                    <h4 className="text-xs font-bold text-zinc-500 mb-3 uppercase tracking-widest flex items-center gap-2">
                      <Eye className="w-3.5 h-3.5" /> Extracted OCR Text
                    </h4>
                    <div className="bg-black/40 p-5 rounded-xl text-sm font-mono text-zinc-300 whitespace-pre-wrap leading-relaxed max-h-[500px] overflow-y-auto">
                      {result.ocr_text || (
                        <span className="text-zinc-600 italic">
                          No text extracted from this image.
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </section>
            )}
          </div>
        </div>

        {/* Footer gradient */}
        <div className="absolute bottom-0 left-0 right-0 h-48 bg-gradient-to-t from-blue-600/5 to-transparent pointer-events-none" />
      </main>
    </div>
  );
}
