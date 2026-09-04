"use client";

import { useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/components/providers/Providers";
import apiClient from "@sarathi/api-client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Skeleton, Badge, Button, CardFooter } from "@sarathi/ui";
import { PlayCircle } from "lucide-react";

export default function PlanPage() {
  const router = useRouter();
  const { id } = useParams() as { id: string };
  const { session, isLoading: isAuthLoading } = useAuth();

  useEffect(() => {
    if (!isAuthLoading && !session) {
      router.push("/login");
    }
  }, [session, isAuthLoading, router]);

  const { data: plan, isLoading, error } = useQuery({
    queryKey: ["plan", id],
    queryFn: async () => {
      const { data, error } = await apiClient.GET("/api/v1/plans/{plan_id}", {
        params: { path: { plan_id: id } }
      });
      if (error) throw error;
      return data;
    },
    enabled: !!session && !!id,
  });

  if (isAuthLoading || isLoading) {
    return (
      <div className="flex min-h-screen p-4 bg-gray-50 dark:bg-gray-950">
        <div className="w-full max-w-5xl mx-auto mt-8 space-y-6">
          <Skeleton className="h-10 w-1/3" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  if (error || !plan) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <Card className="w-full max-w-2xl border-red-500">
          <CardHeader>
            <CardTitle className="text-red-500">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{(error as Error)?.message || "Failed to load plan"}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen p-4 bg-gray-50 dark:bg-gray-950">
      <div className="w-full max-w-5xl mx-auto mt-8 space-y-8">
        <div>
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-gray-100 mb-2">
            {plan.title}
          </h1>
          <Badge variant="secondary" className="mb-4">Version {plan.version}</Badge>
          
          <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-100 dark:border-blue-800">
            <CardContent className="p-4">
              <p className="text-gray-700 dark:text-gray-300 italic">
                {plan.rationale}
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-8">
          {plan.modules.map((module) => (
            <div key={module.id} className="relative">
              <div className="mb-4">
                <h2 className="text-2xl font-semibold flex items-center">
                  <span className="bg-gray-200 dark:bg-gray-800 text-gray-800 dark:text-gray-200 w-8 h-8 rounded-full inline-flex items-center justify-center text-sm mr-3">
                    {module.order_index}
                  </span>
                  {module.title}
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mt-2 ml-11">
                  {module.objective}
                </p>
                <div className="ml-11 mt-2 text-sm text-gray-500 bg-gray-100 dark:bg-gray-800/50 p-3 rounded">
                  <strong>Why this module?</strong> {module.rationale}
                </div>
              </div>

              <div className="ml-14 space-y-4">
                {module.lessons.map((lesson) => (
                  <Card key={lesson.id} className="hover:shadow-md transition-shadow">
                    <CardHeader className="py-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="text-lg">{lesson.title}</CardTitle>
                          <CardDescription className="mt-1">{lesson.objective}</CardDescription>
                        </div>
                        <Badge variant="outline">{lesson.est_minutes} min</Badge>
                      </div>
                    </CardHeader>
                    <CardFooter className="py-3 border-t bg-gray-50 dark:bg-gray-900 flex justify-end">
                      <Button variant="ghost" className="text-blue-600" onClick={() => router.push(`/lessons/${lesson.id}`)}>
                        <PlayCircle className="w-4 h-4 mr-2" /> Start Lesson
                      </Button>
                    </CardFooter>
                  </Card>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
