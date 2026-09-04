import { AnalogyBlock as AnalogyBlockType } from "@sarathi/api-types";
import { Quote } from "lucide-react";

export function AnalogyBlock({ block }: { block: AnalogyBlockType }) {
  return (
    <div className="my-6 relative rounded-lg border-l-4 border-l-orange-400 bg-orange-50/50 dark:bg-orange-950/20 dark:border-l-orange-600 p-5 shadow-sm">
      <Quote className="absolute top-4 right-4 w-8 h-8 text-orange-200 dark:text-orange-900/40 rotate-180" />
      <div className="pr-8 text-foreground/90 leading-relaxed italic">
        {block.content}
      </div>
    </div>
  );
}
