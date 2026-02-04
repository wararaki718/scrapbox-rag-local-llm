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
    <div className="p-4 bg-base-100 border-t border-base-300">
      <form onSubmit={onSubmit} className="relative group">
        <label className="input input-bordered flex items-center gap-3 pr-2 focus-within:ring-2 focus-within:ring-primary/20 transition-all">
          <Search className="text-base-content/40 group-focus-within:text-primary transition-colors" size={20} />
          <input
            type="text"
            className="grow py-4"
            placeholder="何について知りたいですか？"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isLoading}
          />
          <button
            type="submit"
            className={`btn btn-circle btn-primary btn-sm ${
              isLoading ? "btn-disabled" : ""
            }`}
            disabled={!query.trim() || isLoading}
          >
            <Send size={16} />
          </button>
        </label>
      </form>
      <p className="text-[10px] text-center mt-2 text-base-content/40 uppercase tracking-widest font-semibold">
        Powered by Gemma 3 & Scrapbox
      </p>
    </div>
  );
};
