"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { calculateWhatIf } from "@/lib/api";

type BaseParams = {
  monthly_income: number;
  monthly_expense: number;
  current_corpus: number;
  age: number;
};

export default function WhatIfSlider({ baseParams }: { baseParams: BaseParams }) {
  const [extraSip, setExtraSip] = useState(0);
  const [retireEarly, setRetireEarly] = useState(0);
  const [result, setResult] = useState<any>(null);

  // Trigger Debounced recalculations strictly executing after 300ms 
  // ensuring the FastApi Python backend is efficiently invoked
  useEffect(() => {
    const timer = setTimeout(async () => {
      try {
        const res = await calculateWhatIf({
          ...baseParams,
          extra_sip: extraSip,
          retire_early_years: retireEarly,
        });
        setResult(res);
      } catch (err) {
        console.error("Calculation failed:", err);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [extraSip, retireEarly, baseParams]);

  if (!result) {
    return (
      <div className="p-8 border border-neutral-800 rounded-3xl bg-neutral-900/50 flex justify-center h-64 items-center">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-emerald-500"></div>
      </div>
    );
  }

  const successRate = result.success_rate || 0;
  let colorClass = "text-red-400";
  if (successRate > 80) colorClass = "text-emerald-400";
  else if (successRate >= 60) colorClass = "text-amber-400";

  return (
    <div className="bg-gradient-to-br from-neutral-800 to-neutral-900 border border-emerald-900/40 p-6 md:p-8 rounded-3xl shadow-2xl relative overflow-hidden">
      
      {/* Interactive Controls */}
      <div className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-8 z-10 relative">
        <div className="bg-neutral-950/40 p-5 rounded-2xl border border-neutral-800">
          <label className="flex justify-between text-neutral-400 font-medium mb-4 uppercase tracking-wide text-xs">
            <span>Invest more per month</span>
            <span className="text-emerald-400 font-mono text-sm">₹{extraSip.toLocaleString()}</span>
          </label>
          <input
            type="range"
            min="0"
            max="10000"
            step="500"
            value={extraSip}
            onChange={(e) => setExtraSip(Number(e.target.value))}
            className="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
          />
        </div>

        <div className="bg-neutral-950/40 p-5 rounded-2xl border border-neutral-800">
          <label className="flex justify-between text-neutral-400 font-medium mb-4 uppercase tracking-wide text-xs">
            <span>Retire earlier by</span>
            <span className="text-amber-400 font-mono text-sm">{retireEarly} Years</span>
          </label>
          <input
            type="range"
            min="0"
            max="10"
            step="1"
            value={retireEarly}
            onChange={(e) => setRetireEarly(Number(e.target.value))}
            className="w-full h-2 bg-neutral-700 rounded-lg appearance-none cursor-pointer accent-amber-500"
          />
        </div>
      </div>

      <AnimatePresence mode="popLayout">
        <motion.div
          key={result.fi_number + "_" + successRate}
          layout
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="bg-neutral-950/70 p-6 rounded-2xl border border-neutral-800 shadow-inner block"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-1">
              <p className="text-sm text-neutral-400 uppercase tracking-wider font-semibold">Target FI Corpus</p>
              <p className="text-6xl font-black font-mono tracking-tighter text-white">
                ₹{(result.fi_number / 100000).toLocaleString(undefined, { maximumFractionDigits: 1 })}L
              </p>
            </div>
            
            <div className="space-y-1">
              <p className="text-sm text-neutral-400 uppercase tracking-wider font-semibold">Target Hit Rate</p>
              <p className={`text-6xl font-black tracking-tighter ${colorClass}`}>
                {successRate}%
              </p>
            </div>
          </div>

          <div className="mt-8 pt-6 border-t border-neutral-800/80">
            <p className="text-xs text-neutral-500 uppercase tracking-widest mb-4 flex items-center justify-between font-bold">
              <span>Expected FI Scale Spread</span>
              <span>P10 ➔ P90 Range</span>
            </p>
            <div className="flex items-center space-x-4">
              <span className="font-mono text-sm text-neutral-400 font-medium">₹{(result.p10_corpus / 100000).toFixed(1)}L</span>
              <div className="flex-1 h-4 bg-neutral-800 rounded-full overflow-hidden relative shadow-inner">
                {/* Visual marker of the median in the center of the range bar */}
                <div className="absolute h-full w-0.5 bg-amber-400 left-1/2 -translate-x-1/2 z-10 opacity-50"/>
                <div 
                  className="absolute h-full bg-gradient-to-r from-transparent via-emerald-600 to-transparent rounded-full w-full opacity-60"
                />
              </div>
              <span className="font-mono text-sm text-neutral-400 font-medium">₹{(result.p90_corpus / 100000).toFixed(1)}L</span>
            </div>
            <p className="text-center font-mono text-amber-500 mt-3 text-sm font-semibold tracking-wide">
               Predicted Median Core: ₹{(result.median_corpus / 100000).toLocaleString(undefined, { maximumFractionDigits: 1 })}L
            </p>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
