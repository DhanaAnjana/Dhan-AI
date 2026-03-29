"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { sendChat, sendFollowUp } from "@/lib/api";
import ChatBubble from "@/components/ChatBubble";
import { Send, LayoutDashboard, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

type Message = { role: "user" | "assistant"; content: string };

// Dynamically builds a persona explanation using the *actual* data extracted from the user's PDF
function getPersonaExplanation(persona: string, fullState: any): string {
  const ghosts: any[] = fullState?.ghost_expenses || [];
  const ghostNames = ghosts.map((g: any) => g.merchant).slice(0, 3).join(", ") || "recurring small payments";
  const fiNumber: number = fullState?.fi_number || 0;
  const successRate: number = fullState?.monte_carlo_success_rate || 0;

  const fiStr = fiNumber >= 10000000
    ? `₹${(fiNumber / 10000000).toFixed(2)} Crores`
    : fiNumber >= 100000
      ? `₹${(fiNumber / 100000).toFixed(2)} Lakhs`
      : `₹${fiNumber.toLocaleString("en-IN")}`;

  const lower = persona.toLowerCase().replace(/[*"]/g, "").trim();

  if (lower.includes("impulse")) {
    return `🛍️ **You've been classified as an Impulse Spender.**\n\nYour transactions show frequent small, unplanned purchases — your statement reveals recurring debits to merchants like **${ghostNames}**. These individually feel harmless but collectively drain your savings. Your spending pattern is reactive rather than planned.\n\n💡 Your FIRE target is **${fiStr}** with a **${successRate}% success rate**. Small habit shifts here create massive long-term gains.`;
  }
  if (lower.includes("subscription")) {
    return `📱 **You've been classified as a Subscription Collector.**\n\nYour statement shows multiple recurring charges — specifically to **${ghostNames}**. These "set and forget" debits are the sneakiest budget drain because each one feels cheap alone, but together they compound into a significant monthly leak.\n\n💡 Your FIRE target is **${fiStr}**. Redirecting even 2 of these subscriptions into a SIP could meaningfully shift your **${successRate}% success rate** upward.`;
  }
  if (lower.includes("social")) {
    return `👥 **You've been classified as a Social Spender.**\n\nYour money flows heavily around people — splitting bills, sending money, eating out. Your statement shows repeated payments to **${ghostNames}**, which reflects a deeply social spending style.\n\n💡 Your FIRE target is **${fiStr}** with a **${successRate}% success rate**. Building an intentional "experience budget" turns this from a leak into a planned line item.`;
  }

  // Fallback for any other persona the LLM generates
  return `🧠 **You've been classified as: ${persona}**\n\nOur Detective Agent identified this pattern by analyzing your transaction timing, merchant recurrence, and spend distribution. The key recurring merchants detected were: **${ghostNames}**.\n\n💡 Your Financial Independence target is **${fiStr}** with a current Monte Carlo success rate of **${successRate}%**. Your 6-month roadmap has been calibrated around this profile.`;
}

const MESSAGES_KEY = "dhan_i_messages";

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // ── Restore messages from sessionStorage on mount ──────────────────
  useEffect(() => {
    const saved = sessionStorage.getItem(MESSAGES_KEY);
    const rawText = sessionStorage.getItem("dhan_i_raw_text");

    if (rawText) {
      // Fresh file upload — clear old messages and run analysis
      sessionStorage.removeItem(MESSAGES_KEY);
      runInitialAnalysis(rawText);
    } else if (saved) {
      // Returning from dashboard — restore previous conversation
      setMessages(JSON.parse(saved));
    }
  }, []);

  // ── Persist messages every time they change ──────────────────────
  useEffect(() => {
    if (messages.length > 0) {
      sessionStorage.setItem(MESSAGES_KEY, JSON.stringify(messages));
    }
  }, [messages]);

  // ── Auto-scroll ──────────────────────────────────────────────────
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const addMessages = (msgs: Message[]) =>
    setMessages(prev => [...prev, ...msgs]);

  async function runInitialAnalysis(rawText: string) {
    setIsLoading(true);
    setMessages([{ role: "assistant", content: "Analyzing your statements now to map your financial DNA... Give me a few seconds! 🕵️" }]);

    try {
      const res = await sendChat("Build my holistic financial profile and roadmap.", { raw_text: rawText });
      sessionStorage.setItem("dhan_i_state", JSON.stringify(res));

      const persona = res.full_state?.user_persona || "";
      const personaExplanation = getPersonaExplanation(persona, res.full_state);

      setMessages([
        { role: "assistant", content: "Analysis complete! 🚀" },
        { role: "assistant", content: personaExplanation },
        { role: "assistant", content: res.final_response || "Your roadmap is ready — check the Dashboard!" },
      ]);
    } catch (e) {
      addMessages([{ role: "assistant", content: "Sorry, the multi-agent analysis faced an error. Please try again." }]);
    } finally {
      setIsLoading(false);
      sessionStorage.removeItem("dhan_i_raw_text");
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const query = input;
    addMessages([{ role: "user", content: query }]);
    setInput("");
    setIsLoading(true);

    try {
      const cachedStateStr = sessionStorage.getItem("dhan_i_state");
      const cachedState = cachedStateStr ? JSON.parse(cachedStateStr).full_state : {};
      const res = await sendFollowUp(query, cachedState);
      addMessages([{ role: "assistant", content: res.final_response }]);
    } catch (err) {
      addMessages([{ role: "assistant", content: "I'm having trouble connecting right now. Try again in a moment!" }]);
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
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
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
