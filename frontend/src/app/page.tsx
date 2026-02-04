"use client";

import { useState } from "react";
import axios from "axios";
import { Book, Upload, Loader2, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { ChatContainer } from "@/components/chat/ChatContainer";
import { SearchInput } from "@/components/input/SearchInput";
import { Source } from "@/components/chat/MessageBubble";

interface ChatMessage {
  role: "user" | "bot";
  content: string;
  sources?: Source[];
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    const userMessage: ChatMessage = { role: "user", content: query };
    setMessages((prev) => [...prev, userMessage]);
    setQuery("");
    setIsLoading(true);

    // Initial bot message for streaming
    const botMessageId = Date.now();
    setMessages((prev) => [...prev, { role: "bot", content: "", sources: [] }]);

    try {
      const response = await fetch("http://localhost:8000/api/v1/search/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMessage.content }),
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedAnswer = "";
      let foundSources: Source[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.substring(6));
              
              if (data.error) {
                accumulatedAnswer += `\n[Error: ${data.error}]`;
              } else if (data.sources) {
                foundSources = data.sources;
              } else if (data.answer) {
                accumulatedAnswer += data.answer;
              }

              // Update the last message
              setMessages((prev) => {
                const updated = [...prev];
                const lastIdx = updated.length - 1;
                updated[lastIdx] = {
                  ...updated[lastIdx],
                  content: accumulatedAnswer,
                  sources: foundSources,
                };
                return updated;
              });
            } catch (e) {
              console.error("Error parsing JSON chunk", e);
            }
          }
        }
      }
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        { role: "bot", content: "エラーが発生しました。バックエンドサーバーが起動しているか確認してください。" },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsIngesting(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post("http://localhost:8000/api/v1/ingest", formData);
      alert("インポートを開始しました。バックグラウンドで処理されます。");
    } catch (error) {
      console.error(error);
      alert("インポートに失敗しました。");
    } finally {
      setIsIngesting(false);
    }
  };

  return (
    <main className="min-h-screen bg-base-200">
      <div className="max-w-5xl mx-auto h-screen flex flex-col p-4 md:p-8">
        {/* Header */}
        <header className="flex justify-between items-center mb-6 shrink-0">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-3"
          >
            <div className="w-12 h-12 bg-primary text-primary-content rounded-xl flex items-center justify-center shadow-lg">
              <Book size={28} />
            </div>
            <div>
              <h1 className="text-2xl font-black tracking-tight flex items-center gap-2">
                Scrapbox RAG
                <div className="badge badge-secondary badge-sm">BETA</div>
              </h1>
              <p className="text-xs font-medium text-base-content/50 uppercase tracking-widest">
                Local Knowledge Base
              </p>
            </div>
          </motion.div>
          
          <div className="flex gap-2">
            <label className={`btn btn-ghost btn-sm gap-2 border-base-300 ${isIngesting ? "disabled" : ""}`}>
              {isIngesting ? <Loader2 className="animate-spin" size={16} /> : <Upload size={16} />}
              <span className="hidden sm:inline">JSON Import</span>
              <input type="file" className="hidden" onChange={handleFileUpload} accept=".json" disabled={isIngesting} />
            </label>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 bg-base-100 rounded-3xl shadow-2xl flex flex-col overflow-hidden border border-base-300">
           <ChatContainer messages={messages} isLoading={isLoading} />
           <SearchInput 
             query={query} 
             setQuery={setQuery} 
             onSubmit={handleSearch} 
             isLoading={isLoading} 
           />
        </div>

        {/* Footer info */}
        <footer className="mt-4 text-center">
            <p className="text-xs text-base-content/40 flex items-center justify-center gap-1">
              Made with <Sparkles size={12} className="text-secondary" /> for Scrapbox Lovers
            </p>
        </footer>
      </div>
    </main>
  );
}
