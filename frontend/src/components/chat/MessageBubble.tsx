"use client";

import React from "react";
import { ScrapboxRenderer } from "../scrapbox/ScrapboxRenderer";
import { SourceCard } from "./SourceCard";
import { motion } from "framer-motion";
import { Bot, User } from "lucide-react";

export interface Source {
  title: string;
  text: string;
  url: string;
  score: number;
}

interface MessageBubbleProps {
  role: "user" | "bot";
  content: string;
  sources?: Source[];
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  role,
  content,
  sources,
}) => {
  const isBot = role === "bot";

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      className={`group w-full flex flex-col ${isBot ? "items-start" : "items-end"} mb-10`}
    >
      <div
        className={`flex gap-4 w-full md:max-w-[85%] ${
          isBot ? "flex-row" : "flex-row-reverse"
        }`}
      >
        <div
          className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 shadow-sm ${
            isBot ? "bg-primary text-primary-content" : "bg-secondary text-secondary-content"
          }`}
        >
          {isBot ? <Bot size={18} /> : <User size={18} />}
        </div>
        
        <div className={`flex flex-col gap-2 min-w-0 ${isBot ? "items-start" : "items-end"} flex-1`}>
          {/* Label indicating sender */}
          <span className="text-[10px] font-bold uppercase tracking-widest text-base-content/30 px-1">
            {isBot ? "AI Assistant" : "You"}
          </span>

          <div
            className={`w-full p-5 rounded-3xl shadow-sm relative ${
              isBot
                ? "bg-base-100 text-base-content border border-base-300/60 rounded-tl-none"
                : "bg-secondary text-secondary-content rounded-tr-none"
            }`}
          >
            {isBot ? (
              <div className="prose prose-sm max-w-none text-base-content leading-relaxed">
                {content ? (
                  <ScrapboxRenderer text={content} />
                ) : (
                  <div className="flex gap-1 py-1">
                    <span className="w-1.5 h-1.5 bg-primary/40 rounded-full animate-bounce"></span>
                    <span className="w-1.5 h-1.5 bg-primary/40 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                    <span className="w-1.5 h-1.5 bg-primary/40 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                  </div>
                )}
              </div>
            ) : (
              <p className="whitespace-pre-wrap font-medium">{content}</p>
            )}
          </div>
        </div>
      </div>

      {isBot && sources && sources.length > 0 && (
        <div className="mt-4 ml-12 w-full">
          <div className="flex items-center gap-2 mb-3 text-xs font-bold text-base-content/40">
            <div className="h-px bg-base-300 flex-1"></div>
            <span>SOURCES</span>
            <div className="h-px bg-base-300 flex-1"></div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-[90%]">
            {sources.map((source, index) => (
              <SourceCard key={index} source={source} />
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
};
