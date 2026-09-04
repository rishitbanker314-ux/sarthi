import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "./utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-transparent bg-accent text-accent-foreground",
        secondary: "border-transparent bg-muted text-muted-foreground",
        outline: "text-foreground",
        // Mastery variants
        mastery1: "border-transparent bg-mastery-1 text-slate-800 dark:text-slate-200",
        mastery2: "border-transparent bg-mastery-2 text-green-900 dark:text-green-100",
        mastery3: "border-transparent bg-mastery-3 text-green-900 dark:text-green-100",
        mastery4: "border-transparent bg-mastery-4 text-green-50 dark:text-green-950",
        mastery5: "border-transparent bg-mastery-5 text-green-50 dark:text-green-950",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
