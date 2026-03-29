"use client";
import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { uploadFile } from "@/lib/api";
import { UploadCloud, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

export default function FileUpload() {
  const [isDragActive, setIsDragActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const handleFile = async (file: File) => {
    setIsLoading(true);
    try {
      const data = await uploadFile(file);
      // Pass the initial parsed state via session storage for the hackathon
      sessionStorage.setItem("dhan_i_raw_text", data.raw_text);
      router.push("/chat");
    } catch (error) {
      console.error(error);
      alert("Failed to upload. Make sure the backend is running.");
      setIsLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`border-2 border-dashed rounded-xl p-12 cursor-pointer transition-colors ${
        isDragActive ? "border-emerald-400 bg-emerald-400/10" : "border-neutral-700 hover:border-amber-400"
      }`}
      onDragOver={(e) => { e.preventDefault(); setIsDragActive(true); }}
      onDragLeave={() => setIsDragActive(false)}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
    >
      <input 
        type="file" 
        className="hidden" 
        ref={fileInputRef} 
        onChange={(e) => e.target.files && handleFile(e.target.files[0])}
        accept=".pdf,.png,.jpg,.jpeg"
      />
      <div className="flex flex-col items-center justify-center space-y-4 text-neutral-400">
        {isLoading ? (
          <Loader2 className="w-12 h-12 animate-spin text-amber-400" />
        ) : (
          <UploadCloud className="w-12 h-12" />
        )}
        <p className="font-medium text-lg">
          {isLoading ? "Analyzing your transaction footprint..." : "Drag & drop your statement here"}
        </p>
        <p className="text-sm">We securely support PDF, PNG, and JPG</p>
      </div>
    </motion.div>
  );
}
