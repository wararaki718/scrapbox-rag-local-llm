"use client";

import React from "react";
import { parse, Node } from "@progfay/scrapbox-parser";

interface ScrapboxRendererProps {
  text: string;
}

export const ScrapboxRenderer: React.FC<ScrapboxRendererProps> = ({ text }) => {
  const blocks = parse(text);

  const renderNode = (node: Node, index: number): React.ReactNode => {
    switch (node.type) {
      case "plain":
        return <span key={index}>{node.text}</span>;
      case "link":
        if (node.pathType === "relative") {
          return (
            <a
              key={index}
              href={`#${node.href}`}
              className="text-primary hover:underline"
            >
              {node.content || node.href}
            </a>
          );
        }
        return (
          <a
            key={index}
            href={node.href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-secondary hover:underline"
          >
            {node.content || node.href}
          </a>
        );
      case "decoration":
        // decoration covers strong, italic, strike through [* ], [/ ], [- ]
        const classNames = [];
        // Use any to bypass strict type check for varied node properties
        const nodeAny = node as any;
        const decos = nodeAny.decos as string[];
        if (decos.includes("/")) classNames.push("italic");
        if (decos.includes("-")) classNames.push("line-through");
        if (decos.includes("*")) classNames.push("font-bold");
        
        return (
          <span key={index} className={classNames.join(" ")}>
            {nodeAny.nodes.map((n: any, i: number) => renderNode(n, i))}
          </span>
        );
      case "quote":
        return (
          <blockquote key={index} className="border-l-4 border-base-300 pl-4 my-2 italic">
            {node.nodes.map((n, i) => renderNode(n, i))}
          </blockquote>
        );
      case "code":
        return (
          <code key={index} className="bg-base-300 px-1 rounded text-sm">
            {node.text}
          </code>
        );
      case "image":
        return (
          <img
            key={index}
            src={node.src}
            alt="scrapbox image"
            className="max-w-full h-auto rounded-lg shadow-sm my-2"
          />
        );
      default:
        // @ts-ignore
        return node.text || null;
    }
  };

  return (
    <div className="scrapbox-content leading-relaxed space-y-1">
      {blocks.map((block, i) => {
        if (block.type === "line") {
          return (
            <div
              key={i}
              style={{ paddingLeft: `${block.indent * 1.5}rem` }}
              className="min-h-[1.5em]"
            >
              {block.nodes.map((node, j) => renderNode(node, j))}
            </div>
          );
        }
        if (block.type === "codeBlock") {
            return (
                <pre key={i} className="bg-neutral text-neutral-content p-4 rounded-lg overflow-x-auto my-2">
                    <code>{block.content}</code>
                </pre>
            )
        }
        if (block.type === "table") {
            return (
                <div key={i} className="overflow-x-auto my-2">
                    <table className="table table-compact w-full border border-base-300">
                        <tbody>
                            {block.cells.map((row, ri) => (
                                <tr key={ri}>
                                    {row.map((cell, ci) => (
                                        <td key={ci} className="border border-base-300">
                                            {cell.map((n, ni) => renderNode(n, ni))}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )
        }
        return null;
      })}
    </div>
  );
};
