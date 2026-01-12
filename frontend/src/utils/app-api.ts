import type { Application } from '@/types/application';

/**
 * 根据应用配置调用API
 */
export async function callApplicationAPI(
  app: Application,
  inputData: Record<string, unknown>,
  onProgress?: (data: unknown) => void,
  onToken?: (token: string) => void,
  onError?: (error: Error) => void
): Promise<unknown> {
  const { api_endpoint, api_method, request_format, response_format, headers, timeout } = app;

  // 准备请求头
  const requestHeaders: HeadersInit = {
    ...headers,
  };

  // 根据请求格式设置Content-Type
  if (api_method !== 'GET') {
    if (request_format === 'json') {
      requestHeaders['Content-Type'] = 'application/json';
    } else if (request_format === 'x-www-form-urlencoded') {
      requestHeaders['Content-Type'] = 'application/x-www-form-urlencoded';
    }
    // form-data 不设置Content-Type，让浏览器自动设置
  }

  // 准备请求体
  let body: BodyInit | undefined;
  if (api_method !== 'GET') {
    if (request_format === 'json') {
      body = JSON.stringify(inputData);
    } else if (request_format === 'x-www-form-urlencoded') {
      const formData = new URLSearchParams();
      Object.entries(inputData).forEach(([key, value]) => {
        formData.append(key, String(value));
      });
      body = formData;
    } else if (request_format === 'form-data') {
      const formData = new FormData();
      Object.entries(inputData).forEach(([key, value]) => {
        formData.append(key, value instanceof File ? value : String(value));
      });
      body = formData;
    }
  }

  // 创建AbortController用于超时控制
  const controller = new AbortController();
  const timeoutId = timeout
    ? setTimeout(() => controller.abort(), timeout * 1000)
    : null;

  try {
    const response = await fetch(api_endpoint, {
      method: api_method || 'POST',
      headers: requestHeaders,
      body,
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // 处理SSE流式响应
    if (response_format === 'sse' || response_format === 'stream') {
      return handleSSEResponse(response, onProgress, onToken, onError);
    }

    // 处理JSON响应
    const data = await response.json();
    if (onProgress) {
      onProgress(data);
    }
    return data;
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('请求超时');
    }
    if (onError) {
      onError(error instanceof Error ? error : new Error('未知错误'));
    }
    throw error;
  } finally {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
  }
}

/**
 * 处理SSE流式响应
 */
async function handleSSEResponse(
  response: Response,
  onProgress?: (data: unknown) => void,
  onToken?: (token: string) => void,
  onError?: (error: Error) => void
): Promise<unknown> {
  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error('无法读取响应流');
  }

  let buffer = '';
  let finalResult: unknown = null;

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      buffer += chunk;
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        // 处理可能的多重 data: 前缀（如 "data: data: {...}"）
        let dataLine = line.trim();
        while (dataLine.startsWith('data: ')) {
          dataLine = dataLine.slice(6).trim();
        }
        
        if (line.startsWith('data: ') || dataLine) {
          try {
            const jsonStr = dataLine || line.slice(6).trim();
            if (!jsonStr) continue;

            const event = JSON.parse(jsonStr);

            // 处理涉密研判智能体的SSE格式
            if (event.type === 'progress') {
              if (onProgress) {
                onProgress(event);
              }
            } else if (event.type === 'stream_token') {
              if (onToken && event.token) {
                onToken(event.token);
              }
            } else if (event.type === 'final') {
              finalResult = event.data;
              if (onProgress) {
                onProgress(event);
              }
            } else if (event.type === 'error') {
              const error = new Error(event.message || '处理过程中发生错误');
              if (onError) {
                onError(error);
              }
              throw error;
            } else {
              // 其他格式的事件
              if (onProgress) {
                onProgress(event);
              }
            }
          } catch (e) {
            // 忽略JSON解析错误（可能是不完整的数据）
            if (e instanceof SyntaxError) continue;
            throw e;
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }

  return finalResult;
}

