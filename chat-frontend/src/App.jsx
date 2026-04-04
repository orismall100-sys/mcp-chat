import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { sendChatMessage } from './api'
import './App.css'

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
  const abortControllerRef = useRef(null)

  useEffect(() => {
    document.body.classList.toggle('dark', dark)
  }, [dark])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  function handleInputChange(e) {
    setInput(e.target.value)
    const textArea = textareaRef.current
    textArea.style.height = 'auto'
    textArea.style.height = Math.min(textArea.scrollHeight, 160) + 'px'
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  function stopMessage() {
    abortControllerRef.current?.abort()
  }

  async function sendMessage() {
    const text = input.trim()
    if (!text || loading) return

    const userMessage = { role: 'user', content: text, id: Date.now() }
    const newMessages = [...messages, userMessage]
    setMessages(newMessages)
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
    setLoading(true)

    abortControllerRef.current = new AbortController()

    try {
      const history = messages.map(message => ({ role: message.role, content: message.content }))
      const response = await sendChatMessage(text, history, abortControllerRef.current.signal)
      setMessages([...newMessages, { role: 'assistant', content: response, id: Date.now() }])
    } catch (err) {
      if (err.name === 'AbortError') {
        setMessages([...newMessages, { role: 'assistant', content: 'Response stopped.', id: Date.now() }])
      } else {
        setMessages([...newMessages, { role: 'assistant', content: `Error: ${err.message}`, id: Date.now() }])
      }
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
            <div className="chat-subtitle">Data Assistant</div>
          </div>
          <button className="dark-toggle" onClick={() => setDark(dark => !dark)}>
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

        {messages.map((message) => (
          <div key={message.id} className={`message-row ${message.role}`}>
            {message.role === 'assistant' && (
              <div className="message-avatar">C&C</div>
            )}
            <div className="message-bubble">
              {message.role === 'assistant'
                ? <ReactMarkdown>{message.content}</ReactMarkdown>
                : message.content
              }
            </div>
          </div>
        ))}

        {loading && (
          <div className="message-row assistant">
            <div className="message-avatar">C&C</div>
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
            rows={1}
            autoFocus
          />
          <button
            className="chat-send-btn"
            onClick={loading ? stopMessage : sendMessage}
            disabled={!loading && !input.trim()}
          >
            {loading ? '■' : '↑'}
          </button>
        </div>
        <p className="chat-hint">Press Enter to send · Shift+Enter for new line</p>
      </footer>
    </div>
  )
}
