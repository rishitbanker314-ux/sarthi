import { ImagePromptBlock as ImagePromptBlockType } from "@sarathi/api-types";
import { Image as ImageIcon } from "lucide-react";

export function ImagePromptBlock({ block }: { block: ImagePromptBlockType }) {
  // In a real app, this might fetch a generated image based on the prompt.
  // For now, it displays a placeholder.
  return (
    <div className="my-6 rounded-lg border border-border overflow-hidden bg-muted/20">
      <div className="aspect-video bg-muted flex items-center justify-center flex-col gap-3 text-muted-foreground">
        <ImageIcon className="w-12 h-12 opacity-20" />
        <p className="text-sm font-medium opacity-60">Image Generation Placeholder</p>
      </div>
      <div className="p-3 bg-background border-t border-border">
        <p className="text-xs text-muted-foreground italic text-center">
          {block.alt_text || "Generated image"}
        </p>
      </div>
    </div>
  );
}
