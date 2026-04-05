import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import api from '../lib/api'
import { ArrowLeft, Send, Loader2, GitBranch, Code, BookOpen } from 'lucide-react'

export default function RepoPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [messages, setMessages] = useState<{role: string, content: string}[]>([])
  const [input, setInput] = useState('')
  const [isAsking, setIsAsking] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'files' | 'chat'>('overview')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { data: repo } = useQuery({
    queryKey: ['repo', id],
    queryFn: () => api.get(`/repos/${id}`).then(r => r.data),
  })

  const { data: analyses = [] } = useQuery({
    queryKey: ['analyses', id],
    queryFn: () => api.get(`/repos/${id}/analyses`).then(r => r.data),
    enabled: !!id,
  })

  const { data: files = [] } = useQuery({
    queryKey: ['files', id],
    queryFn: () => api.get(`/repos/${id}/files`).then(r => r.data),
    enabled: !!id,
  })

  const analysis = analyses[0]

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleAsk() {
    if (!input.trim() || isAsking) return
    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setIsAsking(true)

    try {
      const res = await api.post(`/repos/${id}/chat`, { message: userMsg, history: messages })
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.response }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, something went wrong.' }])
    } finally {
      setIsAsking(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col">
      <header className="border-b border-slate-800 px-6 py-4 flex items-center gap-4">
        <button onClick={() => navigate('/')} className="text-slate-400 hover:text-white transition">
          <ArrowLeft size={20} />
        </button>
        <div className="flex items-center gap-2">
          <GitBranch className="text-sky-400" size={20} />
          <span className="text-white font-semibold">{repo?.full_name}</span>
        </div>
        <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full">Ready</span>
      </header>

      <div className="flex border-b border-slate-800 px-6">
        {[
          { key: 'overview', label: 'Overview', icon: BookOpen },
          { key: 'files', label: 'Files', icon: Code },
          { key: 'chat', label: 'Ask AI', icon: Send },
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key as any)}
            className={`flex items-center gap-2 px-4 py-3 text-sm border-b-2 transition ${
              activeTab === key
                ? 'border-sky-500 text-sky-400'
                : 'border-transparent text-slate-400 hover:text-white'
            }`}
          >
            <Icon size={14} /> {label}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-auto">
        {activeTab === 'overview' && analysis && (
          <div className="max-w-3xl mx-auto px-6 py-8 space-y-6">
            <div className="bg-slate-800 rounded-xl p-6">
              <h2 className="text-white font-semibold mb-3">Architecture</h2>
              <p className="text-slate-300 leading-relaxed">{analysis.architecture_summary}</p>
            </div>
            {analysis.tech_stack?.length > 0 && (
              <div className="bg-slate-800 rounded-xl p-6">
                <h2 className="text-white font-semibold mb-3">Tech Stack</h2>
                <div className="flex flex-wrap gap-2">
                  {analysis.tech_stack.map((tech: string) => (
                    <span key={tech} className="bg-sky-500/20 text-sky-300 text-sm px-3 py-1 rounded-full">{tech}</span>
                  ))}
                </div>
              </div>
            )}
            {analysis.onboarding_guide && (
              <div className="bg-slate-800 rounded-xl p-6">
                <h2 className="text-white font-semibold mb-3">Onboarding Guide</h2>
                <p className="text-slate-300 leading-relaxed">{analysis.onboarding_guide}</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'files' && (
          <div className="max-w-3xl mx-auto px-6 py-8">
            <div className="space-y-2">
              {files.map((file: any) => (
                <div key={file.id} className="bg-slate-800 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-1">
                    <Code size={14} className="text-sky-400 flex-shrink-0" />
                    <span className="text-slate-300 text-sm font-mono truncate">{file.path}</span>
                  </div>
                  {file.ai_summary && <p className="text-slate-400 text-sm pl-5">{file.ai_summary}</p>}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'chat' && (
          <div className="flex flex-col h-full max-w-3xl mx-auto w-full px-6">
            <div className="flex-1 py-6 space-y-4 overflow-auto">
              {messages.length === 0 && (
                <div className="text-center py-20 text-slate-500">
                  <Send size={32} className="mx-auto mb-3 opacity-30" />
                  <p>Ask anything about this codebase</p>
                </div>
              )}
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-xl px-4 py-3 rounded-xl text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-sky-500 text-white'
                      : 'bg-slate-800 text-slate-200'
                  }`}>
                    {msg.content}
                  </div>
                </div>
              ))}
              {isAsking && (
                <div className="flex justify-start">
                  <div className="bg-slate-800 px-4 py-3 rounded-xl">
                    <Loader2 size={16} className="animate-spin text-sky-400" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            <div className="flex gap-3 py-4 border-t border-slate-800">
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleAsk()}
                placeholder="Ask about the codebase..."
                className="flex-1 bg-slate-800 text-white rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-sky-500"
              />
              <button
                onClick={handleAsk}
                disabled={!input.trim() || isAsking}
                className="bg-sky-500 hover:bg-sky-600 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition"
              >
                <Send size={16} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
