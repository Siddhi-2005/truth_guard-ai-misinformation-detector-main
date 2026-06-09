import React, { useState, useEffect, useRef } from 'react';
import { 
  ShieldCheck, 
  Search, 
  Send, 
  AlertCircle, 
  CheckCircle2, 
  XCircle, 
  HelpCircle, 
  ExternalLink,
  BookOpen,
  Image as ImageIcon,
  MessageSquare,
  Globe
} from 'lucide-react';
import './App.css';

// Base API configuration
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8002'
  : '/api';

interface EvidenceItem {
  title: string;
  org: string;
  url: string;
  date?: string;
  extract: string;
}

interface VerdictData {
  claim_id: string;
  timestamp_utc: string;
  input: {
    original_text: string;
    language: string;
    source_url?: string;
  };
  normalized_claim: string;
  verdict: 'TRUE' | 'FALSE' | 'MISLEADING' | 'UNVERIFIED' | 'INCOMPLETE';
  confidence: number;
  scores: {
    supporting_score: number;
    refuting_score: number;
  };
  evidence: EvidenceItem[];
  explanation: {
    public_summary: string;
    technical_note: string;
  };
  recommended_actions: string[];
  image_generation?: {
    requested: boolean;
    image_prompt?: string;
    generated_image_base64?: string;
  };
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  assessment?: string;
  imagePrompt?: string;
}

function App() {
  // Connection states
  const [backendConnected, setBackendConnected] = useState<boolean>(false);
  const [checkingConnection, setCheckingConnection] = useState<boolean>(true);

  // Verification states
  const [claim, setClaim] = useState<string>('');
  const [imageRequested, setImageRequested] = useState<boolean>(false);
  const [language, setLanguage] = useState<string>('English');
  const [verifying, setVerifying] = useState<boolean>(false);
  const [verdictResult, setVerdictResult] = useState<VerdictData | null>(null);
  const [verifyError, setVerifyError] = useState<string | null>(null);

  // Chat states
  const [chatInput, setChatInput] = useState<string>('');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: 'Hello! I am FactGuard AI. You can ask me follow-up questions about verified claims, or type a topic directly to run custom checks.'
    }
  ]);
  const [chatLoading, setChatLoading] = useState<boolean>(false);
  const [chatLogs, setChatLogs] = useState<string[]>([]);
  const chatMessagesEndRef = useRef<HTMLDivElement>(null);

  // Example preset claims
  const presets = [
    { label: '🧬 Health', text: 'Eating garlic prevents COVID-19 infection.' },
    { label: '🤖 Tech', text: 'AI models can read minds through browser cookies.' },
    { label: '🏦 Finance', text: 'The government will replace all paper currency with digital coins next week.' },
    { label: '🌍 Space', text: 'NASA discovered a secret parallel universe where time runs backward.' }
  ];

  // Check backend connection on mount
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/`);
        if (response.ok) {
          setBackendConnected(true);
        } else {
          setBackendConnected(false);
        }
      } catch (err) {
        setBackendConnected(false);
      } finally {
        setCheckingConnection(false);
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 10000);
    return () => clearInterval(interval);
  }, []);

  // Scroll to bottom of chat
  useEffect(() => {
    chatMessagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, chatLogs]);

  // Handle claim verification
  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!claim.trim()) return;

    setVerifying(true);
    setVerdictResult(null);
    setVerifyError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          claim: claim.trim(),
          image_requested: imageRequested,
          language
        })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to verify claim');
      }

      const data = await response.json();
      setVerdictResult(data);
    } catch (err: any) {
      console.error(err);
      const msg = err.message || '';
      if (msg.includes('429') || msg.includes('RESOURCE_EXHAUSTED')) {
        setVerifyError('⏳ API rate limit reached. The free tier has limited requests per minute. Please wait 60 seconds and try again.');
      } else if (msg.includes('503') || msg.includes('UNAVAILABLE')) {
        setVerifyError('🔄 The AI model is temporarily busy due to high demand. Please wait a moment and try again.');
      } else {
        setVerifyError(msg || 'An error occurred while connecting to the backend.');
      }
    } finally {
      setVerifying(false);
    }
  };

  // Handle chat submission
  const handleSendChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || chatLoading) return;

    const userMsgText = chatInput.trim();
    setChatInput('');
    setChatLoading(true);
    setChatLogs([]);

    const userMsgId = Math.random().toString();
    setChatMessages(prev => [...prev, { id: userMsgId, sender: 'user', text: userMsgText }]);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMsgText,
          language,
          session_id: 'chat_session_web',
          agent_name: 'FactGuard'
        })
      });

      if (!response.body) {
        throw new Error('Streaming not supported by backend');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim()) continue;
          
          try {
            const event = JSON.parse(line);
            if (event.type === 'log') {
              setChatLogs(prev => [...prev, event.message]);
            } else if (event.type === 'result') {
              const resultData = event.data;
              setChatMessages(prev => [
                ...prev,
                {
                  id: Math.random().toString(),
                  sender: 'assistant',
                  text: resultData.response,
                  assessment: resultData.assessment,
                  imagePrompt: resultData.image_prompt
                }
              ]);
              setChatLogs([]);
            } else if (event.type === 'error') {
              throw new Error(event.message);
            }
          } catch (jsonErr) {
            console.error('Error parsing line:', line, jsonErr);
          }
        }
      }
    } catch (err: any) {
      console.error(err);
      setChatMessages(prev => [
        ...prev,
        {
          id: Math.random().toString(),
          sender: 'assistant',
          text: `Error: ${err.message || 'Could not communicate with FactGuard agent.'}`
        }
      ]);
      setChatLogs([]);
    } finally {
      setChatLoading(false);
    }
  };

  const getVerdictIcon = (verdict: string) => {
    switch (verdict) {
      case 'TRUE':
        return <CheckCircle2 size={32} style={{ color: 'var(--color-true)' }} />;
      case 'FALSE':
        return <XCircle size={32} style={{ color: 'var(--color-false)' }} />;
      case 'MISLEADING':
        return <AlertCircle size={32} style={{ color: 'var(--color-misleading)' }} />;
      default:
        return <HelpCircle size={32} style={{ color: 'var(--color-unverified)' }} />;
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="brand-section">
          <ShieldCheck size={28} color="var(--primary-color)" />
          <div className="app-logo-text">
            <span>FactGuard</span>
            <span className="logo-accent">AI</span>
          </div>
        </div>

        <nav className="nav-links">
          <a className="nav-link active">Analyzer</a>
          <a className="nav-link" href="#chat-section">Agent Chat</a>
        </nav>

        <div className="status-badge">
          <div className={`status-dot ${backendConnected ? 'connected' : 'disconnected'}`}></div>
          {checkingConnection ? (
            <span>Connecting...</span>
          ) : backendConnected ? (
            <span>Active</span>
          ) : (
            <span style={{ color: 'var(--color-false)' }}>Offline</span>
          )}
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <h1 className="hero-title">
          Verify Any Claim With <span>Autonomous AI</span>
        </h1>
        <p className="hero-subtitle">
          FactGuard runs live web searches, cross-references sources, and delivers evidence-based truth scores in seconds.
        </p>
      </section>

      {/* Main Grid */}
      <main className="console-grid">
        
        {/* Left Column: Analyzer Console */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
          
          <div className="console-card">
            <div className="card-header-group">
              <h2 className="card-title">
                <Search size={20} color="var(--primary-color)" />
                Claim Verification Console
              </h2>
              <span className="card-subtitle">Submit rumors, social posts, or news headings for deep analysis.</span>
            </div>

            <form onSubmit={handleVerify} className="search-container-box">
              <div className="search-input-wrapper">
                <Search className="search-input-icon" size={20} />
                <input
                  type="text"
                  className="premium-search-input"
                  placeholder="Enter a claim (e.g. Eating garlic prevents COVID-19)..."
                  value={claim}
                  onChange={(e) => setClaim(e.target.value)}
                  disabled={verifying}
                />
              </div>

              {/* Preset claims buttons */}
              <div className="preset-section">
                <span className="preset-title">Or Try An Example:</span>
                <div className="presets-container">
                  {presets.map((p, idx) => (
                    <button
                      key={idx}
                      type="button"
                      className="preset-pill"
                      onClick={() => setClaim(p.text)}
                      disabled={verifying}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Controls Row */}
              <div className="controls-row">
                <label className="switch-label">
                  <input
                    type="checkbox"
                    className="switch-input"
                    checked={imageRequested}
                    onChange={(e) => setImageRequested(e.target.checked)}
                    disabled={verifying}
                  />
                  <span>Generate Awareness Graphic</span>
                </label>

                <div className="select-wrapper">
                  <Globe size={15} color="var(--text-muted)" />
                  <select
                    className="premium-select"
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    disabled={verifying}
                  >
                    <option value="English">English</option>
                    <option value="Hindi">Hindi</option>
                    <option value="Marathi">Marathi</option>
                    <option value="Spanish">Spanish</option>
                  </select>
                </div>
              </div>

              {/* Action Button */}
              <div className="action-btn-group">
                <button
                  type="submit"
                  className="btn-premium-verify"
                  disabled={verifying || !claim.trim() || !backendConnected}
                >
                  {verifying ? (
                    <>
                      <span className="spinner-micro"></span>
                      <span>FactGuard is Researching...</span>
                    </>
                  ) : (
                    <>
                      <ShieldCheck size={18} />
                      <span>Verify Claim Truthfulness</span>
                    </>
                  )}
                </button>
              </div>
            </form>

            {/* Error Message */}
            {verifyError && (
              <div className="verdict-badge-card false" style={{ display: 'flex', gap: '14px', alignItems: 'center' }}>
                <AlertCircle size={28} style={{ color: 'var(--color-false)' }} />
                <div>
                  <strong style={{ color: 'var(--color-false)' }}>Connection Error:</strong>
                  <div style={{ fontSize: '13px', marginTop: '3px', color: 'var(--text-secondary)' }}>
                    Failed to reach verification agent. Verify the backend is running on port 8002 and your API key is active.
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Verification Results Hub */}
          {verdictResult && (
            <div className="verdict-hub-container">
              {/* Verdict Header Badge */}
              <div className={`verdict-badge-card ${verdictResult.verdict.toLowerCase()}`}>
                <div className="verdict-info-left">
                  {getVerdictIcon(verdictResult.verdict)}
                  <div className="verdict-title-text">
                    <span className="verdict-time">AUTOMATED VERDICT</span>
                    <span className={`verdict-main-label ${verdictResult.verdict.toLowerCase()}`}>
                      {verdictResult.verdict}
                    </span>
                  </div>
                </div>

                <div className="verdict-metrics-dial">
                  <span className="metrics-value">
                    {Math.round(verdictResult.confidence * 100)}%
                  </span>
                  <span className="metrics-label">Confidence</span>
                </div>
              </div>

              {/* Claims details */}
              <div className="detailed-report-section">
                <div className="report-title">Original Claim Analyzed</div>
                <div className="report-text">"{verdictResult.input.original_text}"</div>
                
                {verdictResult.normalized_claim !== verdictResult.input.original_text && (
                  <>
                    <div className="divider"></div>
                    <div className="report-title">Normalized Claim</div>
                    <div className="report-text">"{verdictResult.normalized_claim}"</div>
                  </>
                )}
              </div>

              {/* Explanations */}
              <div className="detailed-report-section">
                <div className="report-title">Public Verdict Summary</div>
                <div className="report-text">{verdictResult.explanation.public_summary}</div>
                
                <div className="divider"></div>
                
                <div className="report-title">Technical Deep-Dive</div>
                <div className="report-text" style={{ fontFamily: 'monospace', fontSize: '12px', background: '#F8FAFC', padding: '12px', borderRadius: '4px' }}>
                  {verdictResult.explanation.technical_note}
                </div>
              </div>

              {/* Poster Preview */}
              {verdictResult.image_generation?.generated_image_base64 && (
                <div className="poster-preview-card">
                  <div className="report-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <ImageIcon size={18} color="var(--primary-color)" />
                    Awareness Poster Generated
                  </div>
                  <img
                    src={`data:image/png;base64,${verdictResult.image_generation.generated_image_base64}`}
                    alt="Awareness Poster"
                    style={{
                      width: '100%',
                      maxHeight: '320px',
                      objectFit: 'contain',
                      borderRadius: 'var(--radius-sm)',
                      backgroundColor: '#F1F5F9',
                      border: '1px solid var(--border-color)'
                    }}
                  />
                </div>
              )}

              {/* Verifiable Sources */}
              {verdictResult.evidence && verdictResult.evidence.length > 0 && (
                <div className="evidence-section">
                  <h3 className="evidence-header-title">
                    <BookOpen size={20} color="var(--primary-color)" />
                    Reference Sources & Evidence Checked ({verdictResult.evidence.length})
                  </h3>
                  <div className="evidence-cards-container">
                    {verdictResult.evidence.map((source, index) => (
                      <div key={index} className="evidence-source-card">
                        <div className="source-card-header">
                          <span className="source-badge">{source.org || 'Web Citation'}</span>
                          <a
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="source-link-anchor"
                          >
                            Visit Source <ExternalLink size={12} />
                          </a>
                        </div>
                        <h4 className="source-title">{source.title}</h4>
                        <p className="source-extract">"{source.extract}"</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>
          )}

        </div>

        {/* Right Column: AI Companion Chat */}
        <div id="chat-section">
          <div className="console-card chat-console-card">
            <div className="card-header-group">
              <h2 className="card-title">
                <MessageSquare size={20} color="var(--primary-color)" />
                AI Agent Companion
              </h2>
              <span className="card-subtitle">Ask follow-up questions or test hypotheses with the FactGuard agent.</span>
            </div>

            <div className="chat-messages-viewport">
              {chatMessages.map((msg) => (
                <div key={msg.id} className={`message-bubble ${msg.sender}`}>
                  {msg.text}
                  {msg.assessment && (
                    <div className="chat-assessment-footer">
                      🔍 Agent Assessment: {msg.assessment}
                    </div>
                  )}
                </div>
              ))}

              {/* Stream Logs */}
              {chatLoading && chatLogs.length > 0 && (
                <div className="log-stream-bubble">
                  ⚡ {chatLogs[chatLogs.length - 1]}
                </div>
              )}

              {/* Streaming loading bubble */}
              {chatLoading && chatLogs.length === 0 && (
                <div className="message-bubble assistant" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span className="spinner-micro" style={{ borderTopColor: 'var(--primary-color)', borderLeftColor: '#E2E8F0', borderRightColor: '#E2E8F0', borderBottomColor: '#E2E8F0' }}></span>
                  <span>Agent is compiling response...</span>
                </div>
              )}

              <div ref={chatMessagesEndRef} />
            </div>

            <form onSubmit={handleSendChat} className="chat-form-row">
              <input
                type="text"
                className="chat-text-input"
                placeholder={backendConnected ? "Ask the AI Agent follow-up questions..." : "Connect backend to enable chat..."}
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                disabled={chatLoading || !backendConnected}
              />
              <button
                type="submit"
                className="chat-send-btn"
                disabled={chatLoading || !chatInput.trim() || !backendConnected}
              >
                <Send size={16} />
              </button>
            </form>
          </div>
        </div>

      </main>
    </div>
  );
}

export default App;
