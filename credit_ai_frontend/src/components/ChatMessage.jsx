import { motion } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Bot, User } from 'lucide-react'
import { cn } from '@/lib/utils'

export function ChatMessage({ role, content, isStreaming }) {
  const isUser = role === 'user'

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.2 }}
      className={cn('w-full', isUser ? 'bg-muted/20' : 'bg-transparent')}
      style={{ overflowAnchor: isStreaming ? 'none' : 'auto' }}
    >
      <div className="chat-content-width flex gap-4 py-5">
        <div
          className={cn(
            'mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-sm',
            isUser ? 'bg-primary/90 text-primary-foreground' : 'bg-emerald-500/15 text-emerald-400'
          )}
        >
          {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
        </div>

        <div className="min-w-0 flex-1 pt-0.5">
          <p className="mb-2 text-xs font-medium text-muted-foreground">
            {isUser ? 'You' : 'Kuber AI'}
          </p>
          <div className="markdown-body text-[15px] leading-relaxed text-foreground/95">
            {isUser ? (
              <p className="whitespace-pre-wrap">{content}</p>
            ) : (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
            )}
            {isStreaming && (
              <span className="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-primary align-middle" />
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export function ChatTurn({ turn, streamingMessageId }) {
  return (
    <section className="border-b border-border/15 last:border-b-0">
      {turn.user && <ChatMessage role="user" content={turn.user.content} />}
      {turn.assistant && (
        <ChatMessage
          role="assistant"
          content={turn.assistant.content}
          isStreaming={turn.assistant.id === streamingMessageId}
        />
      )}
    </section>
  )
}
