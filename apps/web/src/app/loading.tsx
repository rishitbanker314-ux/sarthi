import { Skeleton } from "@sarathi/ui";

export default function GlobalLoading() {
  return (
    <div className="container max-w-5xl mx-auto py-8 px-4 space-y-8 animate-in fade-in duration-500">
      <div className="space-y-4">
        <Skeleton className="h-10 w-1/3" />
        <Skeleton className="h-4 w-1/4" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Skeleton className="h-64 w-full md:col-span-2 rounded-xl" />
        <Skeleton className="h-64 w-full rounded-xl" />
      </div>
    </div>
  );
}
