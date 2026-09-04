"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/components/providers/Providers";
import apiClient from "@sarathi/api-client";
import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle, Skeleton } from "@sarathi/ui";

export default function JobPollingPage() {
  const router = useRouter();
  const { jobId } = useParams() as { jobId: string };
  const { session, isLoading: isAuthLoading } = useAuth();
  const [shouldPoll, setShouldPoll] = useState(true);

  useEffect(() => {
    if (!isAuthLoading && !session) {
      router.push("/login");
    }
  }, [session, isAuthLoading, router]);

  const { data: job, isLoading, error } = useQuery({
    queryKey: ["job", jobId],
    queryFn: async () => {
      const { data, error } = await apiClient.GET("/api/v1/jobs/{job_id}", {
        params: { path: { job_id: jobId } }
      });
      if (error) throw error;
      
      if (data.status === "succeeded" && data.result?.plan_id) {
        setShouldPoll(false);
        router.push(`/plan/${data.result.plan_id}`);
      } else if (data.status === "failed") {
        setShouldPoll(false);
      }
      
      return data;
    },
    enabled: !!session && !!jobId && shouldPoll,
    refetchInterval: shouldPoll ? 1500 : false,
  });

  if (isAuthLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <Skeleton className="w-full max-w-lg h-64" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4 bg-gray-50 dark:bg-gray-950">
      <Card className="w-full max-w-lg text-center py-8">
        <CardHeader>
          <CardTitle>Generating your plan</CardTitle>
          <CardDescription>We're building a personalized route based on your goal.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
            <div 
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-300" 
              style={{ width: `${job?.progress || 0}%` }}
            />
          </div>
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {job?.progress_message || "Initializing..."}
          </p>
          {error && (
            <div className="mt-4 p-4 bg-red-100 text-red-700 rounded text-sm">
              Failed to check job status: {(error as Error).message}
            </div>
          )}
          {job?.status === "failed" && (
            <div className="mt-4 p-4 bg-red-100 text-red-700 rounded text-sm flex flex-col items-center gap-4">
              <p>Generation failed. Please try again later.</p>
              <Button variant="outline" onClick={() => router.push("/profile")}>Return to Profile</Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
