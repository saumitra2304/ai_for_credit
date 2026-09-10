import { memo, useMemo } from 'react'
import { motion } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Bot, User } from 'lucide-react'
import { cn } from '@/lib/utils'
import { formatChatMarkdown } from '@/lib/formatChatMarkdown'
import { calloutTone, cellTone, headingTone } from '@/lib/markdownTone'

function Heading({ as: Tag, baseClass, children }) {
  const tone = headingTone(children)
  return (
    <Tag className={cn(baseClass, tone && `markdown-h-${tone}`)}>
      {children}
    </Tag>
  )
}

const markdownComponents = {
  h1: ({ children }) => (
    <Heading as="h1" baseClass="markdown-h1">
      {children}
    </Heading>
  ),
  h2: ({ children }) => (
    <Heading as="h2" baseClass="markdown-h2">
      {children}
    </Heading>
  ),
  h3: ({ children }) => (
    <Heading as="h3" baseClass="markdown-h3">
      {children}
    </Heading>
  ),
  h4: ({ children }) => (
    <Heading as="h4" baseClass="markdown-h4">
      {children}
    </Heading>
  ),
  p: ({ children }) => <p className="markdown-p">{children}</p>,
  ul: ({ children }) => <ul className="markdown-ul">{children}</ul>,
  ol: ({ children }) => <ol className="markdown-ol">{children}</ol>,
  li: ({ children }) => <li className="markdown-li">{children}</li>,
  hr: () => <hr className="markdown-hr" />,
  strong: ({ children }) => {
    const tone = calloutTone(children)
    if (tone) {
      return <strong className={cn('markdown-callout', `markdown-callout-${tone}`)}>{children}</strong>
    }
    return <strong className="markdown-strong">{children}</strong>
  },
  em: ({ children }) => <em className="markdown-em">{children}</em>,
  blockquote: ({ children }) => <blockquote className="markdown-quote">{children}</blockquote>,
  a: ({ href, children }) => (
    <a href={href} target="_blank" rel="noreferrer noopener" className="markdown-a">
      {children}
    </a>
  ),
  pre: ({ children }) => <pre className="markdown-pre">{children}</pre>,
  code: ({ className, children }) => {
    const block = Boolean(className)
    if (block) {
      return <code className={cn('markdown-code-block', className)}>{children}</code>
    }
    return <code className="markdown-code">{children}</code>
  },
  table: ({ children }) => (
    <div className="markdown-table-wrap">
      <table>{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead>{children}</thead>,
  tbody: ({ children }) => <tbody>{children}</tbody>,
  tr: ({ children }) => <tr>{children}</tr>,
  th: ({ children }) => <th>{children}</th>,
  td: ({ children, style }) => {
    const tone = cellTone(children)
    return (
      <td
        style={style}
        className={cn('markdown-td', tone === 'neg' && 'markdown-td-neg', tone === 'muted' && 'markdown-td-muted')}
      >
        {children}
      </td>
    )
  },
}

export const ChatMessage = memo(function ChatMessage({ role, content, isStreaming }) {
  const isUser = role === 'user'
  const rendered = useMemo(
    () => (isUser ? content : formatChatMarkdown(content ?? '')),
    [isUser, content]
  )

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className={cn('w-full', isUser ? 'bg-muted/20' : 'bg-transparent')}
      style={{ overflowAnchor: isStreaming ? 'none' : 'auto' }}
    >
      <div className="chat-content-width flex gap-3 py-4 sm:gap-4 sm:py-5">
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
            {isUser ? 'You' : 'Kuber'}
          </p>
          <div className="markdown-body text-[15px] leading-relaxed text-foreground/95">
            {isUser ? (
              <p className="whitespace-pre-wrap">{rendered}</p>
            ) : (
              <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                {rendered}
              </ReactMarkdown>
            )}
            {isStreaming && (
              <span className="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-primary align-middle" />
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
})

export function ChatTurn({ turn, streamingMessageId }) {
  return (
    <section className="border-b border-border/15 last:border-b-0">
      {turn.user && !turn.user.hidden && (
        <ChatMessage role="user" content={turn.user.content} />
      )}
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
