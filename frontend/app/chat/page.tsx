"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { sendChat } from "@/lib/api";
import ChatBubble from "@/components/ChatBubble";
import { Send, LayoutDashboard, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<{role: "user"|"assistant", content: string}[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    // Initial kickoff when landing after OCR
    const initiateAnalysis = async () => {
      const rawText = sessionStorage.getItem("dhan_i_raw_text");
      if (rawText) {
        setIsLoading(true);
        setMessages([{role: "assistant", content: "Analyzing your statements now to map your financial DNA... Give me a few seconds! 🕵️"}]);
        
        try {
            // First time logic calls /chat with just the extracted document text
          const res = await sendChat("Build my holistic financial profile and roadmap.", { raw_text: rawText });
          
          sessionStorage.setItem("dhan_i_state", JSON.stringify(res));
          setMessages([
            {role: "assistant", content: "Analysis complete! 🚀"},
            {role: "assistant", content: res.final_response || "Check out your dashboard!"}
          ]);
        } catch(e) {
          setMessages(prev => [...prev, {role: "assistant", content: "Sorry, the multi-agent analysis faced an error bridging."}]);
        } finally {
          setIsLoading(false);
          sessionStorage.removeItem("dhan_i_raw_text");
        }
      }
    };
    initiateAnalysis();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if(!input.trim()) return;
    
    const query = input;
    setMessages(prev => [...prev, {role: "user", content: query}]);
    setInput("");
    setIsLoading(true);
    
    try {
      const cachedStateStr = sessionStorage.getItem("dhan_i_state");
      const currentState = cachedStateStr ? JSON.parse(cachedStateStr).full_state : {};
      
      const res = await sendChat(query, currentState);
      
      // Update cache
      sessionStorage.setItem("dhan_i_state", JSON.stringify(res));
      
      setMessages(prev => [...prev, {role: "assistant", content: res.final_response}]);
    } catch(err) {
      setMessages(prev => [...prev, {role: "assistant", content: "I'm having trouble connecting right now."}]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-neutral-900 text-neutral-100 font-sans">
      <header className="p-4 bg-neutral-950 border-b border-neutral-800 flex justify-between items-center z-10">
        <h1 className="text-2xl font-black bg-gradient-to-r from-amber-400 to-emerald-400 bg-clip-text text-transparent">Dhan-I</h1>
        <button 
          onClick={() => router.push("/dashboard")}
          className="flex items-center space-x-2 bg-gradient-to-r from-emerald-600 to-emerald-700 hover:opacity-90 px-4 py-2 rounded-lg font-medium transition shadow-lg shadow-emerald-900/40"
        >
          <LayoutDashboard size={18} />
          <span>View Dashboard</span>
        </button>
      </header>
      
      <main className="flex-1 overflow-y-auto p-4 md:p-8 space-y-4 max-w-5xl mx-auto w-full" ref={scrollRef}>
        <AnimatePresence>
          {messages.map((m, i) => (
            <ChatBubble key={i} role={m.role} content={m.content} />
          ))}
          {isLoading && (
            <motion.div initial={{opacity: 0}} animate={{opacity: 1}} className="flex justify-start">
              <div className="bg-neutral-800 px-5 py-4 rounded-2xl rounded-tl-sm w-16 flex justify-center border border-neutral-700/50">
                <Loader2 className="w-5 h-5 animate-spin text-amber-400" />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
      
      <footer className="p-4 bg-neutral-950 border-t border-neutral-800">
        <form onSubmit={handleSubmit} className="max-w-5xl mx-auto flex items-center gap-2">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            placeholder="Ask your Cognitive Twin about your financial future..."
            className="flex-1 bg-neutral-800 rounded-full px-6 py-4 outline-none focus:ring-2 ring-emerald-500/50 transition placeholder:text-neutral-500 shadow-inner"
          />
          <button 
            type="submit" 
            disabled={isLoading || !input.trim()}
            className="bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-neutral-950 p-4 rounded-full transition shadow-lg"
          >
            <Send size={20} className="ml-0.5" />
          </button>
        </form>
      </footer>
    </div>
  );
}
