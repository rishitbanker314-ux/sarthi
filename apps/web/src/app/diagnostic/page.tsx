"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/providers/Providers";
import apiClient from "@sarathi/api-client";
import { Button, Card, CardContent, CardFooter, CardHeader, CardTitle, Skeleton } from "@sarathi/ui";

export default function DiagnosticPage() {
  const router = useRouter();
  const { session, isLoading: isAuthLoading } = useAuth();
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  const [diagnosticState, setDiagnosticState] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedOption, setSelectedOption] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthLoading && !session) {
      router.push("/login");
    }
  }, [session, isAuthLoading, router]);

  useEffect(() => {
    if (!session) return;
    
    // Try to load existing session from localStorage
    const savedSessionId = localStorage.getItem("sarathi_diagnostic_session");
    
    const initDiagnostic = async () => {
      setLoading(true);
      try {
        if (savedSessionId) {
          const { data, error } = await apiClient.GET("/api/v1/diagnostic/sessions/{session_id}", {
            params: { path: { session_id: savedSessionId } }
          });
          if (!error && data) {
            setSessionId(savedSessionId);
            setDiagnosticState(data);
            setLoading(false);
            return;
          }
        }
        
        // Start new session
        const { data, error } = await apiClient.POST("/api/v1/diagnostic/sessions");
        if (error) throw error;
        
        if (data) {
          setSessionId(data.id);
          localStorage.setItem("sarathi_diagnostic_session", data.id);
          setDiagnosticState(data);
        }
      } catch (err: any) {
        setError(err.message || "Failed to initialize diagnostic");
      } finally {
        setLoading(false);
      }
    };

    initDiagnostic();
  }, [session]);

  const handleAnswer = async () => {
    if (!sessionId || !selectedOption) return;
    setSubmitting(true);
    setError(null);
    try {
      const { data, error } = await apiClient.POST("/api/v1/diagnostic/sessions/{session_id}/answer", {
        params: { path: { session_id: sessionId } },
        body: { answer: selectedOption }
      });
      if (error) throw error;
      
      setDiagnosticState(data);
      setSelectedOption("");
    } catch (err: any) {
      setError(err.message || "Failed to submit answer");
    } finally {
      setSubmitting(false);
    }
  };

  const handleComplete = async () => {
    if (!sessionId) return;
    setSubmitting(true);
    setError(null);
    try {
      const { data, error } = await apiClient.POST("/api/v1/diagnostic/sessions/{session_id}/complete", {
        params: { path: { session_id: sessionId } }
      });
      if (error) throw error;
      
      // Cleanup and redirect
      localStorage.removeItem("sarathi_diagnostic_session");
      router.push("/profile");
    } catch (err: any) {
      setError(err.message || "Failed to complete diagnostic");
    } finally {
      setSubmitting(false);
    }
  };

  if (isAuthLoading || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <Card className="w-full max-w-2xl">
          <CardHeader>
            <Skeleton className="h-8 w-1/2" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-6 w-full" />
            <Skeleton className="h-6 w-5/6" />
            <Skeleton className="h-10 w-full mt-8" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <Card className="w-full max-w-2xl border-red-500">
          <CardHeader>
            <CardTitle className="text-red-500">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{error}</p>
          </CardContent>
          <CardFooter>
            <Button onClick={() => window.location.reload()}>Try Again</Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  if (!diagnosticState) return null;

  const { complete, question, progress } = diagnosticState;

  if (complete) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <Card className="w-full max-w-2xl">
          <CardHeader>
            <CardTitle>Diagnostic Complete!</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 dark:text-gray-300">
              We've gathered enough information to build your personalized learner profile. Let's review it.
            </p>
          </CardContent>
          <CardFooter>
            <Button onClick={handleComplete} disabled={submitting}>
              {submitting ? "Finalizing..." : "Review Profile"}
            </Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4 bg-gray-50 dark:bg-gray-950">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle>Diagnostic Assessment</CardTitle>
          {progress && (
            <div className="text-sm text-gray-500 mt-1">
              Question {progress.answered + 1} / ~{progress.estimated_total}
            </div>
          )}
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-lg font-medium text-gray-900 dark:text-gray-100">
            {question?.question_text}
          </div>
          
          <div className="space-y-3">
            {question?.options?.map((option: string, idx: number) => (
              <label 
                key={idx} 
                className={`flex items-center space-x-3 p-4 rounded-lg border cursor-pointer transition-colors ${
                  selectedOption === option 
                    ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20" 
                    : "border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-900"
                }`}
              >
                <input
                  type="radio"
                  name="diagnostic_option"
                  value={option}
                  checked={selectedOption === option}
                  onChange={() => setSelectedOption(option)}
                  className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-gray-700 dark:text-gray-200">{option}</span>
              </label>
            ))}
          </div>
        </CardContent>
        <CardFooter className="flex justify-end">
          <Button 
            onClick={handleAnswer} 
            disabled={!selectedOption || submitting}
          >
            {submitting ? "Submitting..." : "Next Question"}
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
