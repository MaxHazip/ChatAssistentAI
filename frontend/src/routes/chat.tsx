import { useState, useRef, useEffect, useCallback } from 'react'
import { createFileRoute } from '@tanstack/react-router'

type BotStatus = 'thinking' | 'clarifying' | 'human' | 'ready'

type Message = {
  id: string
  text: string
  sender: 'user' | 'bot'
  timestamp: string
  status?: BotStatus
  isLoading?: boolean
}

export const Route = createFileRoute('/chat')({
  component: ChatPage,
})

const STATUS_TEXTS: Record<BotStatus, string> = {
  thinking: '🤔 Готовлю ответ...',
  clarifying: '❓ Готовлю уточняющий вопрос...',
  human: '👨‍💼 Подключаю специалиста...',
  ready: '✅ Ответ готов'
}

function ChatPage() {
  const [isVisible, setIsVisible] = useState(false)
  const [isMounted, setIsMounted] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', text: 'Привет! Задай вопрос.', sender: 'bot', timestamp: 'Сейчас' },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const [pos, setPos] = useState({ x: window.innerWidth - 420, y: window.innerHeight - 700 })
  const [isDragging, setIsDragging] = useState(false)
  const dragOffset = useRef({ x: 0, y: 0 })

  useEffect(() => {
    setIsMounted(true)
    const timer = setTimeout(() => setIsVisible(true), 50)
    return () => clearTimeout(timer)
  }, [])

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    setIsDragging(true)
    dragOffset.current = {
      x: e.clientX - pos.x,
      y: e.clientY - pos.y,
    }
  }, [pos.x, pos.y])

  useEffect(() => {
    if (!isDragging) return

    const handleMouseMove = (e: MouseEvent) => {
      setPos({
        x: e.clientX - dragOffset.current.x,
        y: e.clientY - dragOffset.current.y,
      })
    }

    const handleMouseUp = () => setIsDragging(false)

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseup', handleMouseUp)

    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMsg: Message = {
      id: Date.now().toString(),
      text: input.trim(),
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }

    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setIsLoading(true)

    const loadingMsgId = (Date.now() + 1).toString()
    setMessages((prev) => [
      ...prev,
      {
        id: loadingMsgId,
        text: '',
        sender: 'bot',
        timestamp: 'Сейчас',
        status: 'thinking',
        isLoading: true
      }
    ])

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/send_answer/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMsg.text }),
      })
      if (!response.ok) throw new Error('Ошибка сервера')
      const data = await response.json()

      setMessages((prev) => 
        prev.map(msg => 
          msg.id === loadingMsgId 
            ? {
                ...msg,
                text: data.answer || 'Ответ получен.',
                status: data.status || 'ready',
                isLoading: false
              }
            : msg
        )
      )
    } catch (error) {
      setMessages((prev) => 
        prev.map(msg => 
          msg.id === loadingMsgId 
            ? {
                ...msg,
                text: 'Ошибка соединения.',
                status: 'ready',
                isLoading: false
              }
            : msg
        )
      )
    } finally {
      setIsLoading(false)
    }
  }

  if (!isMounted) return null

  return (
    <>
      {!isVisible && (
        <button
          onClick={() => setIsVisible(true)}
          className="fixed bottom-6 right-6 bg-[#22c55e] text-white p-4 rounded-full shadow-lg hover:bg-[#16a34a] transition-colors duration-200 z-50"
          aria-label="Открыть чат"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </button>
      )}

      <div
        className={`w-full max-w-[400px] bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col h-[650px] transition-all duration-300 ease-out transform ${
          isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8 pointer-events-none'
        }`}
        style={{ position: 'fixed', left: pos.x, top: pos.y, zIndex: 50 }}
      >
        <div
          className={`bg-[#1a1a1a] text-white px-4 py-3 flex items-center justify-between select-none ${
            isDragging ? 'cursor-grabbing' : 'cursor-grab'
          }`}
          onMouseDown={handleMouseDown}
        >
          <div className="flex items-center gap-3">
            <button
              onClick={(e) => { e.stopPropagation(); setIsVisible(false); }}
              className="text-gray-400 hover:text-white transition-colors p-1 rounded"
              aria-label="Закрыть чат"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
            <h2 className="font-medium text-base tracking-wide">Чат бот</h2>
          </div>
          <div className="w-6" />
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-white">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
              <span className="text-[10px] text-gray-400 mb-1 px-1">{msg.timestamp}</span>
              <div className={`flex items-end gap-2 max-w-[85%] ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                {msg.sender === 'bot' && <div className="w-8 h-8 rounded-full bg-gray-200 flex-shrink-0" />}
                <div
                  className={`px-4 py-2.5 text-sm leading-relaxed ${
                    msg.sender === 'user'
                      ? 'bg-[#e8e8e8] text-gray-800 rounded-2xl rounded-br-md'
                      : 'bg-[#222222] text-white rounded-2xl rounded-bl-md'
                  }`}
                >
                  {msg.isLoading && msg.status && (
                    <div className="flex items-center gap-2 text-sm text-gray-300 mb-1">
                      <span className="animate-pulse">●</span>
                      <span>{STATUS_TEXTS[msg.status]}</span>
                    </div>
                  )}
                  {msg.text && <p>{msg.text}</p>}
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 border-t border-gray-100 bg-white flex gap-2 items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Введите сообщение..."
            disabled={isLoading}
            className="flex-1 px-4 py-2.5 border border-gray-200 rounded-full text-sm bg-gray-50 text-gray-900 focus:outline-none focus:ring-2 focus:ring-green-500/20 focus:border-green-500 transition-all placeholder:text-gray-400 disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="bg-[#22c55e] hover:bg-[#16a34a] disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-5 py-2.5 rounded-full text-sm font-medium transition-all shadow-sm active:scale-95 min-w-[90px]"
          >
            {isLoading ? '...' : 'Отправить'}
          </button>
        </div>
      </div>
    </>
  )
}