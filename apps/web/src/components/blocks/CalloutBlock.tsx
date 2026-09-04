import { CalloutBlock as CalloutBlockType } from "@sarathi/api-types";
import { Info, AlertTriangle, Lightbulb, XCircle, Sparkles } from "lucide-react";

export function CalloutBlock({ block }: { block: CalloutBlockType }) {
  const variantStyles = {
    info: {
      container: "bg-blue-50 border-blue-200 text-blue-900 dark:bg-blue-950/40 dark:border-blue-900 dark:text-blue-200",
      icon: <Info className="w-5 h-5 text-blue-500" />,
    },
    tip: {
      container: "bg-green-50 border-green-200 text-green-900 dark:bg-green-950/40 dark:border-green-900 dark:text-green-200",
      icon: <Lightbulb className="w-5 h-5 text-green-500" />,
    },
    warning: {
      container: "bg-amber-50 border-amber-200 text-amber-900 dark:bg-amber-950/40 dark:border-amber-900 dark:text-amber-200",
      icon: <AlertTriangle className="w-5 h-5 text-amber-500" />,
    },
    misconception: {
      container: "bg-rose-50 border-rose-200 text-rose-900 dark:bg-rose-950/40 dark:border-rose-900 dark:text-rose-200",
      icon: <XCircle className="w-5 h-5 text-rose-500" />,
    },
    ai_notice: {
      container: "bg-purple-50 border-purple-200 text-purple-900 text-sm dark:bg-purple-950/40 dark:border-purple-900 dark:text-purple-200 opacity-80",
      icon: <Sparkles className="w-4 h-4 text-purple-500" />,
    },
  };

  const style = variantStyles[block.variant] || variantStyles.info;

  return (
    <div className={`my-5 p-4 rounded-lg border flex gap-3 ${style.container}`}>
      <div className="shrink-0 mt-0.5">{style.icon}</div>
      <div className="flex-1">
        {block.title && <h5 className="font-semibold mb-1 tracking-tight">{block.title}</h5>}
        <div className="leading-relaxed">{block.content}</div>
      </div>
    </div>
  );
}
