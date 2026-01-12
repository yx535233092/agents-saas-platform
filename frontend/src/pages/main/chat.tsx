import { useState, useRef, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Send,
  ArrowLeft,
  MoreHorizontal,
  Eraser,
  Database,
  Loader2
} from 'lucide-react';
import { ChatMessage, type Message } from '@/components/chat/chat-message';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
import { getApplication } from '@/services/applications';
import { callApplicationAPI } from '@/utils/app-api';
import type { Application } from '@/types/application';
// import { useAuthStore } from '@/stores/auth';

// 格式化节点输出为可读内容
function formatNodeOutput(
  nodeName: string,
  output: Record<string, unknown>,
  currentContent: string
): string {
  const nodeLabels: Record<string, string> = {
    start_node: '1、🚀 开始分析',
    hard_condition_node: '2、🔍 关键词检测',
    judgement_scene_node: '2、🎯 场景识别',
    judgement_secret_directory_node: '3、🔐 秘密目录判别',
    judgement_public_content_node: '4、📋 内容公开判别',
    agent_semantics: '3、🧠 涉密分析',
    agent_non_secret_proof: '4、📋 公开性分析',
    agent_decision: '5、⚖️ 决策评审'
  };

  const label = nodeLabels[nodeName] || nodeName;
  let content = currentContent;

  if (nodeName === 'start_node') {
    content = `### ${label}\n正在初始化分析流程...\n\n`;
  } else if (nodeName === 'hard_condition_node') {
    const isSensitive = output.is_sensitive;
    const evidence = output.evidence || '';
    content += `### ${label}\n`;
    content += isSensitive
      ? `⚠️ **检测到敏感内容**\n${evidence}\n\n`
      : `✅ 未检测到敏感关键词\n\n`;
  } else if (nodeName === 'judgement_scene_node') {
    const scene = output.scene || '';
    content += `### ${label}\n`;
    content += `- 识别场景: **${scene || '分析中...'}**\n\n`;
  } else if (nodeName === 'judgement_secret_directory_node') {
    // 处理秘密目录判别结果（可能是字符串或对象）
    let result: Record<string, unknown> = {};
    if (typeof output === 'string') {
      try {
        result = JSON.parse(output);
      } catch {
        result = { evidence: output };
      }
    } else if (output && typeof output === 'object') {
      result = output as Record<string, unknown>;
    }

    if (result) {
      content += `### ${label}\n`;
      const resultValue = result.result;
      const confidence = result.confidence || 0;
      const evidence = Array.isArray(result.evidence)
        ? result.evidence.join('\n')
        : result.evidence || '...';

      content += `- 判定结果: **${
        resultValue === false
          ? '非涉密'
          : resultValue === true
          ? '涉密'
          : '分析中...'
      }**\n`;
      content += `- 置信度: ${confidence}%\n`;
      content += `- 分析依据:\n${evidence}\n\n`;
    }
  } else if (nodeName === 'judgement_public_content_node') {
    // 处理内容公开判别结果（可能是字符串或对象）
    let result: Record<string, unknown> = {};
    if (typeof output === 'string') {
      try {
        result = JSON.parse(output);
      } catch {
        result = { evidence: output };
      }
    } else if (output && typeof output === 'object') {
      result = output as Record<string, unknown>;
    }

    if (result) {
      content += `### ${label}\n`;
      const isPublic = result.is_public;
      const confidence = result.confidence || 0;
      const evidence = result.evidence || '...';

      content += `- 判定结果: **${
        isPublic === true ? '公开' : isPublic === false ? '非公开' : '分析中...'
      }**\n`;
      content += `- 置信度: ${confidence}%\n`;
      content += `- 分析依据: ${evidence}\n\n`;
    }
  } else if (nodeName === 'agent_semantics') {
    const result = output.secret_analysis_result as Record<string, unknown>;
    if (result) {
      content += `### ${label}\n`;
      content += `- 判定结果: **${result.result || '分析中...'}**\n`;
      content += `- 置信度: ${result.confidence || 0}%\n`;
      content += `- 分析依据: ${result.evidence || '...'}\n\n`;
    }
  } else if (nodeName === 'agent_non_secret_proof') {
    const result = output.public_analysis_result as Record<string, unknown>;
    if (result) {
      content += `### ${label}\n`;
      content += `- 判定结果: **${result.result || '分析中...'}**\n`;
      content += `- 置信度: ${result.confidence || 0}%\n`;
      content += `- 分析依据: ${result.evidence || '...'}\n\n`;
    }
  } else if (nodeName === 'agent_decision') {
    // 决策节点的输出在 formatFinalResult 中处理
    // 但如果收到 progress 事件，也显示状态
    if (output.status) {
      content += `### ${label}\n正在生成最终判定结果...\n\n`;
    } else if (output.is_sensitive !== undefined) {
      // 如果已经收到决策结果，先显示
      const isSensitive = output.is_sensitive;
      const confidence = output.confidence || 0;
      const evidence = output.evidence || '';
      content += `### ${label}\n`;
      content += isSensitive
        ? `⚠️ **判定为涉密文件**\n`
        : `✅ **判定为非涉密文件**\n`;
      content += `- 置信度: ${confidence}%\n`;
      content += `- 证据链: ${evidence}\n\n`;
    }
  }

  return content;
}

// 格式化最终结果
function formatFinalResult(
  result: Record<string, unknown>,
  currentContent: string
): string {
  let content = currentContent;
  content += `---\n\n## 🎯 最终判定\n\n`;

  const isSensitive = result.is_sensitive;
  const confidence = result.confidence || 0;
  const evidence = result.evidence || '';
  const secret_analysis_result = result.secret_analysis_result || '';
  const public_analysis_result = result.public_analysis_result || '';

  if (isSensitive) {
    content += `### ⚠️ **涉密文件**\n\n`;
  } else {
    content += `### ✅ **非涉密文件**\n\n`;
  }

  content += `- **置信度**: ${confidence}\n`;
  content += `- **涉密研判报告**:\n\n${secret_analysis_result}\n`;
  content += `- **公开性判别报告**:\n\n${public_analysis_result}\n`;
  content += `- **证据链**:\n\n${evidence}\n`;

  return content;
}

export default function AppChatPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [app, setApp] = useState<Application | null>(null);
  const [loadingApp, setLoadingApp] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setLoading] = useState(false);
  const [isBatchProcessing, setBatchProcessing] = useState(false);
  const [batchProgress, setBatchProgress] = useState({ current: 0, total: 0 });
  const scrollRef = useRef<HTMLDivElement>(null);

  // 加载应用配置
  useEffect(() => {
    const fetchApp = async () => {
      if (!id) return;
      setLoadingApp(true);
      try {
        const appData = await getApplication(Number(id));
        setApp(appData);
        setMessages([
          {
            id: '0',
            role: 'assistant',
            content: `你好！我是 **${appData.name}**。\n\n${
              appData.description || '请问有什么我可以帮你的吗？'
            }`,
            timestamp: Date.now()
          }
        ]);
      } catch (error) {
        console.error('获取应用配置失败:', error);
        setMessages([
          {
            id: '0',
            role: 'assistant',
            content: '抱歉，无法加载应用配置。',
            timestamp: Date.now()
          }
        ]);
      } finally {
        setLoadingApp(false);
      }
    };

    fetchApp();
  }, [id]);

  useEffect(() => {
    // Auto scroll to bottom
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading || !app) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: Date.now()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    // 不立即创建空消息，等有内容时再创建
    const aiMsgId = (Date.now() + 1).toString();
    let messageCreated = false;

    // 辅助函数：确保消息存在，只在有内容时创建/更新
    const ensureMessageExists = (content: string) => {
      if (!content.trim() && !messageCreated) {
        // 如果内容为空且消息还未创建，不创建消息
        return;
      }

      setMessages((prev) => {
        const existingMsg = prev.find((m) => m.id === aiMsgId);
        if (existingMsg) {
          // 消息已存在，更新内容
          return prev.map((msg) =>
            msg.id === aiMsgId ? { ...msg, content } : msg
          );
        } else {
          // 消息不存在，创建新消息
          messageCreated = true;
          return [
            ...prev,
            {
              id: aiMsgId,
              role: 'assistant',
              content,
              timestamp: Date.now()
            }
          ];
        }
      });
    };

    try {
      // 根据应用类型准备输入数据
      let inputData: Record<string, unknown>;
      if (app.app_type === 'secret_judgement') {
        // 涉密研判智能体的输入格式
        inputData = {
          doc_title: '用户输入',
          doc_content: input
        };
      } else {
        // 自定义应用的输入格式（可以根据需要调整）
        inputData = {
          message: input,
          messages: messages
            .filter((m) => m.id !== '0')
            .map((m) => ({
              role: m.role,
              content: m.content
            }))
        };
      }

      let currentContent = '';

      // 调用应用API
      await callApplicationAPI(
        app,
        inputData,
        // onProgress: 处理进度事件
        (progressData) => {
          const event = progressData as {
            type: string;
            node?: string;
            data?: unknown;
          };

          if (event.type === 'progress' && event.node) {
            // 格式化节点输出
            const nodeData = (event.data as Record<string, unknown>) || {};
            currentContent = formatNodeOutput(
              event.node,
              nodeData,
              currentContent
            );
            // 确保内容不为空
            if (
              !currentContent.trim() &&
              event.node === 'agent_decision' &&
              nodeData.evidence
            ) {
              // 如果决策节点有证据，直接显示
              currentContent += `### 5、⚖️ 决策评审\n`;
              currentContent += nodeData.is_sensitive
                ? `⚠️ **判定为涉密文件**\n`
                : `✅ **判定为非涉密文件**\n`;
              currentContent += `- 置信度: ${nodeData.confidence || 0}%\n`;
              currentContent += `- 证据链: ${nodeData.evidence}\n\n`;
            }
            // 只在有内容时创建/更新消息
            if (currentContent.trim()) {
              ensureMessageExists(currentContent);
            }
          } else if (event.type === 'final') {
            // 处理最终结果
            const finalData = (event as { data?: unknown }).data as Record<
              string,
              unknown
            >;
            if (finalData) {
              currentContent = formatFinalResult(finalData, currentContent);
              ensureMessageExists(currentContent);
            }
          } else if (event.type === 'stream_token') {
            // stream_token 在 onToken 回调中处理，这里不需要额外处理
          }
        },
        // onToken: 处理流式token
        (token) => {
          // 只处理非空token
          if (token && token.trim()) {
            currentContent += token;
            ensureMessageExists(currentContent);
          }
        },
        // onError: 处理错误
        (error) => {
          ensureMessageExists(`错误: ${error.message}`);
        }
      );

      // 如果没有收到任何内容，显示默认消息
      // 注意：这里需要等待一小段时间，因为 SSE 可能是异步的
      setTimeout(() => {
        setMessages((prev) => {
          const msg = prev.find((m) => m.id === aiMsgId);
          // 如果消息不存在或内容为空，创建错误消息
          if (!msg || !msg.content.trim()) {
            if (msg) {
              // 消息存在但内容为空，更新为错误消息
              return prev.map((m) =>
                m.id === aiMsgId
                  ? { ...m, content: '抱歉，我暂时无法回答这个问题。' }
                  : m
              );
            } else {
              // 消息不存在，创建错误消息
              return [
                ...prev,
                {
                  id: aiMsgId,
                  role: 'assistant',
                  content: '抱歉，我暂时无法回答这个问题。',
                  timestamp: Date.now()
                }
              ];
            }
          }
          return prev;
        });
      }, 500);
    } catch (error) {
      console.error('调用应用API失败:', error);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === aiMsgId
            ? {
                ...msg,
                content: `抱歉，服务出现错误：${
                  error instanceof Error ? error.message : '未知错误'
                }。请稍后再试。`
              }
            : msg
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // 批处理函数（仅用于涉密研判智能体）
  const handleBatchProcess = async () => {
    if (
      isBatchProcessing ||
      isLoading ||
      !app ||
      app.app_type !== 'secret_judgement'
    )
      return;

    setBatchProcessing(true);
    setBatchProgress({ current: 0, total: 0 });

    try {
      // 1. 从后端获取数据库数据
      const baseUrl = import.meta.env.VITE_API_URL || '/api';
      const response = await fetch(`${baseUrl}/test-db/`);
      if (!response.ok) {
        throw new Error('获取数据库数据失败');
      }
      const result = await response.json();
      const dbData = result.data || [];

      if (dbData.length === 0) {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now().toString(),
            role: 'assistant',
            content: '数据库中没有数据可处理。',
            timestamp: Date.now()
          }
        ]);
        setBatchProcessing(false);
        return;
      }

      setBatchProgress({ current: 0, total: dbData.length });

      // 2. 添加批处理开始消息
      const batchStartMsg: Message = {
        id: `batch-start-${Date.now()}`,
        role: 'assistant',
        content: `## 📊 开始批处理\n\n共 ${dbData.length} 条数据待处理...\n\n`,
        timestamp: Date.now()
      };
      setMessages((prev) => [...prev, batchStartMsg]);

      // 3. 依次处理每条数据
      for (let i = 0; i < dbData.length; i++) {
        const item = dbData[i];
        const docContent = item['摘要'] || '';
        const fileName = item['文件名'] || `记录 ${i + 1}`;

        if (!docContent.trim()) {
          continue;
        }

        setBatchProgress({ current: i + 1, total: dbData.length });

        // 添加当前处理项的用户消息
        const userMsg: Message = {
          id: `batch-user-${i}-${Date.now()}`,
          role: 'user',
          content: `[批处理 ${i + 1}/${
            dbData.length
          }] ${fileName}\n\n${docContent}`,
          timestamp: Date.now()
        };
        setMessages((prev) => [...prev, userMsg]);

        // 调用应用API进行批处理
        try {
          const inputData = {
            doc_title: fileName,
            doc_content: docContent
          };

          const aiMsgId = `batch-ai-${i}-${Date.now()}`;
          let fullContent = `### 📄 ${fileName}\n\n`;

          setMessages((prev) => [
            ...prev,
            {
              id: aiMsgId,
              role: 'assistant',
              content: fullContent,
              timestamp: Date.now()
            }
          ]);

          await callApplicationAPI(
            app,
            inputData,
            (progressData) => {
              const event = progressData as {
                type: string;
                node?: string;
                data?: unknown;
              };
              if (event.type === 'progress' && event.node) {
                fullContent = formatNodeOutput(
                  event.node,
                  (event.data as Record<string, unknown>) || {},
                  fullContent
                );
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === aiMsgId ? { ...msg, content: fullContent } : msg
                  )
                );
              } else if (event.type === 'final') {
                const finalData = (event as { data?: unknown }).data as Record<
                  string,
                  unknown
                >;
                if (finalData) {
                  fullContent = formatFinalResult(finalData, fullContent);
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === aiMsgId
                        ? { ...msg, content: fullContent }
                        : msg
                    )
                  );
                }
              }
            },
            (token) => {
              fullContent += token;
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === aiMsgId ? { ...msg, content: fullContent } : msg
                )
              );
            }
          );

          // 添加分隔线
          setMessages((prev) => [
            ...prev,
            {
              id: `batch-separator-${i}-${Date.now()}`,
              role: 'assistant',
              content: '---\n\n',
              timestamp: Date.now()
            }
          ]);
        } catch (error) {
          console.error(`处理第 ${i + 1} 条数据时出错:`, error);
          setMessages((prev) => [
            ...prev,
            {
              id: `batch-error-${i}-${Date.now()}`,
              role: 'assistant',
              content: `❌ 处理 "${fileName}" 时出错: ${
                error instanceof Error ? error.message : '未知错误'
              }\n\n`,
              timestamp: Date.now()
            }
          ]);
        }
      }

      // 4. 添加批处理完成消息
      setMessages((prev) => [
        ...prev,
        {
          id: `batch-complete-${Date.now()}`,
          role: 'assistant',
          content: `\n## ✅ 批处理完成\n\n共处理 ${dbData.length} 条数据。\n\n`,
          timestamp: Date.now()
        }
      ]);
    } catch (error) {
      console.error('批处理出错:', error);
      setMessages((prev) => [
        ...prev,
        {
          id: `batch-error-${Date.now()}`,
          role: 'assistant',
          content: `❌ 批处理失败: ${
            error instanceof Error ? error.message : '未知错误'
          }`,
          timestamp: Date.now()
        }
      ]);
    } finally {
      setBatchProcessing(false);
      setBatchProgress({ current: 0, total: 0 });
    }
  };

  if (loadingApp) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">加载应用中...</p>
        </div>
      </div>
    );
  }

  if (!app) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold">应用不存在</h2>
          <p className="mt-2 text-muted-foreground">请返回应用广场选择应用</p>
          <Button className="mt-4" onClick={() => navigate('/')}>
            返回首页
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col overflow-hidden">
      {/* Chat Header */}
      <header className="flex h-14 items-center justify-between border-b px-6">
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/')}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>返回首页</span>
          </Button>
          <div>
            <h1 className="text-base font-semibold">{app.name}</h1>
            <p className="text-xs text-muted-foreground">{app.description}</p>
          </div>
        </div>
        {app.app_type === 'secret_judgement' && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleBatchProcess}
            disabled={isBatchProcessing || isLoading}
            className="flex items-center gap-2"
          >
            <Database className="h-4 w-4" />
            <span>
              {isBatchProcessing
                ? `批处理中 (${batchProgress.current}/${batchProgress.total})`
                : '批处理数据库'}
            </span>
          </Button>
        )}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <MoreHorizontal className="h-5 w-5" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => setMessages([messages[0]])}>
              <Eraser className="mr-2 h-4 w-4" />
              清除上下文
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full px-4 py-4">
          <div className="mx-auto max-w-3xl space-y-4">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            {isLoading && (
              <div className="flex w-full gap-4 p-4">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md border shadow">
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                </div>
                <div className="flex items-center">
                  <span className="text-sm text-muted-foreground">
                    正在思考...
                  </span>
                </div>
              </div>
            )}
            <div ref={scrollRef} />
          </div>
        </ScrollArea>
      </div>

      {/* Input Area */}
      <div className="border-t bg-background p-4">
        <div className="mx-auto flex max-w-3xl items-end gap-4 rounded-xl border bg-background p-3 shadow-sm focus-within:ring-1 focus-within:ring-ring">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入您的问题..."
            className="min-h-[44px] w-full resize-none border-0 bg-transparent p-1 shadow-none focus-visible:ring-0"
            rows={1}
          />
          <Button
            size="icon"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="shrink-0"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <p className="mt-2 text-center text-xs text-muted-foreground">
          内容由 AI 生成，请仔细甄别。
        </p>
      </div>
    </div>
  );
}
