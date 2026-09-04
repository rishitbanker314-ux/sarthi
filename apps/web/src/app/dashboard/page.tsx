"use client";

import { useQuery } from "@tanstack/react-query";
import apiClient from "@sarathi/api-client";
import type { components } from "@sarathi/api-types";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter, Button, Badge, Skeleton } from "@sarathi/ui";
import { BookOpen, Flame, Map, Zap, Calendar, TrendingUp, AlertTriangle, Lightbulb, Route as RouteIcon, CheckCircle2, Clock } from "lucide-react";
import { useRouter } from "next/navigation";
import { AdaptationDialog } from "@/components/adaptation/AdaptationDialog";
import { useState } from "react";

export default function DashboardPage() {
  const router = useRouter();
  const [selectedAdaptationId, setSelectedAdaptationId] = useState<string | null>(null);

  const { data: meResponse, isLoading: meLoading } = useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      const { data, error } = await apiClient.GET("/api/v1/me", {});
      if (error) throw error;
      return data;
    },
  });

  const { data: progressData, isLoading: progressLoading } = useQuery({
    queryKey: ["progress"],
    queryFn: async () => {
      const { data, error } = await apiClient.GET("/api/v1/users/me/progress", {});
      if (error) throw error;
      return data;
    },
  });

  const { data: goalsData, isLoading: goalsLoading } = useQuery({
    queryKey: ["goals"],
    queryFn: async () => {
      const { data, error } = await apiClient.GET("/api/v1/goals", {
        params: { query: { page: 1, size: 10 } }
      });
      if (error) throw error;
      return data;
    },
  });

  const { data: adaptationsData, isLoading: adaptationsLoading } = useQuery({
    queryKey: ["adaptations"],
    queryFn: async () => {
      const { data, error } = await apiClient.GET("/api/v1/adaptations");
      if (error) throw error;
      return data;
    },
  });

  const isLoading = meLoading || progressLoading || goalsLoading || adaptationsLoading;
  
  // Try to find the most recent planned goal
  const activeGoal = goalsData?.data?.find((g: any) => g.status === "planned" || g.status === "active") || goalsData?.data?.[0];
  const pendingAdaptation = adaptationsData?.items?.find((a: any) => a.accepted === null);
  const recentAdaptations = adaptationsData?.items?.filter((a: any) => a.accepted !== null).slice(0, 3) || [];

  return (
    <div className="container max-w-5xl mx-auto py-8 px-4 space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            {isLoading ? <Skeleton className="h-9 w-64" /> : `Welcome back${(meResponse as components["schemas"]["MeResponse"])?.display_name ? `, ${(meResponse as components["schemas"]["MeResponse"]).display_name}` : ''}`}
          </h1>
          <p className="text-muted-foreground mt-1">
            Pick up where you left off and keep your streak alive.
          </p>
        </div>
        <div className="flex items-center gap-4 bg-muted/50 p-3 rounded-lg border">
          <div className="flex items-center gap-2">
            <Flame className="w-5 h-5 text-orange-500" />
            <div className="flex flex-col">
              <span className="text-sm font-semibold leading-none">3 Day Streak</span>
              <span className="text-xs text-muted-foreground">Keep it up!</span>
            </div>
          </div>
          <div className="w-px h-8 bg-border"></div>
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-500" />
            <div className="flex flex-col">
              <span className="text-sm font-semibold leading-none">420 XP</span>
              <span className="text-xs text-muted-foreground">This week</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Continue Lesson Card */}
        <Card className="md:col-span-2 border-primary/20 shadow-sm relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardDescription className="flex items-center gap-1.5 font-medium text-primary">
                  <BookOpen className="w-4 h-4" /> Up Next
                </CardDescription>
                <CardTitle className="text-2xl mt-2">
                  {isLoading ? <Skeleton className="h-8 w-3/4" /> : "Introduction to React Hooks"}
                </CardTitle>
              </div>
              <Badge variant="secondary" className="bg-secondary/50">Module 2</Badge>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-4">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-2/3" />
              </div>
            ) : (
              <p className="text-muted-foreground">
                Dive into state management with useState and side effects with useEffect. This lesson will solidify your understanding of functional components.
              </p>
            )}
            
            <div className="mt-6 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Module Progress</span>
                <span className="font-medium">40%</span>
              </div>
              <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                <div className="h-full bg-primary transition-all" style={{ width: "40%" }} />
              </div>
            </div>
          </CardContent>
          <CardFooter className="pt-2">
            <Button className="w-full sm:w-auto" size="lg" onClick={() => router.push(activeGoal ? `/plan/${activeGoal.id}` : "/goals")}>
              Continue Learning
            </Button>
          </CardFooter>
        </Card>

        {/* Current Goal Summary */}
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Map className="w-5 h-5 text-primary" /> Current Goal
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {isLoading ? (
              <div className="space-y-4">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            ) : activeGoal ? (
              <>
                <div>
                  <h4 className="font-medium">{activeGoal.normalized_topic}</h4>
                  <p className="text-sm text-muted-foreground capitalize mt-1">Level: {activeGoal.target_level}</p>
                </div>
                
                <div className="bg-muted/50 rounded-lg p-3 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium flex items-center gap-1.5"><Calendar className="w-4 h-4 text-muted-foreground" /> Deadline</span>
                    <span className="text-sm">{activeGoal.deadline ? new Date(activeGoal.deadline).toLocaleDateString() : 'None'}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium flex items-center gap-1.5"><TrendingUp className="w-4 h-4 text-muted-foreground" /> Overall</span>
                    <span className="text-sm text-primary font-medium">12%</span>
                  </div>
                </div>
                
                <Button variant="outline" className="w-full" onClick={() => router.push(`/goals/${activeGoal.id}`)}>
                  Review Goal
                </Button>
              </>
            ) : (
              <div className="text-center py-6">
                <p className="text-muted-foreground mb-4">You haven't set a learning goal yet.</p>
                <Button onClick={() => router.push("/goals/new")}>Set a Goal</Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Pending Adaptation Alert */}
      {pendingAdaptation && !selectedAdaptationId && (
        <Card className="border-orange-500/50 bg-orange-500/5 shadow-sm">
          <CardContent className="flex flex-col sm:flex-row items-center justify-between gap-4 py-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-500/20 rounded-full">
                <AlertTriangle className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <h4 className="font-semibold text-orange-900 dark:text-orange-300">Plan Update Recommended</h4>
                <p className="text-sm text-orange-800/80 dark:text-orange-400/80 mt-0.5">
                  We noticed you were struggling. We have a new plan for you.
                </p>
              </div>
            </div>
            <Button onClick={() => setSelectedAdaptationId(pendingAdaptation.id)} className="shrink-0 bg-orange-600 hover:bg-orange-700 text-white">
              Review Changes
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Recent Adaptations */}
      {!isLoading && recentAdaptations.length > 0 && (
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <RouteIcon className="w-5 h-5 text-primary" /> Route Adjustments
            </CardTitle>
            <CardDescription>How your path has evolved to fit your pace</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentAdaptations.map((adaptation: any) => (
                <div key={adaptation.id} className="flex items-start gap-3 p-3 rounded-lg border bg-card hover:bg-muted/30 transition-colors">
                  <div className={`mt-0.5 p-2 rounded-full ${
                    adaptation.accepted 
                      ? "bg-green-500/10 text-green-500" 
                      : "bg-muted text-muted-foreground"
                  }`}>
                    {adaptation.accepted ? <CheckCircle2 className="w-4 h-4" /> : <Clock className="w-4 h-4" />}
                  </div>
                  <div>
                    <h5 className="font-medium text-sm">
                      {adaptation.action.replace(/_/g, ' ')}
                    </h5>
                    <p className="text-sm text-muted-foreground mt-1">
                      {adaptation.reason}
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="outline" className="text-xs font-normal">
                        {adaptation.accepted ? 'Accepted' : 'Declined'}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(adaptation.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Mastery Map */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Mastery Map</CardTitle>
          <CardDescription>Your mastery across different concepts</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="h-[200px] flex items-center justify-center">
              <Skeleton className="h-full w-full rounded-md" />
            </div>
          ) : progressData && progressData.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
              {progressData.map((mastery: any) => (
                <div key={mastery.id} className="p-4 border rounded-lg bg-card hover:bg-muted/30 transition-colors">
                  <div className="text-sm font-medium mb-2 truncate" title={mastery.concept_id}>
                    Concept: {mastery.concept_id.substring(0, 8)}...
                  </div>
                  <div className="flex items-end justify-between">
                    <span className="text-2xl font-bold">{parseFloat(mastery.score).toFixed(1)}</span>
                    <span className="text-xs mb-1 text-muted-foreground">/ 10</span>
                  </div>
                  <div className="h-1.5 mt-3 w-full bg-secondary rounded-full overflow-hidden">
                    <div className="h-full bg-primary transition-all" style={{ width: `${(parseFloat(mastery.score) / 10) * 100}%` }} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-12 text-center border rounded-lg border-dashed">
              <div className="w-12 h-12 bg-muted rounded-full flex items-center justify-center mx-auto mb-3">
                <Map className="w-6 h-6 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-medium">No progress yet</h3>
              <p className="text-sm text-muted-foreground mt-1 max-w-sm mx-auto">
                Start a lesson to begin building your mastery map.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Adaptation Dialog Modal */}
      {selectedAdaptationId && (
        <AdaptationDialog 
          adaptationId={selectedAdaptationId}
          onOpenChange={(open) => {
            if (!open) setSelectedAdaptationId(null);
          }}
        />
      )}
    </div>
  );
}
