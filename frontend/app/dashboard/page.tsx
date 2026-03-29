"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, MapPin, Ghost, Settings2 } from "lucide-react";
import GhostExpenseCard from "@/components/GhostExpenseCard";
import WhatIfSlider from "@/components/WhatIfSlider";
import { motion } from "framer-motion";

export default function Dashboard() {
  const router = useRouter();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    // Read the orchestrated LangGraph output from frontend cache securely
    const raw = sessionStorage.getItem("dhan_i_state");
    if (raw) {
      const parsed = JSON.parse(raw);
      setData(parsed.full_state || parsed);
    }
  }, []);

  if (!data) {
    return (
      <div className="min-h-screen bg-neutral-950 flex flex-col items-center justify-center text-emerald-500 font-sans">
        <p className="text-xl animate-pulse">Constructing your architectural roadmap...</p>
      </div>
    );
  }

  const ghosts = data.ghost_expenses || [];
  const roadmapItems = data.roadmap || [];
  const goldMetrics = data.gold_metrics || {};
  const whatIfParams = data.what_if_params || {};

  // Infer safe initial base parameters from Data Pipeline / LangGraph defaults
  const monthly_expense = goldMetrics.total_monthly_spend || 40000;
  const savings_rate = goldMetrics.savings_rate || 0.2;
  
  let inferred_income = 50000;
  if (savings_rate < 1 && savings_rate > 0) {
      inferred_income = monthly_expense / (1 - savings_rate);
  } else if (savings_rate === 0) {
      inferred_income = monthly_expense;
  }
  
  const baseParams = {
    monthly_income: inferred_income,
    monthly_expense: monthly_expense,
    current_corpus: whatIfParams.current_corpus || 500000,
    age: whatIfParams.age || 30
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 font-sans p-4 md:p-12">
      <div className="max-w-7xl mx-auto space-y-12">
        
        <button 
          onClick={() => router.push("/chat")}
          className="flex items-center space-x-2 text-neutral-400 hover:text-emerald-400 transition font-medium"
        >
          <ArrowLeft size={16} />
          <span>Back to Cognitive Twin</span>
        </button>

        <header>
          <h1 className="text-6xl font-black text-white bg-gradient-to-r from-emerald-100 to-emerald-400 bg-clip-text">
            The Execution Plan
          </h1>
          <p className="text-neutral-400 mt-4 text-xl">
            Detected Persona: 
            <span className="text-amber-400 font-black px-3 py-1 bg-amber-500/10 rounded-lg ml-3 tracking-wide">
              {data.user_persona?.replace(/\"|\*|\\/g, '') || "Unknown Signature"}
            </span>
          </p>
        </header>

        {/* Primary Real-time Interactive Terminal */}
        <section className="space-y-6">
          <h2 className="text-3xl font-black text-white flex items-center space-x-3">
            <Settings2 className="text-amber-400" size={28} />
            <span>Interactive F.I.R.E Simulator</span>
          </h2>
          <WhatIfSlider baseParams={baseParams} />
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 pt-8">
          
          <section className="space-y-8">
            <h2 className="text-3xl font-black text-white flex items-center space-x-3">
              <MapPin className="text-emerald-400" size={28} />
              <span>Prioritized Roadmap</span>
            </h2>
            
            <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px before:h-full before:w-0.5 before:bg-gradient-to-b before:from-emerald-500 before:to-neutral-800">
              {roadmapItems.map((step: any, idx: number) => (
                <motion.div 
                  initial={{ opacity: 0, x: -25 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.15 }}
                  key={idx}
                  className="relative flex items-start space-x-6 group"
                >
                  {/* Step Node */}
                  <div className="w-10 h-10 rounded-full border border-emerald-500/50 bg-neutral-900 group-hover:bg-emerald-500 group-hover:text-neutral-950 text-emerald-400 flex items-center justify-center flex-shrink-0 font-black shadow-lg shadow-emerald-500/20 z-10 transition-colors">
                    {step.month}
                  </div>
                  {/* Content */}
                  <div className="flex-1 bg-neutral-900 border border-neutral-800 p-6 rounded-2xl shadow-xl hover:border-emerald-500/30 transition-colors">
                    <h3 className="font-bold text-white text-xl leading-snug">{step.action}</h3>
                    <p className="text-amber-400 font-mono mt-3 font-semibold bg-amber-500/10 inline-block px-3 py-1 rounded-md text-sm border border-amber-500/20">
                      Allocated: ₹{step.amount.toLocaleString()}
                    </p>
                  </div>
                </motion.div>
              ))}
              {roadmapItems.length === 0 && (
                <div className="text-neutral-500 italic p-6 border border-neutral-800 rounded-xl bg-neutral-900">
                  No strict roadmap generated by orchestrator.
                </div>
              )}
            </div>
          </section>

          <section className="space-y-8">
            <h2 className="text-3xl font-black text-white flex items-center space-x-3">
              <Ghost className="text-red-400" size={28} />
              <span>Ghost Expenses Detected</span>
            </h2>
            
            {ghosts.length === 0 ? (
              <div className="p-8 border border-neutral-800 rounded-2xl bg-neutral-900/50 text-center text-emerald-400 font-medium tracking-wide shadow-inner">
                No ghost liabilities detected! Your monthly burn rate is fully optimized.
              </div>
            ) : (
              <div className="space-y-4">
                {ghosts.map((ghost: any, idx: number) => (
                  <GhostExpenseCard 
                    key={idx} 
                    merchant={ghost.merchant} 
                    cost={ghost.opportunity_cost_10yr || 0} 
                  />
                ))}
              </div>
            )}
          </section>
          
        </div>
      </div>
    </div>
  );
}
