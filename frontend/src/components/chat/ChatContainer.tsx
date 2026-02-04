"use client";

import React, { useEffect, useRef } from "react";
import { MessageBubble, Source } from "./MessageBubble";
import { motion } from "framer-motion";

interface ChatMessage {
  role: "user" | "bot";
  content: string;
  sources?: Source[];
}

interface ChatContainerProps {
  messages: ChatMessage[];
  isLoading: boolean;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({
  messages,
  isLoading,
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages, isLoading]);

  return (
    <div
      ref={scrollRef}
      className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4"
    >
      {messages.length === 0 ? (
        <div className="h-full flex flex-col items-center justify-center text-base-content/40 space-y-6">
          <motion.div 
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="w-24 h-24 rounded-3xl bg-base-200 flex items-center justify-center shadow-inner relative"
          >
             <span className="text-5xl animate-pulse">💭</span>
             <div className="absolute -top-2 -right-2 w-6 h-6 bg-secondary rounded-full border-4 border-base-100 animate-bounce"></div>
          </motion.div>
          <div className="text-center">
            <p className="text-xl font-bold text-base-content/60 mb-2">Ready to explore?</p>
            <p className="text-sm">Scrapboxの知見からお答えします。質問をどうぞ。</p>
          </div>
        </div>
      ) : (
        messages.map((msg, i) => <MessageBubble key={i} {...msg} />)
      )}
    </div>
  );
};
