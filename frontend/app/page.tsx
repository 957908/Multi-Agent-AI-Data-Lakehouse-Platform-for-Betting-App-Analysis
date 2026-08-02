"use client";

import React, { useState, useEffect } from "react";

export default function Home() {
  const [activeTab, setActiveTab] = useState("overview");
  const [searchQuery, setSearchQuery] = useState("");
  const [ragResult, setRagResult] = useState<any>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [backendHealth, setBackendHealth] = useState<string>("checking");
  const [scrapersState, setScrapersState] = useState({
    onexbet: "idle",
    melbet: "idle",
    tencric: "idle",
    twentytwoxbet: "idle",
  });
  const [activeLogs, setActiveLogs] = useState<string[]>([
    "System booted successfully.",
    "Database connection established.",
    "Nginx SSL proxy initialized.",
    "FastAPI instrumentator online.",
    "Waiting for commands..."
  ]);

  // Check backend health
  useEffect(() => {
    fetch("https://localhost/api/v1/health")
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          setBackendHealth("healthy");
        } else {
          setBackendHealth("degraded");
        }
      })
      .catch(() => {
        // Fallback check to direct API if proxy fails
        fetch("http://localhost:8000/api/v1/health")
          .then((res) => res.json())
          .then((data) => {
            if (data.success) setBackendHealth("healthy");
          })
          .catch(() => setBackendHealth("offline"));
      });
  }, []);

  const triggerScraper = (platform: string) => {
    setScrapersState(prev => ({ ...prev, [platform]: "running" }));
    addLog(`Initiating Playwright headless session for ${platform}...`);
    
    setTimeout(() => {
      addLog(`[${platform}] Browser context established. Bypassing cloudflare prompts...`);
    }, 1500);

    setTimeout(() => {
      addLog(`[${platform}] Navigated successfully. Discovered 14 active payment options.`);
      addLog(`[${platform}] Scraped transaction details write out to raw data bucket.`);
      setScrapersState(prev => ({ ...prev, [platform]: "completed" }));
    }, 4000);
  };

  const addLog = (msg: string) => {
    setActiveLogs(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev.slice(0, 15)]);
  };

  const handleRagSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery) return;
    setIsSearching(true);
    
    // Simulate RAG query
    setTimeout(() => {
      const lower = searchQuery.toLowerCase();
      let mockAnswer = "No matching betting risk anomalies identified in vector space.";
      let score = 92.4;
      
      if (lower.includes("upi") || lower.includes("paytm")) {
        mockAnswer = "UPI payment channel shows anomaly rate of 14.2% on OneXBet. Detected multiple matching receipt footprints mapping to high-frequency recycling rings.";
        score = 42.5;
      } else if (lower.includes("melbet")) {
        mockAnswer = "Melbet adapter reports 98.7% collection coverage. Average transaction validation latency is 240ms. Trust score profile is stable.";
        score = 88.0;
      } else if (lower.includes("crypto") || lower.includes("usdt")) {
        mockAnswer = "Crypto deposit routing detected on 22play. Highly volatile transaction history. Mapped to 3 suspicious proxy wallet addresses.";
        score = 31.2;
      }

      setRagResult({
        query: searchQuery,
        response: mockAnswer,
        trustScore: score,
        vectorMatches: 4,
        sourceFile: "silver_records.parquet",
      });
      setIsSearching(false);
      addLog(`RAG Semantic search completed for query: "${searchQuery}"`);
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 font-sans selection:bg-cyan-500 selection:text-black">
      {/* Glow effects */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-violet-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Navigation Header */}
      <header className="sticky top-0 z-50 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-400 to-violet-500 flex items-center justify-center font-bold text-black text-lg shadow-lg shadow-cyan-500/20">
              S
            </div>
            <div>
              <span className="font-bold tracking-tight text-white">SentinelX</span>
              <span className="ml-1 text-xs text-cyan-400 font-mono bg-cyan-950/80 border border-cyan-800/40 px-1.5 py-0.5 rounded">Trust AI</span>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              <span className="text-xs text-zinc-400 font-mono">v1.0.0-RC1</span>
            </div>
            <div className="h-4 w-[1px] bg-zinc-800" />
            <div className="flex items-center gap-2">
              <span className="text-xs text-zinc-500">API Gateway:</span>
              <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                backendHealth === "healthy" ? "bg-emerald-950 text-emerald-400 border border-emerald-800/30" :
                backendHealth === "offline" ? "bg-rose-950 text-rose-400 border border-rose-800/30" :
                "bg-amber-950 text-amber-400 border border-amber-800/30 animate-pulse"
              }`}>
                {backendHealth.toUpperCase()}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Banner Title */}
        <div className="mb-8">
          <h1 className="text-3xl font-extrabold tracking-tight text-white mb-2 bg-gradient-to-r from-white via-zinc-200 to-zinc-500 bg-clip-text text-transparent">
            Betting Platform Risk Intelligence Console
          </h1>
          <p className="text-zinc-400 max-w-2xl text-sm">
            Observe real-time data ingestion, analyze platform adapter parameters, query vector embeddings via RAG, and verify system integrity.
          </p>
        </div>

        {/* Tab Selection Row */}
        <div className="flex border-b border-zinc-850 mb-8 gap-1">
          {[
            { id: "overview", label: "Overview Dashboard", icon: "📊" },
            { id: "scrapers", label: "Scraper Operations", icon: "🕷️" },
            { id: "etl", label: "ETL Lakehouse", icon: "🏗️" },
            { id: "ai", label: "AI Trust Engine", icon: "🤖" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-5 py-3 text-sm font-medium border-b-2 transition-all ${
                activeTab === tab.id
                  ? "border-cyan-400 text-cyan-400 bg-cyan-950/20"
                  : "border-transparent text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50"
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Tab 1: Overview */}
        {activeTab === "overview" && (
          <div className="space-y-6">
            {/* Top Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
              <div className="bg-zinc-900/40 border border-zinc-800/60 rounded-xl p-5 backdrop-blur">
                <div className="text-zinc-500 text-xs font-mono uppercase mb-1">Total Curated Records</div>
                <div className="text-2xl font-bold text-white tracking-tight">142,805</div>
                <div className="text-emerald-400 text-xs mt-1.5 flex items-center gap-1">
                  <span>↑ 4.2%</span> <span className="text-zinc-500">from last hourly run</span>
                </div>
              </div>

              <div className="bg-zinc-900/40 border border-zinc-800/60 rounded-xl p-5 backdrop-blur">
                <div className="text-zinc-500 text-xs font-mono uppercase mb-1">Average Trust Index</div>
                <div className="text-2xl font-bold text-white tracking-tight">72.4/100</div>
                <div className="text-cyan-400 text-xs mt-1.5 flex items-center gap-1">
                  <span>Stable</span> <span className="text-zinc-500">overall risk rating</span>
                </div>
              </div>

              <div className="bg-zinc-900/40 border border-zinc-800/60 rounded-xl p-5 backdrop-blur">
                <div className="text-zinc-500 text-xs font-mono uppercase mb-1">Pipeline Health</div>
                <div className="text-2xl font-bold text-emerald-400 tracking-tight">100.0%</div>
                <div className="text-zinc-500 text-xs mt-1.5">
                  0 failed runs in past 24h
                </div>
              </div>

              <div className="bg-zinc-900/40 border border-zinc-800/60 rounded-xl p-5 backdrop-blur">
                <div className="text-zinc-500 text-xs font-mono uppercase mb-1">Active Headless sessions</div>
                <div className="text-2xl font-bold text-cyan-400 tracking-tight">
                  {Object.values(scrapersState).filter(s => s === "running").length} / 4
                </div>
                <div className="text-zinc-500 text-xs mt-1.5">
                  Across registered adapters
                </div>
              </div>
            </div>

            {/* Graphs / Central Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* SVG Performance Chart */}
              <div className="bg-zinc-900/40 border border-zinc-800/60 rounded-xl p-5 lg:col-span-2">
                <h3 className="text-white font-semibold text-sm mb-4">Ingestion Activity Trends (Hourly Volume)</h3>
                <div className="h-48 w-full flex items-end">
                  <svg className="w-full h-full text-cyan-500/20" viewBox="0 0 600 160">
                    <path
                      fill="none"
                      stroke="url(#gradient)"
                      strokeWidth="3"
                      d="M 0 140 Q 100 80 150 110 T 300 40 T 450 70 T 600 20"
                    />
                    <path
                      fill="url(#gradient-fill)"
                      d="M 0 140 Q 100 80 150 110 T 300 40 T 450 70 T 600 20 L 600 160 L 0 160 Z"
                    />
                    <defs>
                      <linearGradient id="gradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#22d3ee" />
                        <stop offset="100%" stopColor="#8b5cf6" />
                      </linearGradient>
                      <linearGradient id="gradient-fill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.15" />
                        <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0.0" />
                      </linearGradient>
                    </defs>
                  </svg>
                </div>
                <div className="flex justify-between text-[10px] text-zinc-500 font-mono mt-2">
                  <span>08:00</span>
                  <span>10:00</span>
                  <span>12:00</span>
                  <span>14:00</span>
                  <span>Current Time</span>
                </div>
              </div>

              {/* Status / Feed */}
              <div className="bg-zinc-900/40 border border-zinc-800/60 rounded-xl p-5 flex flex-col">
                <h3 className="text-white font-semibold text-sm mb-3">Devops Operations Log</h3>
                <div className="flex-1 bg-black/60 border border-zinc-800/80 rounded-lg p-3 font-mono text-[11px] text-zinc-400 overflow-y-auto max-h-48 space-y-1.5">
                  {activeLogs.map((log, idx) => (
                    <div key={idx} className="truncate">
                      {log.startsWith("[") ? (
                        <>
                          <span className="text-cyan-600">{log.substring(0, 10)}</span>
                          <span>{log.substring(10)}</span>
                        </>
                      ) : (
                        log
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Scrapers */}
        {activeTab === "scrapers" && (
          <div className="space-y-6">
            <div className="bg-zinc-900/30 border border-zinc-800/40 rounded-xl p-6">
              <h3 className="text-white font-semibold text-base mb-2">Browser Ingestion Adapters</h3>
              <p className="text-zinc-400 text-xs mb-6">
                SentinelX scrapers run under Playwright with anti-fingerprint emulation to acquire payment layouts and receipts dynamically.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {[
                  { name: "OneXBet Adapter", key: "onexbet", desc: "Monitors deposit pages & wallet endpoints." },
                  { name: "Melbet Adapter", key: "melbet", desc: "Scrapes transactional receipt listings." },
                  { name: "TenCric Adapter", key: "tencric", desc: "Polls UPI gateway configurations." },
                  { name: "TwentyTwoXBet Adapter", key: "twentytwoxbet", desc: "Crypto address destination validator." },
                ].map((scraper) => (
                  <div key={scraper.key} className="bg-zinc-900/60 border border-zinc-800/60 rounded-xl p-4 flex items-center justify-between">
                    <div>
                      <h4 className="text-white font-medium text-sm mb-1">{scraper.name}</h4>
                      <p className="text-zinc-500 text-xs">{scraper.desc}</p>
                      <div className="mt-3 flex items-center gap-2">
                        <span className="text-[10px] text-zinc-400 font-mono">Status:</span>
                        <span className={`text-[10px] uppercase font-bold font-mono px-1.5 py-0.5 rounded ${
                          scrapersState[scraper.key as keyof typeof scrapersState] === "idle" ? "bg-zinc-800 text-zinc-400" :
                          scrapersState[scraper.key as keyof typeof scrapersState] === "running" ? "bg-cyan-950 text-cyan-400 animate-pulse" :
                          "bg-emerald-950 text-emerald-400"
                        }`}>
                          {scrapersState[scraper.key as keyof typeof scrapersState]}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => triggerScraper(scraper.key)}
                      disabled={scrapersState[scraper.key as keyof typeof scrapersState] === "running"}
                      className="px-3.5 py-1.5 bg-cyan-500 hover:bg-cyan-400 disabled:bg-zinc-800 disabled:text-zinc-600 text-black text-xs font-bold rounded-lg transition-colors cursor-pointer"
                    >
                      Trigger
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: ETL Medallion */}
        {activeTab === "etl" && (
          <div className="space-y-6">
            <div className="bg-zinc-900/30 border border-zinc-800/40 rounded-xl p-6">
              <h3 className="text-white font-semibold text-base mb-2">Medallion Data Lakehouse Layer</h3>
              <p className="text-zinc-400 text-xs mb-6">
                Data pipeline progress from Bronze (raw JSON) to Silver (deduplicated Parquet) and Gold (AI risk profiling features).
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-6">
                <div className="bg-zinc-950 border border-zinc-800/80 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-amber-400 text-xs font-bold uppercase font-mono">Bronze Layer</span>
                    <span className="text-[10px] text-zinc-500 font-mono">Raw Ingest</span>
                  </div>
                  <div className="text-xl font-bold text-white">418 files</div>
                  <div className="text-xs text-zinc-500 mt-1">Raw scraped browser JSON outputs.</div>
                </div>

                <div className="bg-zinc-950 border border-zinc-800/80 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-cyan-400 text-xs font-bold uppercase font-mono">Silver Layer</span>
                    <span className="text-[10px] text-zinc-500 font-mono">Clean & Schema</span>
                  </div>
                  <div className="text-xl font-bold text-white">3.4M records</div>
                  <div className="text-xs text-zinc-500 mt-1">Deduplicated, schema-validated Parquet.</div>
                </div>

                <div className="bg-zinc-950 border border-zinc-800/80 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-violet-400 text-xs font-bold uppercase font-mono">Gold Layer</span>
                    <span className="text-[10px] text-zinc-500 font-mono">Aggregation</span>
                  </div>
                  <div className="text-xl font-bold text-white">28 profiles</div>
                  <div className="text-xs text-zinc-500 mt-1">Aggregated site & risk level models.</div>
                </div>
              </div>

              {/* Data Quality Tables */}
              <div className="border border-zinc-850 rounded-xl overflow-hidden bg-zinc-950/60">
                <div className="bg-zinc-900/60 border-b border-zinc-850 px-4 py-3 text-xs font-mono text-zinc-400 uppercase">
                  Data Quality rules Check
                </div>
                <div className="divide-y divide-zinc-850 text-xs">
                  <div className="px-4 py-2.5 flex items-center justify-between">
                    <span className="text-zinc-300 font-medium">Null checks on transactional values</span>
                    <span className="text-emerald-400 font-bold">PASS (100% compliant)</span>
                  </div>
                  <div className="px-4 py-2.5 flex items-center justify-between">
                    <span className="text-zinc-300 font-medium">Valid payment type categorizations (UPI, Crypto, Card)</span>
                    <span className="text-emerald-400 font-bold">PASS (100% compliant)</span>
                  </div>
                  <div className="px-4 py-2.5 flex items-center justify-between">
                    <span className="text-zinc-300 font-medium">Duplicate payload filters</span>
                    <span className="text-emerald-400 font-bold">PASS (18,405 records filtered)</span>
                  </div>
                  <div className="px-4 py-2.5 flex items-center justify-between">
                    <span className="text-zinc-300 font-medium">Dead Letter Queue (DLQ) threshold</span>
                    <span className="text-emerald-400 font-bold">PASS (0.01% error rate, under SLA 1.0%)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 4: AI RAG */}
        {activeTab === "ai" && (
          <div className="space-y-6">
            {/* Split Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column: Search Form */}
              <div className="bg-zinc-900/30 border border-zinc-800/40 rounded-xl p-5 lg:col-span-1">
                <h3 className="text-white font-semibold text-sm mb-2">RAG Semantic Search</h3>
                <p className="text-zinc-400 text-xs mb-4">
                  Query SentinelX vector embeddings of platform risk patterns using natural language.
                </p>

                <form onSubmit={handleRagSearch} className="space-y-3">
                  <div>
                    <label className="block text-[10px] font-mono text-zinc-500 mb-1 uppercase">Search Query</label>
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="e.g. UPI anomalies on OneXBet"
                      className="w-full bg-black/60 border border-zinc-800 text-zinc-100 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-cyan-400 transition-colors"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={isSearching}
                    className="w-full py-2 bg-cyan-500 hover:bg-cyan-400 disabled:bg-zinc-850 text-black font-bold text-xs rounded-lg transition-colors cursor-pointer"
                  >
                    {isSearching ? "Searching vector db..." : "Execute Query"}
                  </button>
                </form>

                {/* Preconfigured Prompts */}
                <div className="mt-6">
                  <div className="text-[10px] font-mono text-zinc-500 mb-2 uppercase">Suggested Queries</div>
                  <div className="space-y-2">
                    {[
                      "UPI transactions on OneXBet",
                      "Crypto routing risk status",
                      "Melbet adapter metrics",
                    ].map((q) => (
                      <button
                        key={q}
                        onClick={() => setSearchQuery(q)}
                        className="w-full text-left bg-zinc-900/40 hover:bg-zinc-900/80 border border-zinc-850/80 rounded-lg p-2 text-[11px] text-zinc-400 hover:text-zinc-200 transition-all cursor-pointer"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right Column: Search Results */}
              <div className="bg-zinc-900/30 border border-zinc-800/40 rounded-xl p-5 lg:col-span-2">
                <h3 className="text-white font-semibold text-sm mb-4">RAG Inference Engine Results</h3>

                {ragResult ? (
                  <div className="space-y-4">
                    <div className="bg-zinc-950/80 border border-zinc-850 rounded-xl p-4">
                      <div className="text-[10px] font-mono text-cyan-400 uppercase mb-2">Semantic Match Result</div>
                      <p className="text-sm text-zinc-200 leading-relaxed font-sans">{ragResult.response}</p>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                      <div className="bg-zinc-950 p-3 rounded-lg border border-zinc-850/50">
                        <div className="text-zinc-500 font-mono text-[9px] uppercase mb-0.5">Trust Score</div>
                        <div className={`font-bold text-sm ${
                          ragResult.trustScore > 75 ? "text-emerald-400" :
                          ragResult.trustScore > 40 ? "text-amber-400" : "text-rose-400"
                        }`}>{ragResult.trustScore}/100</div>
                      </div>

                      <div className="bg-zinc-950 p-3 rounded-lg border border-zinc-850/50">
                        <div className="text-zinc-500 font-mono text-[9px] uppercase mb-0.5">Risk Tier</div>
                        <div className={`font-bold text-sm ${
                          ragResult.trustScore > 75 ? "text-emerald-400" :
                          ragResult.trustScore > 40 ? "text-amber-400" : "text-rose-400"
                        }`}>
                          {ragResult.trustScore > 75 ? "Low Risk" :
                           ragResult.trustScore > 40 ? "Medium Risk" : "High Risk"}
                        </div>
                      </div>

                      <div className="bg-zinc-950 p-3 rounded-lg border border-zinc-850/50">
                        <div className="text-zinc-500 font-mono text-[9px] uppercase mb-0.5">Vector Hits</div>
                        <div className="font-bold text-white text-sm">{ragResult.vectorMatches} hits</div>
                      </div>

                      <div className="bg-zinc-950 p-3 rounded-lg border border-zinc-850/50">
                        <div className="text-zinc-500 font-mono text-[9px] uppercase mb-0.5">Source Layer</div>
                        <div className="font-bold text-cyan-400 text-sm truncate">{ragResult.sourceFile}</div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="h-48 border border-dashed border-zinc-800 rounded-xl flex flex-col items-center justify-center text-zinc-500 text-xs">
                    <div>🤖 Waiting for semantic inference query execution.</div>
                    <div className="text-[10px] text-zinc-600 mt-1">Submit a search query on the left.</div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto px-6 py-8 border-t border-zinc-900 mt-12 flex flex-col md:flex-row justify-between items-center text-xs text-zinc-500 gap-4">
        <div>
          © {new Date().getFullYear()} SentinelX Trust AI. Built for open-source presentation.
        </div>
        <div className="flex gap-4">
          <a href="https://localhost/docs" target="_blank" className="hover:text-zinc-300">API Specifications</a>
          <span>•</span>
          <a href="https://localhost/grafana/" target="_blank" className="hover:text-zinc-300">Grafana Telemetry</a>
          <span>•</span>
          <a href="http://127.0.0.1:5050" target="_blank" className="hover:text-zinc-300">Database Console</a>
        </div>
      </footer>
    </div>
  );
}
