import { ContentBlock } from "@sarathi/api-types";

export function UnknownBlock({ block }: { block: ContentBlock | any }) {
  return (
    <div className="p-4 border-2 border-dashed border-red-300 bg-red-50 text-red-700 rounded-md my-4 dark:bg-red-950/30 dark:border-red-900/50 dark:text-red-400">
      <p className="font-mono text-sm font-semibold">Unknown Block Type: {block.type}</p>
    </div>
  );
}
