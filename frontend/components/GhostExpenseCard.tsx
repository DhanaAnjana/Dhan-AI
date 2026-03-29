"use client";
import { motion } from "framer-motion";
import { Ghost, TrendingUp } from "lucide-react";

export default function GhostExpenseCard({ merchant, cost }: { merchant: string, cost: number }) {
  return (
    <motion.div 
      whileHover={{ y: -5 }}
      className="bg-neutral-800 border border-neutral-700 p-6 rounded-2xl flex items-center justify-between shadow-lg"
    >
      <div className="flex items-center space-x-4">
        <div className="p-3 bg-red-500/10 rounded-full text-red-500">
          <Ghost size={24} />
        </div>
        <div>
          <h3 className="font-bold text-lg text-neutral-100">{merchant}</h3>
          <p className="text-sm text-neutral-400">Recurring Drain</p>
        </div>
      </div>
      <div className="text-right">
        <p className="text-sm font-medium text-emerald-400 flex items-center justify-end space-x-1 mb-1">
          <TrendingUp size={14} /> <span>10-Yr Cost</span>
        </p>
        <p className="text-2xl font-black font-mono tracking-tight">₹{cost.toLocaleString()}</p>
      </div>
    </motion.div>
  );
}
