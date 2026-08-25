import { useCallback, useEffect, useRef, useState } from 'react'

const BOTTOM_THRESHOLD = 120

export function useChatScroll(scrollContainerRef, contentRef) {
  const [showScrollButton, setShowScrollButton] = useState(false)
  const autoScrollEnabledRef = useRef(true)

  const isNearBottom = useCallback(() => {
    const el = scrollContainerRef.current
    if (!el) return true
    return el.scrollHeight - el.scrollTop - el.clientHeight <= BOTTOM_THRESHOLD
  }, [scrollContainerRef])

  const scrollToBottom = useCallback(
    (behavior = 'auto') => {
      const el = scrollContainerRef.current
      if (!el) return
      el.scrollTo({ top: el.scrollHeight, behavior })
    },
    [scrollContainerRef]
  )

  const enableAutoScroll = useCallback(() => {
    autoScrollEnabledRef.current = true
    setShowScrollButton(false)
  }, [])

  const disableAutoScroll = useCallback(() => {
    autoScrollEnabledRef.current = false
    setShowScrollButton(true)
  }, [])

  const jumpToLatest = useCallback(() => {
    enableAutoScroll()
    scrollToBottom('smooth')
  }, [enableAutoScroll, scrollToBottom])

  useEffect(() => {
    const el = scrollContainerRef.current
    if (!el) return

    const onScroll = () => {
      const near = isNearBottom()
      if (!near) {
        autoScrollEnabledRef.current = false
        setShowScrollButton(true)
        return
      }
      if (autoScrollEnabledRef.current) {
        setShowScrollButton(false)
      }
    }

    const onWheel = (event) => {
      if (event.deltaY < 0) {
        disableAutoScroll()
      }
    }

    const onTouchStart = () => {
      if (!isNearBottom()) disableAutoScroll()
    }

    el.addEventListener('scroll', onScroll, { passive: true })
    el.addEventListener('wheel', onWheel, { passive: true })
    el.addEventListener('touchstart', onTouchStart, { passive: true })

    return () => {
      el.removeEventListener('scroll', onScroll)
      el.removeEventListener('wheel', onWheel)
      el.removeEventListener('touchstart', onTouchStart)
    }
  }, [scrollContainerRef, isNearBottom, disableAutoScroll])

  useEffect(() => {
    const content = contentRef.current
    if (!content) return

    const observer = new ResizeObserver(() => {
      if (!autoScrollEnabledRef.current) return
      requestAnimationFrame(() => scrollToBottom('auto'))
    })

    observer.observe(content)
    return () => observer.disconnect()
  }, [contentRef, scrollToBottom])

  return {
    showScrollButton,
    scrollToBottom,
    enableAutoScroll,
    jumpToLatest,
  }
}
