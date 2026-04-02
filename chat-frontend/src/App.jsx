import { useState, useRef, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function sendMessage(e) {
    e.preventDefault()
    const text = input.trim()
    if (!text || loading) return

    const userMsg = { role: 'user', content: text }
    const newMessages = [...messages, userMsg]
    setMessages(newMessages)
    setInput('')
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
    <div className="container py-4" style={{ maxWidth: 720 }}>
      <h4 className="mb-4">HR Assistant — Crumb &amp; Culture</h4>

      <div
        className="border rounded p-3 mb-3 bg-light"
        style={{ height: 500, overflowY: 'auto' }}
      >
        {messages.length === 0 && (
          <p className="text-muted text-center mt-5">
            Ask anything about the people data.
          </p>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`d-flex mb-3 ${msg.role === 'user' ? 'justify-content-end' : 'justify-content-start'}`}
          >
            <div
              className={`p-2 px-3 rounded-3 ${msg.role === 'user' ? 'bg-primary text-white' : 'bg-white border'}`}
              style={{ maxWidth: '80%', whiteSpace: 'pre-wrap' }}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="d-flex justify-content-start mb-3">
            <div className="p-2 px-3 rounded-3 bg-white border text-muted fst-italic">
              Thinking...
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <form onSubmit={sendMessage} className="d-flex gap-2">
        <input
          className="form-control"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask about employees..."
          disabled={loading}
          autoFocus
        />
        <button
          className="btn btn-primary"
          type="submit"
          disabled={loading || !input.trim()}
        >
          Send
        </button>
      </form>
    </div>
  )
}
