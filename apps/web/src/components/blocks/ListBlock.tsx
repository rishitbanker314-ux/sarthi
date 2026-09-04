import { ListBlock as ListBlockType } from "@sarathi/api-types";
import { createElement } from "react";

export function ListBlock({ block }: { block: ListBlockType }) {
  const Tag = block.ordered ? "ol" : "ul";
  const listClass = block.ordered ? "list-decimal" : "list-disc";

  return createElement(
    Tag,
    { className: `my-4 ml-6 space-y-2 ${listClass}` },
    block.items.map((item, index) => (
      <li key={index} className="pl-1">
        {item}
      </li>
    ))
  );
}
