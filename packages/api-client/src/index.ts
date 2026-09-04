import createClient, { Middleware } from "openapi-fetch";
import type { paths } from "@sarathi/api-types";

// Standard Error Envelope based on SKILL.md
export interface JobError {
  code: string;
  message: string;
  retryable: boolean;
  details?: Record<string, unknown>;
}

export class ApiError extends Error {
  public code: string;
  public retryable: boolean;
  public details?: Record<string, unknown>;

  constructor(errorData: JobError) {
    super(errorData.message);
    this.name = "ApiError";
    this.code = errorData.code;
    this.retryable = errorData.retryable;
    this.details = errorData.details;
  }
}

let tokenProvider: (() => Promise<string | null>) | null = null;

export function setTokenProvider(provider: () => Promise<string | null>) {
  tokenProvider = provider;
}

const authMiddleware: Middleware = {
  async onRequest({ request }) {
    if (tokenProvider) {
      const token = await tokenProvider();
      if (token) {
        request.headers.set("Authorization", `Bearer ${token}`);
      }
    }
    return request;
  },
  async onResponse({ response }) {
    if (!response.ok) {
      try {
        const data = await response.clone().json();
        if (data && data.error) {
          throw new ApiError(data.error);
        }
      } catch (e) {
        if (e instanceof ApiError) throw e;
        // If parsing fails or it's not our envelope, throw a generic error
        throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
      }
    }
    return response;
  }
};

const baseUrl = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:4010/api/v1";

export const apiClient = createClient<paths>({ baseUrl });
apiClient.use(authMiddleware);

export default apiClient;

export * from './stream';
