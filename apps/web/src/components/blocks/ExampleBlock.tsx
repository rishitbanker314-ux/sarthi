import { ExampleBlock as ExampleBlockType } from "@sarathi/api-types";
import { BookOpen } from "lucide-react";

export function ExampleBlock({ block }: { block: ExampleBlockType }) {
  return (
    <div className="my-6 rounded-xl border border-indigo-200 bg-indigo-50/50 dark:border-indigo-900/50 dark:bg-indigo-950/20 overflow-hidden shadow-sm">
      <div className="flex items-center gap-2 px-4 py-3 bg-indigo-100/50 dark:bg-indigo-900/30 border-b border-indigo-200 dark:border-indigo-900/50">
        <BookOpen className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
        <h4 className="font-semibold text-indigo-900 dark:text-indigo-300">
          {block.title || "Example"}
        </h4>
      </div>
      <div className="p-4 text-foreground/90 leading-relaxed">
        {block.content}
      </div>
    </div>
  );
}
