import { MathBlock as MathBlockType } from "@sarathi/api-types";
import "katex/dist/katex.min.css";
import { BlockMath, InlineMath } from "react-katex";

export function MathBlock({ block }: { block: MathBlockType }) {
  return (
    <div className={`my-4 ${block.display ? "text-center overflow-x-auto py-2" : "inline-block"}`}>
      {block.display ? (
        <BlockMath math={block.expression} />
      ) : (
        <InlineMath math={block.expression} />
      )}
    </div>
  );
}
