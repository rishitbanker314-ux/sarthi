import { DividerBlock as DividerBlockType } from "@sarathi/api-types";

export function DividerBlock({ block }: { block: DividerBlockType }) {
  return (
    <hr className="my-8 border-t-2 border-border/60 border-dashed" />
  );
}
