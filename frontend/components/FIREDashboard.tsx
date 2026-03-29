"use client";
import { motion } from "framer-motion";
import { Flame, Target, Trophy } from "lucide-react";

export default function FIREDashboard({ fiNumber, successRate }: { fiNumber: number, successRate: number }) {
  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-gradient-to-br from-neutral-800 to-neutral-900 border border-emerald-900/50 p-8 rounded-3xl shadow-2xl relative overflow-hidden"
    >
      {/* Decorative background glow */}
      <div className="absolute top-0 right-0 p-32 bg-emerald-500/10 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none" />
      
      <div className="relative z-10">
        <div className="flex items-center space-x-3 mb-8">
          <Flame className="text-amber-500 w-8 h-8" />
          <h2 className="text-2xl font-bold bg-gradient-to-r from-amber-200 to-amber-500 bg-clip-text text-transparent">
            Your F.I.R.E Target Summary
          </h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-neutral-950/60 p-6 rounded-2xl border border-neutral-800/80 shadow-inner">
            <div className="flex items-center space-x-2 text-neutral-400 mb-2">
              <Target size={18} />
              <span className="font-medium text-sm tracking-wide uppercase">Target F.I. Corpus</span>
            </div>
            <p className="text-5xl font-black text-white font-mono tracking-tight">
              ₹{(fiNumber / 100000).toLocaleString(undefined, { maximumFractionDigits: 1 })}L
            </p>
          </div>
          
          <div className="bg-neutral-950/60 p-6 rounded-2xl border border-neutral-800/80 shadow-inner">
            <div className="flex items-center space-x-2 text-neutral-400 mb-2">
              <Trophy size={18} />
              <span className="font-medium text-sm tracking-wide uppercase">Success Probability</span>
            </div>
            <div className="flex items-end space-x-3">
              <p className={`text-5xl font-black tracking-tight ${successRate >= 80 ? 'text-emerald-400' : successRate > 50 ? 'text-amber-400' : 'text-red-400'}`}>
                {successRate}%
              </p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
