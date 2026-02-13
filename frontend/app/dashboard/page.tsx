'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'
import { 
  Play, 
  Loader2, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  FileText, 
  Search,
  Edit,
  Shield,
  CheckSquare,
  Sparkles
} from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface TaskStatus {
  id: string
  status: string
  title: string
}

interface PipelineResponse {
  pipeline_id: string
  topic: string
  status: string
  tasks: Record<string, TaskStatus>
}

export default function Dashboard() {
  const router = useRouter()
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)
  const [pipeline, setPipeline] = useState<PipelineResponse | null>(null)
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const runPipeline = async () => {
    if (!topic.trim()) {
      setError('Please enter a topic')
      return
    }

    setLoading(true)
    setError(null)
    setPipeline(null)
    setResults(null)

    try {
      const response = await axios.post<PipelineResponse>(`${API_URL}/api/pipeline/run`, {
        topic: topic.trim()
      })
      
      setPipeline(response.data)
      
      // Poll for results
      pollResults(response.data.pipeline_id)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to run pipeline')
      setLoading(false)
    }
  }

  const pollResults = async (pipelineId: string) => {
    const maxAttempts = 60
    let attempts = 0

    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`${API_URL}/api/pipeline/${pipelineId}/results`)
        
        if (response.data.results && Object.keys(response.data.results).length > 0) {
          setResults(response.data.results)
          setLoading(false)
          clearInterval(interval)
        } else if (attempts >= maxAttempts) {
          setLoading(false)
          clearInterval(interval)
        }
        
        attempts++
      } catch (err) {
        console.error('Error polling results:', err)
        attempts++
        if (attempts >= maxAttempts) {
          setLoading(false)
          clearInterval(interval)
        }
      }
    }, 2000)
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-success" />
      case 'failed':
        return <XCircle className="h-5 w-5 text-error" />
      case 'in_progress':
        return <Loader2 className="h-5 w-5 text-accent animate-spin" />
      default:
        return <Clock className="h-5 w-5 text-text-muted" />
    }
  }

  const getTaskIcon = (taskName: string) => {
    const icons: Record<string, React.ReactNode> = {
      research: <Search className="h-5 w-5" />,
      analysis: <FileText className="h-5 w-5" />,
      writing: <Edit className="h-5 w-5" />,
      seo: <Shield className="h-5 w-5" />,
      quality: <CheckSquare className="h-5 w-5" />,
    }
    return icons[taskName] || <Sparkles className="h-5 w-5" />
  }

  return (
    <div className="min-h-screen bg-surface">
      {/* Header */}
      <header className="border-b border-border bg-surface-light">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Sparkles className="h-6 w-6 text-accent" />
              <span className="text-xl font-semibold text-text-primary">OpenClawAgents</span>
            </div>
            <button
              onClick={() => router.push('/')}
              className="text-text-secondary hover:text-text-primary transition-colors"
            >
              Back to Home
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Pipeline Input */}
        <div className="bg-surface-light border border-border rounded-xl p-8 mb-8">
          <h1 className="text-3xl font-bold text-text-primary mb-6">Content Pipeline Dashboard</h1>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="topic" className="block text-sm font-medium text-text-primary mb-2">
                Enter Topic
              </label>
              <input
                id="topic"
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., Artificial Intelligence in Healthcare"
                className="w-full px-4 py-3 border border-border rounded-lg focus:ring-2 focus:ring-accent focus:border-transparent outline-none bg-white text-text-primary"
                disabled={loading}
                onKeyPress={(e) => e.key === 'Enter' && !loading && runPipeline()}
              />
            </div>
            
            {error && (
              <div className="bg-error/10 border border-error/20 text-error px-4 py-3 rounded-lg">
                {error}
              </div>
            )}
            
            <button
              onClick={runPipeline}
              disabled={loading || !topic.trim()}
              className="w-full px-6 py-3 bg-accent text-white rounded-lg font-medium hover:bg-accent-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Running Pipeline...</span>
                </>
              ) : (
                <>
                  <Play className="h-5 w-5" />
                  <span>Run Pipeline</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Pipeline Status */}
        {pipeline && (
          <div className="bg-surface-light border border-border rounded-xl p-8 mb-8">
            <h2 className="text-2xl font-semibold text-text-primary mb-6">Pipeline Status</h2>
            <div className="space-y-2 mb-6">
              <div className="flex items-center justify-between">
                <span className="text-text-secondary">Pipeline ID:</span>
                <span className="font-mono text-sm text-text-primary">{pipeline.pipeline_id}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-text-secondary">Topic:</span>
                <span className="text-text-primary font-medium">{pipeline.topic}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-text-secondary">Status:</span>
                <span className={`font-medium ${
                  pipeline.status === 'completed' ? 'text-success' : 
                  pipeline.status === 'failed' ? 'text-error' : 
                  'text-accent'
                }`}>
                  {pipeline.status}
                </span>
              </div>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-4">
              {Object.entries(pipeline.tasks).map(([taskName, task]) => (
                <div
                  key={task.id}
                  className="bg-white border border-border rounded-lg p-4 flex items-center space-x-3"
                >
                  <div className="text-accent">{getTaskIcon(taskName)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-text-primary truncate">
                      {taskName.charAt(0).toUpperCase() + taskName.slice(1)}
                    </div>
                    <div className="flex items-center space-x-2 mt-1">
                      {getStatusIcon(task.status)}
                      <span className="text-xs text-text-secondary">{task.status}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-text-primary">Pipeline Results</h2>
            
            {Object.entries(results).map(([taskId, taskResult]: [string, any]) => (
              <div key={taskId} className="bg-surface-light border border-border rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold text-text-primary">{taskResult.title}</h3>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(taskResult.status)}
                    <span className="text-sm text-text-secondary">{taskResult.status}</span>
                  </div>
                </div>

                {taskResult.result && (
                  <div className="space-y-4">
                    {taskResult.result.content && (
                      <div>
                        <h4 className="text-sm font-medium text-text-secondary mb-2">Content Preview</h4>
                        <div className="bg-white border border-border rounded-lg p-4 max-h-64 overflow-y-auto">
                          <pre className="text-sm text-text-primary whitespace-pre-wrap">
                            {taskResult.result.content.substring(0, 500)}
                            {taskResult.result.content.length > 500 && '...'}
                          </pre>
                        </div>
                      </div>
                    )}

                    {taskResult.result.word_count && (
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-white border border-border rounded-lg p-3">
                          <div className="text-xs text-text-secondary mb-1">Word Count</div>
                          <div className="text-lg font-semibold text-text-primary">
                            {taskResult.result.word_count}
                          </div>
                        </div>
                        {taskResult.result.seo_score && (
                          <div className="bg-white border border-border rounded-lg p-3">
                            <div className="text-xs text-text-secondary mb-1">SEO Score</div>
                            <div className="text-lg font-semibold text-text-primary">
                              {taskResult.result.seo_score}/100
                            </div>
                          </div>
                        )}
                        {taskResult.result.quality_score && (
                          <div className="bg-white border border-border rounded-lg p-3">
                            <div className="text-xs text-text-secondary mb-1">Quality Score</div>
                            <div className="text-lg font-semibold text-text-primary">
                              {taskResult.result.quality_score}/100
                            </div>
                          </div>
                        )}
                        {taskResult.result.sources_found && (
                          <div className="bg-white border border-border rounded-lg p-3">
                            <div className="text-xs text-text-secondary mb-1">Sources</div>
                            <div className="text-lg font-semibold text-text-primary">
                              {taskResult.result.sources_found}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

