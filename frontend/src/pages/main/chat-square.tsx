import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Send,
  ArrowLeft,
  MoreHorizontal,
  Eraser,
  ChevronDown,
  Sparkles,
  Zap,
  Brain,
  Cpu,
  Bot,
  Loader2
} from 'lucide-react';
import { ChatMessage, type Message } from '@/components/chat/chat-message';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel
} from '@/components/ui/dropdown-menu';
import { getPublicModelConfigs } from '@/services/model-configs';
import type { ModelConfigPublic } from '@/types/model-config';

// 图标映射
const IconMap = {
  sparkles: Sparkles,
  zap: Zap,
  brain: Brain,
  cpu: Cpu,
  bot: Bot
};

// 带图标组件的模型配置接口
interface ModelWithIcon extends ModelConfigPublic {
  IconComponent: React.ComponentType<{ className?: string }>;
}

// 默认模型配置（当后端没有数据时使用）
const DEFAULT_MODELS: ModelConfigPublic[] = [
  {
    id: 0,
    name: 'GPT-3.5 Turbo',
    model_id: 'gpt-3.5-turbo',
    description: '快速且经济实惠',
    provider: 'OpenAI',
    icon: 'cpu',
    icon_color: 'text-blue-500',
    max_tokens: 16385
  }
];

// API 基础路径
const API_BASE = import.meta.env.VITE_API_URL || '/api';

export default function ChatSquarePage() {
  const navigate = useNavigate();
  const [models, setModels] = useState<ModelWithIcon[]>([]);
  const [selectedModel, setSelectedModel] = useState<ModelWithIcon | null>(
    null
  );
  const [loadingModels, setLoadingModels] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // 加载模型列表
  useEffect(() => {
    const fetchModels = async () => {
      setLoadingModels(true);
      try {
        let data = await getPublicModelConfigs();
        // 如果后端没有数据，使用默认模型
        if (!data || data.length === 0) {
          data = DEFAULT_MODELS;
        }
        // 为每个模型添加图标组件
        const modelsWithIcons: ModelWithIcon[] = data.map((m) => ({
          ...m,
          IconComponent: IconMap[m.icon] || Sparkles
        }));
        setModels(modelsWithIcons);
        // 设置默认选中第一个模型
        if (modelsWithIcons.length > 0) {
          setSelectedModel(modelsWithIcons[0]);
          setMessages([
            {
              id: '0',
              role: 'assistant',
              content: `你好！我是 **${modelsWithIcons[0].name}**，来自 ${modelsWithIcons[0].provider}。\n\n${modelsWithIcons[0].description}。我可以帮助你进行对话、回答问题、编写代码、创作内容等。\n\n请问有什么我可以帮你的吗？`,
              timestamp: Date.now()
            }
          ]);
        }
      } catch (error) {
        console.error('获取模型列表失败:', error);
        // 使用默认模型
        const defaultWithIcons: ModelWithIcon[] = DEFAULT_MODELS.map((m) => ({
          ...m,
          IconComponent: IconMap[m.icon] || Sparkles
        }));
        setModels(defaultWithIcons);
        if (defaultWithIcons.length > 0) {
          setSelectedModel(defaultWithIcons[0]);
          setMessages([
            {
              id: '0',
              role: 'assistant',
              content: `你好！我是 **${defaultWithIcons[0].name}**，来自 ${defaultWithIcons[0].provider}。\n\n请问有什么我可以帮你的吗？`,
              timestamp: Date.now()
            }
          ]);
        }
      } finally {
        setLoadingModels(false);
      }
    };

    fetchModels();
  }, []);

  useEffect(() => {
    // Auto scroll to bottom
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // 切换模型时更新欢迎消息
  const handleModelChange = (model: ModelWithIcon) => {
    setSelectedModel(model);
    setMessages([
      {
        id: '0',
        role: 'assistant',
        content: `你好！我是 **${model.name}**，来自 ${model.provider}。\n\n${model.description}。我可以帮助你进行对话、回答问题、编写代码、创作内容等。\n\n请问有什么我可以帮你的吗？`,
        timestamp: Date.now()
      }
    ]);
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading || !selectedModel) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: Date.now()
    };

    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    // 创建 AI 回复消息占位
    const aiMsgId = (Date.now() + 1).toString();
    setMessages((prev) => [
      ...prev,
      {
        id: aiMsgId,
        role: 'assistant',
        content: '',
        timestamp: Date.now()
      }
    ]);

    try {
      // 创建 AbortController 用于取消请求
      abortControllerRef.current = new AbortController();

      // 准备发送给 API 的消息（排除欢迎消息，只发送对话内容）
      const chatMessages = newMessages
        .filter((m) => m.id !== '0') // 排除欢迎消息
        .map((m) => ({
          role: m.role,
          content: m.content
        }));

      // 调用真实 API
      const response = await fetch(`${API_BASE}/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model_id: selectedModel.model_id,
          messages: chatMessages
        }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // 处理 SSE 流式响应
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No reader available');
      }

      let currentContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.type === 'token' && data.content) {
                currentContent += data.content;
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === aiMsgId
                      ? { ...msg, content: currentContent }
                      : msg
                  )
                );
              } else if (data.type === 'error') {
                throw new Error(data.message || '服务出现错误');
              }
            } catch (e) {
              // 忽略 JSON 解析错误（可能是不完整的数据）
              if (e instanceof SyntaxError) continue;
              throw e;
            }
          }
        }
      }

      // 如果没有收到任何内容，显示默认消息
      if (!currentContent) {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === aiMsgId
              ? { ...msg, content: '抱歉，我暂时无法回答这个问题。' }
              : msg
          )
        );
      }
    } catch (error) {
      console.error('Chat error:', error);

      // 检查是否是用户取消
      if (error instanceof Error && error.name === 'AbortError') {
        return;
      }

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
      abortControllerRef.current = null;
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const clearContext = () => {
    if (!selectedModel) return;

    // 取消正在进行的请求
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    setMessages([
      {
        id: '0',
        role: 'assistant',
        content: `对话已清除。\n\n你好！我是 **${selectedModel.name}**，来自 ${selectedModel.provider}。\n\n请问有什么我可以帮你的吗？`,
        timestamp: Date.now()
      }
    ]);
    setLoading(false);
  };

  // 加载中状态
  if (loadingModels) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">加载模型列表中...</p>
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
          <div className="flex items-center gap-3">
            <div>
              <h1 className="text-base font-semibold">对话广场</h1>
              <p className="text-xs text-muted-foreground">
                选择不同模型，体验多样对话
              </p>
            </div>
          </div>
        </div>

        {/* 更多操作 */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <MoreHorizontal className="h-5 w-5" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={clearContext}>
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
            {isLoading && messages[messages.length - 1]?.content === '' && (
              <div className="flex w-full gap-4 p-4">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md border shadow">
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                </div>
                <div className="flex items-center">
                  <span className="text-sm text-muted-foreground">
                    {selectedModel?.name} 正在思考...
                  </span>
                </div>
              </div>
            )}
            <div ref={scrollRef} />
          </div>
        </ScrollArea>
      </div>

      {/* Input Area */}
      <div className="bg-gradient-to-t from-background via-background to-transparent pt-6 pb-4 px-4">
        <div className="mx-auto max-w-3xl space-y-3">
          {/* 输入框容器 */}
          <div className="relative flex items-end gap-3 rounded-2xl border bg-muted/30 p-2 shadow-sm transition-all focus-within:bg-background focus-within:shadow-md focus-within:ring-2 focus-within:ring-ring/20">
            {/* 模型选择器 */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex h-10 items-center gap-1.5 rounded-xl bg-background px-3 border shadow-sm transition-colors hover:bg-accent">
                  {selectedModel && (
                    <>
                      <selectedModel.IconComponent
                        className={`h-4 w-4 ${selectedModel.icon_color}`}
                      />
                      <span className="text-sm font-medium hidden sm:inline">
                        {selectedModel.name}
                      </span>
                    </>
                  )}
                  <ChevronDown className="h-3.5 w-3.5 opacity-50" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-[300px]">
                <DropdownMenuLabel className="text-xs text-muted-foreground font-normal">
                  选择对话模型
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                {models.map((model) => (
                  <DropdownMenuItem
                    key={model.id}
                    onClick={() => handleModelChange(model)}
                    className={`flex items-center gap-3 p-2.5 cursor-pointer rounded-lg my-0.5 ${
                      selectedModel?.id === model.id
                        ? 'bg-primary/10 text-primary'
                        : ''
                    }`}
                  >
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted">
                      <model.IconComponent
                        className={`h-4 w-4 ${model.icon_color}`}
                      />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm">
                          {model.name}
                        </span>
                        <span className="text-[10px] text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                          {model.provider}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground truncate">
                        {model.description}
                      </p>
                    </div>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            {/* 输入框 */}
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入你的问题..."
              className="min-h-[40px] max-h-[200px] flex-1 resize-none border-0 bg-transparent px-2 py-2.5 text-sm shadow-none placeholder:text-muted-foreground/60 focus-visible:ring-0"
              rows={1}
            />

            {/* 发送按钮 */}
            <Button
              size="icon"
              onClick={handleSend}
              disabled={!input.trim() || isLoading || !selectedModel}
              className="h-10 w-10 shrink-0 rounded-xl"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>

          {/* 底部提示 */}
          <p className="text-center text-xs text-muted-foreground/70">
            内容由 AI 生成，请仔细甄别
          </p>
        </div>
      </div>
    </div>
  );
}
