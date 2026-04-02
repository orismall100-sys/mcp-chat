import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function TypingDots() {
  return (
    <div className="typing-dots">
      <span /><span /><span />
    </div>
  )
}

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [dark, setDark] = useState(false)
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    document.body.classList.toggle('dark', dark)
  }, [dark])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  function handleInputChange(e) {
    setInput(e.target.value)
    const ta = textareaRef.current
    ta.style.height = 'auto'
    ta.style.height = Math.min(ta.scrollHeight, 160) + 'px'
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  async function sendMessage() {
    const text = input.trim()
    if (!text || loading) return

    const userMsg = { role: 'user', content: text }
    const newMessages = [...messages, userMsg]
    setMessages(newMessages)
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
    setLoading(true)

    try {
      const history = messages.map(m => ({ role: m.role, content: m.content }))
      const res = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, history }),
      })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()
      setMessages([...newMessages, { role: 'assistant', content: data.response }])
    } catch (err) {
      setMessages([...newMessages, { role: 'assistant', content: `Error: ${err.message}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-layout">
      <header className="chat-header">
        <div className="chat-header-inner">
          <span className="chat-logo">🍞</span>
          <div>
            <div className="chat-title">Crumb &amp; Culture</div>
            <div className="chat-subtitle">HR Assistant</div>
          </div>
          <button className="dark-toggle" onClick={() => setDark(d => !d)}>
            {dark ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      <main className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <div className="chat-empty-icon">🍞</div>
            <p>Ask anything about our people.</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`message-row ${msg.role}`}>
            {msg.role === 'assistant' && (
              <div className="message-avatar">C</div>
            )}
            <div className="message-bubble">
              {msg.role === 'assistant'
                ? <ReactMarkdown>{msg.content}</ReactMarkdown>
                : msg.content
              }
            </div>
          </div>
        ))}

        {loading && (
          <div className="message-row assistant">
            <div className="message-avatar">C</div>
            <div className="message-bubble">
              <TypingDots />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </main>

      <footer className="chat-input-bar">
        <div className="chat-input-inner">
          <textarea
            ref={textareaRef}
            className="chat-textarea"
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask about employees..."
            disabled={loading}
            rows={1}
            autoFocus
          />
          <button
            className="chat-send-btn"
            onClick={sendMessage}
            disabled={loading || !input.trim()}
          >
            ↑
          </button>
        </div>
        <p className="chat-hint">Press Enter to send · Shift+Enter for new line</p>
      </footer>
    </div>
  )
}
