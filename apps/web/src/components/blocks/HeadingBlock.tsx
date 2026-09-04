import { HeadingBlock as HeadingBlockType } from "@sarathi/api-types";
import { createElement } from "react";

export function HeadingBlock({ block }: { block: HeadingBlockType }) {
  const Tag = `h${block.level}`;
  
  const sizeClasses = {
    1: "text-3xl font-bold mt-8 mb-4 tracking-tight",
    2: "text-2xl font-semibold mt-6 mb-3 tracking-tight",
    3: "text-xl font-semibold mt-5 mb-2",
    4: "text-lg font-medium mt-4 mb-2",
    5: "text-base font-medium mt-4 mb-1",
    6: "text-sm font-medium mt-4 mb-1 text-muted-foreground",
  };

  return createElement(
    Tag,
    { className: sizeClasses[block.level] },
    block.text
  );
}
