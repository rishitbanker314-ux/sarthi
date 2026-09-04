"use client";

import { CodeBlock as CodeBlockType } from "@sarathi/api-types";
import { Check, Copy } from "lucide-react";
import { useState } from "react";
import { Button } from "@sarathi/ui";

export function CodeBlock({ block }: { block: CodeBlockType }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(block.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-4 rounded-md overflow-hidden border border-border bg-muted/30">
      <div className="flex items-center justify-between px-4 py-2 bg-muted/50 border-b border-border">
        <span className="text-xs font-mono text-muted-foreground uppercase tracking-wider">
          {block.language || "code"}
        </span>
        <Button variant="ghost" size="sm" onClick={handleCopy} className="h-6 w-6 p-0">
          {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
          <span className="sr-only">Copy code</span>
        </Button>
      </div>
      <div className="p-4 overflow-x-auto">
        <pre className="text-sm font-mono text-foreground/90">
          <code>{block.code}</code>
        </pre>
      </div>
    </div>
  );
}
