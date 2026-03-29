"use client";
import { motion } from "framer-motion";

// Minimal markdown renderer: handles **bold** and newlines
function renderContent(text: string) {
  return text.split("\n").map((line, i) => {
    const parts = line.split(/\*\*(.*?)\*\*/g);
    return (
      <span key={i}>
        {parts.map((part, j) =>
          j % 2 === 1 ? <strong key={j} className="font-bold text-white">{part}</strong> : part
        )}
        {i < text.split("\n").length - 1 && <br />}
      </span>
    );
  });
}

export default function ChatBubble({ role, content }: { role: "user" | "assistant", content: string }) {
  const isUser = role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex w-full ${isUser ? "justify-end" : "justify-start"} mb-4`}
    >
      <div
        className={`max-w-[85%] px-5 py-4 rounded-2xl ${
          isUser
            ? "bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-tr-sm"
            : "bg-neutral-800 text-neutral-200 border border-neutral-700/50 rounded-tl-sm shadow-xl"
        }`}
      >
        <p className="leading-relaxed">{renderContent(content)}</p>
      </div>
    </motion.div>
  );
}
