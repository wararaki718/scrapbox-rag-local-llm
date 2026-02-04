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
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex flex-col ${isBot ? "items-start" : "items-end"} mb-6`}
    >
      <div
        className={`flex gap-3 max-w-[90%] ${
          isBot ? "flex-row" : "flex-row-reverse"
        }`}
      >
        <div
          className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
            isBot ? "bg-primary text-primary-content" : "bg-secondary text-secondary-content"
          }`}
        >
          {isBot ? <Bot size={20} /> : <User size={20} />}
        </div>
        <div
          className={`p-4 rounded-2xl shadow-sm ${
            isBot
              ? "bg-base-100 text-base-content border border-base-300"
              : "bg-secondary text-secondary-content"
          }`}
        >
          {isBot ? (
            <ScrapboxRenderer text={content} />
          ) : (
            <p className="whitespace-pre-wrap">{content}</p>
          )}
        </div>
      </div>

      {isBot && sources && sources.length > 0 && (
        <div className="mt-4 ml-12 flex flex-wrap gap-3">
          {sources.map((source, index) => (
            <SourceCard key={index} source={source} />
          ))}
        </div>
      )}
    </motion.div>
  );
};
