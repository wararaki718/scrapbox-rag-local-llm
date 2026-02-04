"use strict";
"use client";

import { useState } from "react";
import axios from "axios";
import { Search, Send, Upload, Book, Link as LinkIcon, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface Source {
  title: string;
  text: string;
  url: string;
  score: number;
}

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

    try {
      const response = await axios.post("http://localhost:8000/api/v1/search", {
        query: userMessage.content,
      });

      const botMessage: ChatMessage = {
        role: "bot",
        content: response.data.answer,
        sources: response.data.sources,
      };
      setMessages((prev) => [...prev, botMessage]);
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
    <main className="min-h-screen bg-base-200 p-4 md:p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <header className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Book className="text-primary" />
              Scrapbox RAG
            </h1>
            <p className="text-base-content/60">Search your Scrapbox knowledge with Gemma 3</p>
          </div>
          <div className="flex gap-2">
            <label className={`btn btn-outline btn-sm ${isIngesting ? "loading" : ""}`}>
              <Upload size={16} />
              JSON Import
              <input type="file" className="hidden" onChange={handleFileUpload} accept=".json" />
            </label>
          </div>
        </header>

        {/* Chat Area */}
        <div className="bg-base-100 rounded-box shadow-xl min-h-[500px] flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-base-content/40 space-y-2">
                <Search size={48} />
                <p>Scrapboxから知識を検索しましょう</p>
              </div>
            )}
            <AnimatePresence>
              {messages.map((msg, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`chat ${msg.role === "user" ? "chat-end" : "chat-start"}`}
                >
                  <div className={`chat-bubble ${msg.role === "user" ? "chat-bubble-primary" : "chat-bubble-secondary bg-opacity-10 text-base-content border border-secondary/20"}`}>
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                    
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-base-content/10 space-y-2">
                        <p className="text-xs font-bold opacity-60 flex items-center gap-1">
                          <LinkIcon size={12} /> SOURCES
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {msg.sources.map((src, j) => (
                            <a
                              key={j}
                              href={src.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="badge badge-outline badge-sm gap-1 hover:badge-primary transition-colors h-auto py-1"
                            >
                              {src.title}
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            {isLoading && (
              <div className="chat chat-start">
                <div className="chat-bubble chat-bubble-secondary bg-opacity-10 text-base-content flex items-center gap-2">
                  <Loader2 className="animate-spin" size={16} />
                  思考中...
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <form onSubmit={handleSearch} className="p-4 bg-base-200/50 border-t border-base-content/5">
            <div className="join w-full">
              <input
                type="text"
                className="input input-bordered join-item w-full bg-base-100"
                placeholder="興味のあることを入力..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <button type="submit" className="btn btn-primary join-item" disabled={isLoading || !query.trim()}>
                <Send size={18} />
              </button>
            </div>
          </form>
        </div>
      </div>
    </main>
  );
}
