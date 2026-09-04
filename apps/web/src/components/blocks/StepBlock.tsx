"use client";

import { StepBlock as StepBlockType } from "@sarathi/api-types";
import { useState } from "react";
import { Button } from "@sarathi/ui";

export function StepBlock({ block }: { block: StepBlockType }) {
  const [revealed, setRevealed] = useState(!block.reveal);

  const handleReveal = () => {
    setRevealed(true);
    // In a real app, this would emit a hint_requested signal with the block_id
    console.log(`hint_requested signal emitted for block ${block.id}`);
  };

  if (!revealed) {
    return (
      <div className="my-4 p-4 rounded-md border border-dashed border-muted-foreground/30 flex items-center justify-center bg-muted/20">
        <Button variant="secondary" onClick={handleReveal}>
          Show me
        </Button>
      </div>
    );
  }

  return (
    <div className="my-4 pl-4 border-l-2 border-primary/30">
      <p className="leading-7 text-foreground/90">{block.content}</p>
    </div>
  );
}
