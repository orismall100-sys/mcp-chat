const API_URL = import.meta.env.VITE_API_URL

export async function sendChatMessage(message, history, signal) {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
    signal,
  })
  if (!res.ok) throw new Error('Something went wrong. Please try again.')
  const data = await res.json()
  return data.response
}
