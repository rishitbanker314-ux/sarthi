import { TextBlock as TextBlockType } from "@sarathi/api-types";

export function TextBlock({ block }: { block: TextBlockType }) {
  return (
    <p className="leading-7 [&:not(:first-child)]:mt-4 text-foreground/90">
      {block.content}
    </p>
  );
}
