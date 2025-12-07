import { useEffect, useRef, useState } from 'react';
import { Terminal, Play, StopCircle, Activity, LayoutDashboard, History, Settings } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { Textarea } from './components/ui/textarea';
import { cn } from './lib/utils';
import { format } from 'date-fns';
import { OnboardingWizard } from './components/Onboarding';
import { HelpContext } from './components/HelpContext';

const API_BASE = 'http://localhost:8000/api';
const WS_URL = 'ws://localhost:8000/api/ws';

// Types
interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  source: string;
}

interface OptimizedPrompt {
  id?: number;
  original_task: string;
  optimized_prompt: string;
  reasoning: string;
  estimated_tokens: number;
}

interface TaskHistory {
    id: number;
    description: string;
    status: string;
    created_at: string;
}

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'history'>('dashboard');
  const [task, setTask] = useState('');
  const [optimizedData, setOptimizedData] = useState<OptimizedPrompt | null>(null);
  const [status, setStatus] = useState('idle');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<TaskHistory[]>([]);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // WebSocket for Real-time Logs
  useEffect(() => {
    const ws = new WebSocket(WS_URL);

    ws.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.type === 'log') {
        setLogs((prev) => [...prev, payload.data].slice(-500)); // Keep last 500
      } else if (payload.type === 'status') {
        setStatus(payload.data);
      }
    };

    return () => ws.close();
  }, []);

  // Auto-scroll logs
  useEffect(() => {
    if (logsEndRef.current) {
        logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  // Initial Data Fetch
  useEffect(() => {
    fetchStatus();
    fetchHistory();
  }, []);

  const fetchStatus = async () => {
    try {
        const res = await fetch(`${API_BASE}/status`);
        const data = await res.json();
        setStatus(data.status);
    } catch (e) { console.error(e) }
  };

  const fetchHistory = async () => {
      try {
          const res = await fetch(`${API_BASE}/history`);
          const data = await res.json();
          setHistory(data);
      } catch (e) { console.error(e) }
  }

  const optimizeTask = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: task, context_files: [] }),
      });
      const data = await res.json();
      setOptimizedData(data);
      fetchHistory(); // Update history list
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const runAgent = async () => {
    if (!optimizedData || !optimizedData.id) return;
    try {
      await fetch(`${API_BASE}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: optimizedData.id }),
      });
      // Status update comes via WS
    } catch (err) {
      console.error(err);
    }
  };

  const stopAgent = async () => {
    try {
      await fetch(`${API_BASE}/stop`, { method: 'POST' });
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex h-screen bg-gray-950 text-gray-50 font-sans overflow-hidden">
      <OnboardingWizard onComplete={() => {}} />
      {/* Sidebar */}
      <aside className="w-64 border-r border-gray-800 bg-gray-950 flex flex-col">
        <div className="p-6">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            AutoReflex
          </h1>
          <p className="text-xs text-gray-500 mt-1">v0.1.0 Beta</p>
        </div>
        
        <nav className="flex-1 px-4 space-y-2">
          <Button 
            variant={activeTab === 'dashboard' ? 'secondary' : 'ghost'} 
            className="w-full justify-start" 
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard className="mr-2 h-4 w-4" /> Dashboard
          </Button>
          <Button 
            variant={activeTab === 'history' ? 'secondary' : 'ghost'} 
            className="w-full justify-start"
            onClick={() => setActiveTab('history')}
          >
            <History className="mr-2 h-4 w-4" /> History
          </Button>
          <Button variant="ghost" className="w-full justify-start opacity-50 cursor-not-allowed">
            <Settings className="mr-2 h-4 w-4" /> Settings
          </Button>
        </nav>

        <div className="p-4 border-t border-gray-800">
            <div className="flex items-center space-x-2">
                <div className={cn("w-2 h-2 rounded-full", status === 'running' ? "bg-green-500 animate-pulse" : "bg-gray-500")} />
                <span className="text-xs uppercase font-mono text-gray-400">{status}</span>
            </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-gray-900/50 p-8">
        {activeTab === 'dashboard' && (
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 h-full">
            
            {/* Left Col: Controls */}
            <div className="space-y-6 flex flex-col h-full">
                {/* 1. Define */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                            <div className="flex items-center">
                                <Activity className="mr-2 h-5 w-5 text-blue-500" />
                                Observation Phase
                            </div>
                            <HelpContext topic="Observation (Input)" description="Enter your high-level task here. The system uses this raw input to 'Orient' itself before taking action. Be specific about your goals." />
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <Textarea 
                            placeholder="Describe your objective for Claude Code..." 
                            className="h-32 font-mono"
                            value={task}
                            onChange={(e) => setTask(e.target.value)}
                        />
                        <div className="flex justify-end">
                            <Button onClick={optimizeTask} disabled={loading || !task}>
                                {loading ? "Optimizing..." : "Analyze & Optimize"}
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                {/* 2. Orientation */}
                {optimizedData && (
                    <Card className="flex-1 flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <CardHeader>
                            <CardTitle className="flex items-center justify-between">
                                <div className="flex items-center">
                                    <Terminal className="mr-2 h-5 w-5 text-purple-500" />
                                    Orientation Phase
                                </div>
                                <HelpContext topic="Orientation (Optimization)" description="The system has analyzed your request and generated an optimized prompt (Flight Plan). Review this plan before authorizing execution." />
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="flex-1 flex flex-col space-y-4">
                            <div className="bg-gray-950 border border-gray-800 rounded-md p-4 flex-1 overflow-auto">
                                <pre className="text-xs text-gray-300 font-mono whitespace-pre-wrap">
                                    {optimizedData.optimized_prompt}
                                </pre>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="text-xs text-gray-500">
                                    Est. Tokens: {optimizedData.estimated_tokens}
                                </div>
                                <div className="space-x-2">
                                    {status === 'running' ? (
                                        <Button variant="destructive" onClick={stopAgent}>
                                            <StopCircle className="mr-2 h-4 w-4" /> Abort
                                        </Button>
                                    ) : (
                                        <Button className="bg-green-600 hover:bg-green-700" onClick={runAgent}>
                                            <Play className="mr-2 h-4 w-4" /> Execute OODA Loop
                                        </Button>
                                    )}
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                )}
            </div>

            {/* Right Col: Monitoring */}
            <Card className="h-full flex flex-col border-gray-800 bg-black">
                <CardHeader className="border-b border-gray-900 py-3">
                    <div className="flex items-center justify-between">
                        <CardTitle className="text-sm font-mono uppercase text-gray-400">System Logs</CardTitle>
                        <Badge variant="outline" className="font-mono text-[10px]">LIVE</Badge>
                    </div>
                </CardHeader>
                <CardContent className="flex-1 p-0 overflow-hidden relative">
                    <div className="absolute inset-0 p-4 overflow-y-auto font-mono text-xs space-y-1">
                        {logs.length === 0 && (
                            <div className="text-gray-600 italic">Waiting for signal...</div>
                        )}
                        {logs.map((log, i) => (
                            <div key={i} className="flex gap-2">
                                <span className="text-gray-600">[{format(new Date(log.timestamp), 'HH:mm:ss')}]</span>
                                <span className={cn(
                                    log.message.includes('[WARN]') ? 'text-yellow-500' :
                                    log.message.includes('[ERROR]') ? 'text-red-500' :
                                    log.message.includes('[SUCCESS]') ? 'text-green-500' :
                                    'text-gray-300'
                                )}>
                                    {log.message}
                                </span>
                            </div>
                        ))}
                        <div ref={logsEndRef} />
                    </div>
                </CardContent>
            </Card>

            </div>
        )}

        {activeTab === 'history' && (
            <div className="space-y-4">
                <h2 className="text-2xl font-bold">Mission History</h2>
                <div className="grid gap-4">
                    {history.map((h) => (
                        <Card key={h.id} className="hover:bg-gray-900 transition-colors">
                            <CardContent className="p-4 flex items-center justify-between">
                                <div>
                                    <div className="font-medium text-white truncate max-w-xl">{h.description}</div>
                                    <div className="text-xs text-gray-500 mt-1">
                                        {format(new Date(h.created_at), 'MMM d, yyyy HH:mm')}
                                    </div>
                                </div>
                                <Badge variant={h.status === 'completed' ? 'success' : 'secondary'}>
                                    {h.status}
                                </Badge>
                            </CardContent>
                        </Card>
                    ))}
                    {history.length === 0 && (
                        <div className="text-gray-500 text-center py-10">No missions recorded.</div>
                    )}
                </div>
            </div>
        )}
      </main>
    </div>
  );
}

export default App;
