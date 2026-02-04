"use client";

import React from "react";
import { ExternalLink, Book } from "lucide-react";
import { Source } from "./MessageBubble";

interface SourceCardProps {
  source: Source;
}

export const SourceCard: React.FC<SourceCardProps> = ({ source }) => {
  return (
    <div className="card w-64 bg-base-100 shadow-sm border border-base-200 hover:shadow-md transition-shadow">
      <div className="card-body p-3">
        <h3 className="card-title text-sm flex items-center gap-2 truncate">
          <Book className="text-secondary shrink-0" size={14} />
          <span className="truncate">{source.title}</span>
        </h3>
        <p className="text-xs text-base-content/60 line-clamp-2">
          {source.text}
        </p>
        <div className="card-actions justify-end mt-2">
          <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-ghost btn-xs text-primary"
          >
            <ExternalLink size={12} />
            View
          </a>
        </div>
      </div>
    </div>
  );
};
