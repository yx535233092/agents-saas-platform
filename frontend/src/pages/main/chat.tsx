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
  Loader2,
  Database,
  Play,
  History,
  X,
  Trash2
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
import { databaseConfigService } from '@/services/database-configs';
import type { DatabaseConfig } from '@/types/database-config';
import {
  chatHistoryService,
  type ChatHistoryListItem
} from '@/services/chat-history';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
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
  const scrollRef = useRef<HTMLDivElement>(null);

  // 批处理相关状态
  const [batchDialogOpen, setBatchDialogOpen] = useState(false);
  const [databaseConfigs, setDatabaseConfigs] = useState<DatabaseConfig[]>([]);
  const [selectedDbConfigId, setSelectedDbConfigId] = useState<number | null>(
    null
  );
  const [tableName, setTableName] = useState('test');
  const [isBatchProcessing, setBatchProcessing] = useState(false);
  const [batchProgress, setBatchProgress] = useState({
    current: 0,
    total: 0,
    success: 0,
    failed: 0
  });

  // 历史记录相关状态
  const [historySidebarOpen, setHistorySidebarOpen] = useState(false);
  const [histories, setHistories] = useState<ChatHistoryListItem[]>([]);
  const [loadingHistories, setLoadingHistories] = useState(false);
  const [currentHistoryId, setCurrentHistoryId] = useState<number | null>(null);

  // 加载数据库配置列表
  useEffect(() => {
    const fetchDbConfigs = async () => {
      try {
        // 获取所有数据库配置（包括未启用的）
        const configs = await databaseConfigService.list();
        setDatabaseConfigs(Array.isArray(configs) ? configs : []);
        console.log('加载的数据库配置:', configs);
      } catch (error) {
        console.error('获取数据库配置失败:', error);
      }
    };
    fetchDbConfigs();
  }, []);

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

  // 加载历史记录列表
  useEffect(() => {
    if (!app || app.app_type !== 'secret_judgement') return;

    const fetchHistories = async () => {
      setLoadingHistories(true);
      try {
        const data = await chatHistoryService.list(app.id, { limit: 50 });
        setHistories(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error('获取历史记录失败:', error);
      } finally {
        setLoadingHistories(false);
      }
    };

    fetchHistories();
  }, [app]);

  useEffect(() => {
    // Auto scroll to bottom
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // 自动保存历史记录（仅涉密研判智能体）
  useEffect(() => {
    if (!app || app.app_type !== 'secret_judgement' || isLoading) return;

    const currentMessages = messages.filter((m) => m.id !== '0'); // 排除欢迎消息
    if (currentMessages.length < 2) return; // 至少需要用户消息和AI回复

    // 防抖：延迟保存
    const timer = setTimeout(async () => {
      try {
        const userMessages = currentMessages.filter((m) => m.role === 'user');
        const lastUserMessage = userMessages[userMessages.length - 1];

        if (!lastUserMessage) return;

        if (currentHistoryId) {
          // 更新现有历史记录
          await chatHistoryService.update(currentHistoryId, {
            messages: currentMessages.map((m) => ({
              id: m.id,
              role: m.role,
              content: m.content,
              timestamp: m.timestamp
            }))
          });
        } else {
          // 创建新历史记录
          const history = await chatHistoryService.create({
            application_id: app.id,
            user_input: lastUserMessage.content,
            messages: currentMessages.map((m) => ({
              id: m.id,
              role: m.role,
              content: m.content,
              timestamp: m.timestamp
            }))
          });
          setCurrentHistoryId(history.id);
          // 刷新历史记录列表
          const data = await chatHistoryService.list(app.id, { limit: 50 });
          setHistories(Array.isArray(data) ? data : []);
        }
      } catch (error) {
        console.error('保存历史记录失败:', error);
      }
    }, 2000); // 延迟2秒保存，避免频繁保存

    return () => clearTimeout(timer);
  }, [messages, app, currentHistoryId, isLoading]);

  const handleSend = async () => {
    if (!input.trim() || isLoading || !app) return;

    const userMsgId = Date.now().toString();
    const userMsg: Message = {
      id: userMsgId,
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

    // 保存历史记录（仅涉密研判智能体，在消息更新后）
    if (app?.app_type === 'secret_judgement') {
      setTimeout(async () => {
        try {
          const currentMessages = messages.filter((m) => m.id !== '0'); // 排除欢迎消息
          if (currentMessages.length === 0) return;

          // 获取用户输入（最后一条用户消息）
          const userMessages = currentMessages.filter((m) => m.role === 'user');
          const lastUserMessage = userMessages[userMessages.length - 1];

          if (!lastUserMessage) return;

          // 获取最新的消息列表（包括刚发送的消息）
          const allMessages = [
            ...currentMessages,
            {
              id: userMsgId,
              role: 'user' as const,
              content: input,
              timestamp: Date.now()
            }
          ];

          if (currentHistoryId) {
            // 更新现有历史记录
            await chatHistoryService.update(currentHistoryId, {
              messages: allMessages.map((m) => ({
                id: m.id,
                role: m.role,
                content: m.content,
                timestamp: m.timestamp
              }))
            });
          } else {
            // 创建新历史记录
            const history = await chatHistoryService.create({
              application_id: app.id,
              user_input: input,
              messages: allMessages.map((m) => ({
                id: m.id,
                role: m.role,
                content: m.content,
                timestamp: m.timestamp
              }))
            });
            setCurrentHistoryId(history.id);
            // 刷新历史记录列表
            const data = await chatHistoryService.list(app.id, { limit: 50 });
            setHistories(Array.isArray(data) ? data : []);
          }
        } catch (error) {
          console.error('保存历史记录失败:', error);
        }
      }, 1000); // 延迟1秒确保消息已更新
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // 批处理函数
  const handleBatchProcess = async () => {
    if (!app || !selectedDbConfigId || isBatchProcessing) {
      return;
    }

    setBatchProcessing(true);
    setBatchProgress({ current: 0, total: 0, success: 0, failed: 0 });

    try {
      // 1. 从数据库获取数据
      const queryResult = await databaseConfigService.queryData(
        selectedDbConfigId,
        {
          table_name: tableName
        }
      );

      if (
        !queryResult.success ||
        !queryResult.data ||
        queryResult.data.length === 0
      ) {
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
        setBatchDialogOpen(false);
        return;
      }

      const dbData = queryResult.data;
      setBatchProgress({
        current: 0,
        total: dbData.length,
        success: 0,
        failed: 0
      });

      // 2. 添加批处理开始消息
      const batchStartMsg: Message = {
        id: `batch-start-${Date.now()}`,
        role: 'assistant',
        content: `## 📊 开始批处理\n\n共 ${dbData.length} 条数据待处理，使用并发处理...\n\n`,
        timestamp: Date.now()
      };
      setMessages((prev) => [...prev, batchStartMsg]);
      setBatchDialogOpen(false);

      // 3. 并发处理数据（使用 Promise.allSettled 并发执行）
      const concurrency = 5; // 并发数
      const results: Array<{
        success: boolean;
        index: number;
        data: Record<string, unknown>;
        error?: string;
        fileName?: string;
      }> = [];

      for (let i = 0; i < dbData.length; i += concurrency) {
        const batch = dbData.slice(i, i + concurrency);
        const batchPromises = batch.map(
          async (item: Record<string, unknown>, batchIndex: number) => {
            const globalIndex = i + batchIndex;
            const docContent =
              item['全文'] || item['摘要'] || item['doc_content'] || '';
            const fileName =
              item['文件名'] || item['doc_title'] || `记录 ${globalIndex + 1}`;

            if (
              !docContent ||
              typeof docContent !== 'string' ||
              !docContent.trim()
            ) {
              return {
                success: false,
                index: globalIndex,
                data: item,
                error: '内容为空'
              };
            }

            try {
              const inputData = {
                doc_title: fileName,
                doc_content: docContent
              };

              // 调用智能体API（批处理时静默处理，不显示进度）
              await callApplicationAPI(
                app,
                inputData,
                undefined, // 不显示进度回调
                undefined // 不显示token回调
              );

              return {
                success: true,
                index: globalIndex,
                data: item,
                fileName: String(fileName)
              };
            } catch (error) {
              return {
                success: false,
                index: globalIndex,
                data: item,
                error: error instanceof Error ? error.message : '未知错误'
              };
            }
          }
        );

        const batchResults = await Promise.allSettled(batchPromises);
        const settledResults = batchResults.map((result, idx) => {
          if (result.status === 'fulfilled') {
            return result.value;
          } else {
            return {
              success: false,
              index: i + idx,
              data: batch[idx],
              error: (result.reason as Error)?.message || '处理失败'
            };
          }
        });

        results.push(...settledResults);

        // 更新进度
        const successCount = results.filter((r) => r.success).length;
        const failedCount = results.filter((r) => !r.success).length;
        setBatchProgress({
          current: results.length,
          total: dbData.length,
          success: successCount,
          failed: failedCount
        });
      }

      // 4. 添加批处理结果消息
      const successCount = results.filter((r) => r.success).length;
      const failedCount = results.filter((r) => !r.success).length;

      let resultContent = `\n## ✅ 批处理完成\n\n`;
      resultContent += `- 总计: ${dbData.length} 条\n`;
      resultContent += `- 成功: ${successCount} 条\n`;
      resultContent += `- 失败: ${failedCount} 条\n\n`;

      if (failedCount > 0) {
        resultContent += `### 失败记录:\n\n`;
        results
          .filter((r) => !r.success)
          .forEach((r) => {
            const fileName =
              r.data['文件名'] || r.data['doc_title'] || `记录 ${r.index + 1}`;
            resultContent += `- ${fileName}: ${r.error}\n`;
          });
      }

      setMessages((prev) => [
        ...prev,
        {
          id: `batch-complete-${Date.now()}`,
          role: 'assistant',
          content: resultContent,
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
      setBatchProgress({ current: 0, total: 0, success: 0, failed: 0 });
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

  // 加载历史记录
  const handleLoadHistory = async (historyId: number) => {
    try {
      const history = await chatHistoryService.get(historyId);
      setMessages(history.messages as Message[]);
      setCurrentHistoryId(historyId);
    } catch (error) {
      console.error('加载历史记录失败:', error);
    }
  };

  // 删除历史记录
  const handleDeleteHistory = async (
    historyId: number,
    e: React.MouseEvent
  ) => {
    e.stopPropagation();
    if (!confirm('确定要删除这条历史记录吗？')) return;

    try {
      await chatHistoryService.delete(historyId);
      setHistories((prev) => prev.filter((h) => h.id !== historyId));
      if (currentHistoryId === historyId) {
        setCurrentHistoryId(null);
        setMessages([
          {
            id: '0',
            role: 'assistant',
            content: `你好！我是 **${app?.name || ''}**。\n\n${
              app?.description || '请问有什么我可以帮你的吗？'
            }`,
            timestamp: Date.now()
          }
        ]);
      }
    } catch (error) {
      console.error('删除历史记录失败:', error);
    }
  };

  // 创建新对话
  const handleNewChat = () => {
    setCurrentHistoryId(null);
    setMessages([
      {
        id: '0',
        role: 'assistant',
        content: `你好！我是 **${app?.name || ''}**。\n\n${
          app?.description || '请问有什么我可以帮你的吗？'
        }`,
        timestamp: Date.now()
      }
    ]);
    setHistorySidebarOpen(false);
  };

  return (
    <div className="flex h-full overflow-hidden">
      {/* 历史记录侧边栏 */}
      {app?.app_type === 'secret_judgement' && (
        <div
          className={`${
            historySidebarOpen ? 'w-64' : 'w-0'
          } transition-all duration-300 border-r bg-sidebar overflow-hidden flex flex-col`}
        >
          <div className="flex h-14 items-center justify-between border-b px-4">
            <h2 className="font-semibold">历史记录</h2>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setHistorySidebarOpen(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            <Button
              variant="outline"
              className="w-full mb-2"
              onClick={handleNewChat}
            >
              <Send className="mr-2 h-4 w-4" />
              新建对话
            </Button>
            {loadingHistories ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            ) : histories.length === 0 ? (
              <div className="text-center text-sm text-muted-foreground py-8">
                暂无历史记录
              </div>
            ) : (
              <div className="space-y-1">
                {histories.map((history) => (
                  <div
                    key={history.id}
                    className={`group relative rounded-md border p-3 cursor-pointer transition-colors hover:bg-sidebar-accent ${
                      currentHistoryId === history.id
                        ? 'bg-sidebar-accent border-primary'
                        : ''
                    }`}
                    onClick={() => handleLoadHistory(history.id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">
                          {history.title || history.user_input || '未命名对话'}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {new Date(history.updated_at).toLocaleString('zh-CN')}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={(e) => handleDeleteHistory(history.id, e)}
                      >
                        <Trash2 className="h-3 w-3 text-destructive" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* 主内容区域 */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Chat Header */}
        <header className="flex h-14 items-center justify-between border-b px-6">
          <div className="flex items-center gap-4">
            {app?.app_type === 'secret_judgement' && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setHistorySidebarOpen(!historySidebarOpen)}
                className="flex items-center gap-2"
              >
                <History className="h-4 w-4" />
              </Button>
            )}
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
          {app?.app_type === 'secret_judgement' && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setBatchDialogOpen(true)}
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
              className="min-h-[100px] w-full resize-none border-0 bg-transparent p-3 shadow-none focus-visible:ring-0"
              rows={4}
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

      {/* 批处理对话框 */}
      <Dialog open={batchDialogOpen} onOpenChange={setBatchDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>批处理数据库</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="db-config">选择数据库配置 *</Label>
              <select
                id="db-config"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                value={selectedDbConfigId || ''}
                onChange={(e) =>
                  setSelectedDbConfigId(
                    e.target.value ? Number(e.target.value) : null
                  )
                }
              >
                <option value="">
                  {databaseConfigs.length === 0
                    ? '暂无数据库配置，请先在后台管理中添加'
                    : '请选择数据库配置'}
                </option>
                {databaseConfigs.map((config) => (
                  <option key={config.id} value={config.id}>
                    {config.name} ({config.db_type})
                    {config.is_active ? '' : ' [未启用]'}
                  </option>
                ))}
              </select>
              {databaseConfigs.length === 0 && (
                <p className="text-xs text-muted-foreground">
                  提示：请前往{' '}
                  <a
                    href="/admin/database-configs"
                    target="_blank"
                    className="text-primary underline"
                  >
                    数据库管理
                  </a>{' '}
                  页面添加数据库配置
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="table-name">表名</Label>
              <input
                id="table-name"
                type="text"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                value={tableName}
                onChange={(e) => setTableName(e.target.value)}
                placeholder="test"
              />
            </div>
            {isBatchProcessing && (
              <div className="rounded-md border p-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>处理进度</span>
                    <span>
                      {batchProgress.current} / {batchProgress.total}
                    </span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                    <div
                      className="h-full bg-primary transition-all"
                      style={{
                        width: `${
                          (batchProgress.current / batchProgress.total) * 100
                        }%`
                      }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>成功: {batchProgress.success}</span>
                    <span>失败: {batchProgress.failed}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setBatchDialogOpen(false)}
              disabled={isBatchProcessing}
            >
              取消
            </Button>
            <Button
              onClick={handleBatchProcess}
              disabled={!selectedDbConfigId || isBatchProcessing}
            >
              {isBatchProcessing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  处理中...
                </>
              ) : (
                <>
                  <Play className="mr-2 h-4 w-4" />
                  开始批处理
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
