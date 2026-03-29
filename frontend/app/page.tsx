"use client";
import FileUpload from "@/components/FileUpload";
import { motion } from "framer-motion";

export default function Home() {
  return (
    <main className="min-h-screen bg-neutral-900 text-neutral-100 flex flex-col items-center justify-center p-8">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-xl w-full text-center space-y-8"
      >
        <div className="space-y-4">
          <h1 className="text-6xl font-black bg-gradient-to-r from-amber-400 to-emerald-400 bg-clip-text text-transparent">
            Dhan-I
          </h1>
          <p className="text-neutral-400 text-lg">
            Your AI-Powered Cognitive Financial Twin. Drop your bank statement to discover your Financial Independence path.
          </p>
        </div>
        
        <FileUpload />
      </motion.div>
    </main>
  );
}
