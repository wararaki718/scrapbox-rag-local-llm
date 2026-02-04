"use client";

import React, { useEffect, useRef } from "react";
import { MessageBubble, Source } from "./MessageBubble";

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
        <div className="h-full flex flex-col items-center justify-center text-base-content/40 space-y-4">
          <div className="w-16 h-16 rounded-full bg-base-300 flex items-center justify-center">
             <span className="text-4xl">💭</span>
          </div>
          <p>Scrapboxの知見からお答えします。質問をどうぞ。</p>
        </div>
      ) : (
        messages.map((msg, i) => <MessageBubble key={i} {...msg} />)
      )}
      
      {isLoading && (
        <div className="flex gap-3 max-w-[90%]">
          <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center shrink-0">
            <span className="loading loading-dots loading-sm text-primary-content"></span>
          </div>
          <div className="p-4 rounded-2xl bg-base-100 border border-base-300">
             <span className="loading loading-dots loading-md text-primary"></span>
          </div>
        </div>
      )}
    </div>
  );
};
