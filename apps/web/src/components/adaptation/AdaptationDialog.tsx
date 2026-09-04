"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import apiClient from "@sarathi/api-client";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, Button, Skeleton } from "@sarathi/ui";
import { Route, AlertTriangle, Lightbulb, TrendingUp } from "lucide-react";
import type { components } from "@sarathi/api-types";

type AdaptationEventResponse = components["schemas"]["AdaptationEventResponse"];

interface AdaptationDialogProps {
  adaptationId: string;
  onOpenChange: (open: boolean) => void;
  onRespond?: (accepted: boolean) => void;
}

export function AdaptationDialog({ adaptationId, onOpenChange, onRespond }: AdaptationDialogProps) {
  const [isOpen, setIsOpen] = useState(true);

  // Fetch recent adaptations to find our event
  const { data: adaptations, isLoading } = useQuery({
    queryKey: ["adaptations"],
    queryFn: async () => {
      const { data, error } = await apiClient.GET("/api/v1/adaptations");
      if (error) throw error;
      return data;
    },
  });

  const adaptation = adaptations?.items?.find((item: AdaptationEventResponse) => item.id === adaptationId);

  const respondMutation = useMutation({
    mutationFn: async (accepted: boolean) => {
      const { data, error } = await apiClient.POST("/api/v1/adaptations/{id}/respond", {
        params: { path: { id: adaptationId } },
        body: { accepted }
      });
      if (error) throw error;
      return data;
    },
    onSuccess: (_, accepted) => {
      setIsOpen(false);
      onOpenChange(false);
      if (onRespond) onRespond(accepted);
    }
  });

  // Derived styling based on action
  const getActionStyles = (action: string) => {
    switch(action) {
      case "insert_prerequisite":
        return { icon: Route, color: "text-blue-500", bg: "bg-blue-500/10", label: "Prerequisite Added" };
      case "slow_pace":
        return { icon: AlertTriangle, color: "text-yellow-500", bg: "bg-yellow-500/10", label: "Pace Slowed" };
      case "reexplain_concept":
        return { icon: Lightbulb, color: "text-green-500", bg: "bg-green-500/10", label: "Concept Re-explained" };
      case "compress_forward":
        return { icon: TrendingUp, color: "text-purple-500", bg: "bg-purple-500/10", label: "Fast-tracked" };
      default:
        return { icon: Route, color: "text-primary", bg: "bg-primary/10", label: "Plan Updated" };
    }
  };

  const ActionIcon = adaptation ? getActionStyles(adaptation.action).icon : Route;
  const styles = adaptation ? getActionStyles(adaptation.action) : { color: "", bg: "", label: "" };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => {
      // Prevent closing by clicking outside if not responded yet
      if (!open && !respondMutation.isSuccess) return;
      setIsOpen(open);
      onOpenChange(open);
    }}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-4 mb-4">
            <div className={`p-3 rounded-full ${styles.bg}`}>
              <ActionIcon className={`w-6 h-6 ${styles.color}`} />
            </div>
            <div>
              <DialogTitle className="text-xl">Plan Update Recommended</DialogTitle>
              <DialogDescription className="text-sm font-medium mt-1 text-foreground">
                {styles.label}
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {isLoading ? (
            <div className="space-y-3">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-5/6" />
              <Skeleton className="h-4 w-4/6" />
            </div>
          ) : adaptation ? (
            <div className="bg-muted/50 p-4 rounded-lg text-sm leading-relaxed border">
              {adaptation.reason}
            </div>
          ) : (
            <div className="text-destructive">
              Could not load adaptation details.
            </div>
          )}
        </div>

        <DialogFooter className="flex gap-3 sm:justify-start">
          <Button 
            variant="outline" 
            className="w-full"
            disabled={isLoading || respondMutation.isPending}
            onClick={() => respondMutation.mutate(false)}
          >
            Decline
          </Button>
          <Button 
            className="w-full"
            disabled={isLoading || respondMutation.isPending || !adaptation}
            onClick={() => respondMutation.mutate(true)}
          >
            {respondMutation.isPending ? "Updating..." : "Accept Change"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
