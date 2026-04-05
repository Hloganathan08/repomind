import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import api from '../lib/api'
import { GitBranch, Plus, LogOut, Star, Loader2 } from 'lucide-react'

export default function DashboardPage() {
  const [repoInput, setRepoInput] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: repos = [], isLoading } = useQuery({
    queryKey: ['repos'],
    queryFn: () => api.get('/repos').then(r => r.data),
    refetchInterval: 5000,
  })

  const addRepo = useMutation({
    mutationFn: (full_name: string) => api.post('/repos', { full_name }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['repos'] })
      setRepoInput('')
      setError('')
    },
    onError: (err: any) => setError(err.response?.data?.detail || 'Failed to add repo'),
  })

  const analyzeRepo = useMutation({
    mutationFn: (id: string) => api.post(`/repos/${id}/analyze`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['repos'] }),
  })

  function handleLogout() {
    localStorage.removeItem('token')
    navigate('/login')
  }

  const statusColor: Record<string, string> = {
    pending: 'text-slate-400',
    analyzing: 'text-yellow-400',
    ready: 'text-green-400',
    error: 'text-red-400',
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <header className="border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <GitBranch className="text-sky-400" size={24} />
          <span className="text-white font-bold text-xl">RepoMind</span>
        </div>
        <button onClick={handleLogout} className="flex items-center gap-1 text-slate-400 hover:text-white transition">
          <LogOut size={16} /> Sign out
        </button>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-10">
        <h1 className="text-2xl font-bold text-white mb-2">Your Repositories</h1>
        <p className="text-slate-400 mb-8">Add a GitHub repo to get AI-powered codebase intelligence.</p>

        <div className="flex gap-3 mb-4">
          <input
            value={repoInput}
            onChange={e => setRepoInput(e.target.value)}
            placeholder="owner/repo (e.g. facebook/react)"
            className="flex-1 bg-slate-800 text-white rounded-lg px-4 py-2 outline-none focus:ring-2 focus:ring-sky-500"
            onKeyDown={e => e.key === 'Enter' && addRepo.mutate(repoInput)}
          />
          <button
            onClick={() => addRepo.mutate(repoInput)}
            disabled={!repoInput || addRepo.isPending}
            className="bg-sky-500 hover:bg-sky-600 disabled:opacity-50 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition"
          >
            {addRepo.isPending ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
            Add Repo
          </button>
        </div>
        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}

        {isLoading ? (
          <div className="flex justify-center py-20"><Loader2 className="animate-spin text-sky-400" size={32} /></div>
        ) : repos.length === 0 ? (
          <div className="text-center py-20 text-slate-500">No repositories yet. Add one above.</div>
        ) : (
          <div className="space-y-3">
            {repos.map((repo: any) => (
              <div key={repo.id} className="bg-slate-800 rounded-xl p-5 flex items-center justify-between hover:bg-slate-750 transition">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="text-white font-semibold truncate">{repo.full_name}</h3>
                    <span className={`text-xs font-medium ${statusColor[repo.status] || 'text-slate-400'}`}>
                      {repo.status === 'analyzing' ? '⟳ Analyzing...' : repo.status}
                    </span>
                  </div>
                  <p className="text-slate-400 text-sm truncate">{repo.description || 'No description'}</p>
                  <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                    {repo.language && <span>{repo.language}</span>}
                    <span className="flex items-center gap-1"><Star size={10} /> {repo.stars.toLocaleString()}</span>
                    {repo.file_count > 0 && <span>{repo.file_count} files analyzed</span>}
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  {repo.status === 'pending' && (
                    <button
                      onClick={() => analyzeRepo.mutate(repo.id)}
                      className="bg-sky-500 hover:bg-sky-600 text-white text-sm px-3 py-1.5 rounded-lg transition"
                    >
                      Analyze
                    </button>
                  )}
                  {repo.status === 'ready' && (
                    <button
                      onClick={() => navigate(`/repo/${repo.id}`)}
                      className="bg-green-500 hover:bg-green-600 text-white text-sm px-3 py-1.5 rounded-lg transition"
                    >
                      Explore
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
