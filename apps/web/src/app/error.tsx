"use client";

import { useEffect } from "react";
import { Button } from "@sarathi/ui";
import { AlertTriangle } from "lucide-react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Global Error:", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] px-4 text-center">
      <div className="p-4 bg-destructive/10 rounded-full mb-4">
        <AlertTriangle className="w-10 h-10 text-destructive" />
      </div>
      <h2 className="text-2xl font-bold tracking-tight mb-2">Something went wrong</h2>
      <p className="text-muted-foreground max-w-md mb-6">
        An unexpected error occurred. Please try again or refresh the page.
      </p>
      <Button onClick={() => reset()} size="lg">
        Try again
      </Button>
    </div>
  );
}
