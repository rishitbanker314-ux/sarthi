import { useState, useEffect, useRef, useCallback } from 'react';
import { parseSSEChunk, StreamEvent } from '@sarathi/api-client/src/stream'; // Importing the pure parser

interface UseStreamMobileOptions {
  url: string;
  method?: string;
  body?: any;
  headers?: Record<string, string>;
  onEvent?: (event: StreamEvent) => void;
  onDone?: () => void;
  onError?: (error: Error) => void;
}

export function useStreamMobile({ url, method = 'GET', body, headers, onEvent, onDone, onError }: UseStreamMobileOptions) {
  const [isStreaming, setIsStreaming] = useState(false);
  const xhrRef = useRef<XMLHttpRequest | null>(null);
  const bufferRef = useRef('');

  const startStream = useCallback(() => {
    setIsStreaming(true);
    bufferRef.current = '';
    
    const xhr = new XMLHttpRequest();
    xhrRef.current = xhr;

    xhr.open(method, url);
    if (headers) {
      Object.entries(headers).forEach(([key, value]) => {
        xhr.setRequestHeader(key, value);
      });
    }
    
    if (body) {
      xhr.setRequestHeader('Content-Type', 'application/json');
    }

    let lastIndex = 0;

    xhr.onreadystatechange = () => {
      if (xhr.readyState === XMLHttpRequest.LOADING || xhr.readyState === XMLHttpRequest.DONE) {
        const responseText = xhr.responseText;
        const chunk = responseText.substring(lastIndex);
        lastIndex = responseText.length;

        if (chunk) {
          const { events, buffer: newBuffer } = parseSSEChunk(chunk, bufferRef.current);
          bufferRef.current = newBuffer;

          events.forEach((event) => {
            if (onEvent) onEvent(event);
            if (event.type === 'done' && onDone) {
              onDone();
            }
            if (event.type === 'error' && onError) {
              onError(new Error(event.message));
            }
          });
        }
      }

      if (xhr.readyState === XMLHttpRequest.DONE) {
        setIsStreaming(false);
        if (xhr.status >= 400 && onError) {
          onError(new Error(`HTTP Error ${xhr.status}`));
        }
      }
    };

    xhr.onerror = () => {
      if (onError) onError(new Error('Network error'));
      setIsStreaming(false);
    };

    xhr.send(body ? JSON.stringify(body) : undefined);
  }, [url, method, body, headers, onEvent, onDone, onError]);

  const stopStream = useCallback(() => {
    if (xhrRef.current) {
      xhrRef.current.abort();
      xhrRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  useEffect(() => {
    return () => {
      stopStream();
    };
  }, [stopStream]);

  return { startStream, stopStream, isStreaming };
}
