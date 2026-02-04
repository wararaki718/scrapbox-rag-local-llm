"use client";

import React from "react";
import { Send, Search } from "lucide-react";

interface SearchInputProps {
  query: string;
  setQuery: (q: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  isLoading: boolean;
}

export const SearchInput: React.FC<SearchInputProps> = ({
  query,
  setQuery,
  onSubmit,
  isLoading,
}) => {
  return (
    <div className="px-4 pb-8 pt-2 bg-base-100/80 backdrop-blur-md border-t border-base-300/30">
      <form onSubmit={onSubmit} className="max-w-3xl mx-auto relative group">
        <label className="input input-lg bg-base-200/50 border-base-300/50 flex items-center gap-4 pr-3 rounded-2xl focus-within:bg-base-100 focus-within:ring-4 focus-within:ring-primary/5 transition-all h-16 shadow-inner">
          <Search className="text-base-content/30 group-focus-within:text-primary transition-colors" size={24} />
          <input
            type="text"
            className="grow text-lg font-medium placeholder:text-base-content/30"
            placeholder="Scrapboxの知見を検索..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading}
          />
          <button
            type="submit"
            className={`btn btn-circle btn-primary shadow-lg transition-all ${
              !query.trim() || isLoading ? "btn-disabled opacity-30" : "hover:scale-110 active:scale-95"
            }`}
            disabled={!query.trim() || isLoading}
          >
            {isLoading ? (
              <span className="loading loading-spinner loading-sm"></span>
            ) : (
              <Send size={20} />
            )}
          </button>
        </label>
        <div className="absolute -bottom-6 left-0 right-0 text-center">
            <p className="text-[10px] text-base-content/20 font-bold uppercase tracking-widest">
                Press Enter to ask everything
            </p>
        </div>
      </form>
    </div>
  );
};
