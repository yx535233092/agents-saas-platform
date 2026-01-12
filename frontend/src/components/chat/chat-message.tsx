// import { Avatar } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';
import { User, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className="flex w-full gap-3 p-3 text-sm">
      {/* 头像 */}
      <div
        className={cn(
          'flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-lg shadow-sm',
          isUser
            ? 'bg-blue-500 text-white'
            : 'border bg-background text-primary'
        )}
      >
        {isUser ? (
          <User className="h-4 w-4" />
        ) : (
          <Bot className="h-4 w-4" />
        )}
      </div>

      {/* 消息内容 */}
      <div className="flex-1 space-y-1">
        <div
          className={cn(
            'inline-block max-w-[85%] rounded-xl px-4 py-2.5',
            isUser
              ? 'bg-blue-500 text-white'
              : 'border bg-muted/30'
          )}
        >
          <div className="prose break-words dark:prose-invert prose-p:leading-relaxed prose-pre:p-0">
            {isUser ? (
              <div className="whitespace-pre-wrap text-white">{message.content}</div>
            ) : (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

