import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { Info, Lightbulb, AlertTriangle, XCircle, Sparkles } from "lucide-react"
import { cn } from "./utils"

const calloutVariants = cva(
  "rounded-lg border p-4 flex gap-3 text-sm leading-relaxed",
  {
    variants: {
      variant: {
        info: "border-callout-info/20 bg-callout-info-bg text-callout-info dark:text-foreground",
        tip: "border-callout-tip/20 bg-callout-tip-bg text-callout-tip dark:text-foreground",
        warning: "border-callout-warning/20 bg-callout-warning-bg text-callout-warning dark:text-foreground",
        misconception: "border-callout-misconception/20 bg-callout-misconception-bg text-callout-misconception dark:text-foreground",
        ai_notice: "border-callout-ai/20 bg-callout-ai-bg text-callout-ai dark:text-foreground",
      },
    },
    defaultVariants: {
      variant: "info",
    },
  }
)

export interface CalloutProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof calloutVariants> {
  title?: string
}

const icons = {
  info: Info,
  tip: Lightbulb,
  warning: AlertTriangle,
  misconception: XCircle,
  ai_notice: Sparkles,
}

function Callout({ className, variant, title, children, ...props }: CalloutProps) {
  const Icon = variant ? icons[variant] : icons.info
  
  return (
    <div className={cn(calloutVariants({ variant }), className)} {...props}>
      <Icon className="h-5 w-5 shrink-0 mt-0.5" />
      <div className="flex flex-col gap-1">
        {title && <span className="font-semibold">{title}</span>}
        <div className="text-foreground">{children}</div>
      </div>
    </div>
  )
}

export { Callout, calloutVariants }
