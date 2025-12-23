import { useState, useRef, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, ArrowLeft, MoreHorizontal, Eraser } from 'lucide-react';
import { ChatMessage, type Message } from '@/components/chat/chat-message';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';
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

  if (isSensitive) {
    content += `### ⚠️ **涉密文件**\n\n`;
  } else {
    content += `### ✅ **非涉密文件**\n\n`;
  }

  content += `- **置信度**: ${confidence}%\n`;
  content += `- **证据链**:\n\n${evidence}\n`;

  return content;
}

// Mock App Data
const MOCK_APPS = {
  '1': { name: '周报生成助手', description: '自动生成周报' },
  '2': {
    name: '涉密研判助手',
    description: '研判文件内容是否涉密，给出涉密研判证据链与具体建议。'
  },
  '3': { name: '营销文案大师', description: '生成爆款文案' },
  '4': { name: 'SQL 生成器', description: '自然语言转 SQL' },
  '5': { name: '英语口语陪练', description: '纠正发音语法' },
  '6': { name: '法律咨询助手', description: '法律问题解答' }
};

export default function AppChatPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content: `你好！我是${
        MOCK_APPS[id as keyof typeof MOCK_APPS]?.name || '智能助手'
      }。\n请问有什么我可以帮你的吗？`,
      timestamp: Date.now()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const app = MOCK_APPS[id as keyof typeof MOCK_APPS];

  useEffect(() => {
    // Auto scroll to bottom
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: Date.now()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    // Special handling for "涉密研判助手" (ID: 2) - 使用 LangGraph 流式 API
    if (id === '2') {
      try {
        // LangGraph 流式 API 端点
        const response = await fetch('http://localhost:5001/agent/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            input: {
              doc_title: 'User Input',
              doc_content: userMsg.content,
              current_node: 'start_node',
              is_sensitive: false,
              evidence: '',
              secret_analysis_result: {},
              public_analysis_result: {},
              confidence: 0
            }
          })
        });

        if (!response.ok) {
          throw new Error(`API Error: ${response.statusText}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        // Create a placeholder message for AI response
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

        let fullContent = '';
        let buffer = '';
        let finalResult: Record<string, unknown> | null = null;

        while (reader) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const jsonStr = line.slice(6).trim();
                if (!jsonStr) continue;
                const event = JSON.parse(jsonStr);

                // LangGraph 流式输出格式: 每个节点返回 { "node_name": { ...state... } }
                // 或者 LangServe 格式: { "event": "data", "data": {...} }

                if (event.event === 'data' && event.data) {
                  // LangServe 流式格式
                  const nodeData = event.data;
                  for (const [nodeName, nodeOutput] of Object.entries(
                    nodeData
                  )) {
                    const output = nodeOutput as Record<string, unknown>;

                    // 更新显示内容
                    fullContent = formatNodeOutput(
                      nodeName,
                      output,
                      fullContent
                    );
                    setMessages((prev) =>
                      prev.map((msg) =>
                        msg.id === aiMsgId
                          ? { ...msg, content: fullContent }
                          : msg
                      )
                    );

                    // 保存最终结果
                    if (
                      nodeName === 'agent_decision' ||
                      output.is_sensitive !== undefined
                    ) {
                      finalResult = output;
                    }
                  }
                } else if (event.event === 'end') {
                  // 流结束
                  if (finalResult) {
                    fullContent = formatFinalResult(finalResult, fullContent);
                    setMessages((prev) =>
                      prev.map((msg) =>
                        msg.id === aiMsgId
                          ? { ...msg, content: fullContent }
                          : msg
                      )
                    );
                  }
                } else if (!event.event) {
                  // 直接的节点输出格式 (不带 event 包装)
                  for (const [nodeName, nodeOutput] of Object.entries(event)) {
                    const output = nodeOutput as Record<string, unknown>;

                    fullContent = formatNodeOutput(
                      nodeName,
                      output,
                      fullContent
                    );
                    setMessages((prev) =>
                      prev.map((msg) =>
                        msg.id === aiMsgId
                          ? { ...msg, content: fullContent }
                          : msg
                      )
                    );

                    if (output.is_sensitive !== undefined) {
                      finalResult = output;
                    }
                  }
                }
              } catch (e) {
                console.error('Error parsing SSE data:', e, 'Line:', line);
              }
            }
          }
        }

        // 确保最终结果显示
        if (finalResult && !fullContent.includes('## 最终判定')) {
          fullContent = formatFinalResult(finalResult, fullContent);
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === aiMsgId ? { ...msg, content: fullContent } : msg
            )
          );
        }
      } catch (error) {
        console.error(error);
        setMessages((prev) => [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: '抱歉，服务出现错误，请稍后再试。',
            timestamp: Date.now()
          }
        ]);
      } finally {
        setLoading(false);
      }
      return;
    }

    // Mock API Call for other apps
    setTimeout(() => {
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `这是针对 "${userMsg.content}" 的模拟回复。\n\n**支持 Markdown 语法**：\n- 列表项 1\n- 列表项 2\n\n\`\`\`javascript\nconsole.log("Code Block");\n\`\`\``,
        timestamp: Date.now()
      };
      setMessages((prev) => [...prev, aiMsg]);
      setLoading(false);
    }, 1000);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!app) {
    return <div>应用不存在</div>;
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
