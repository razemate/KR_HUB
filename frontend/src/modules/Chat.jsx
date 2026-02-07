import React, { useState, useEffect, useRef } from 'react';
import { Send, Paperclip, BarChart3, Bot, User, FileText, Database, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

export default function Chat({ session }) {
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'Hello! I am your central AI assistant. You can upload CSV/PDF files or ask me about your database.' }
  ]);
  const [input, setInput] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [mode, setMode] = useState('database'); // 'general' or 'database'
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
        textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [input]);

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
  };

  const sendMessage = async () => {
    if ((!input.trim() && !selectedFile) || isLoading) return;

    const userMessage = { 
        role: 'user', 
        text: input, 
        file: selectedFile ? selectedFile.name : null 
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto'; // Reset height
    setIsLoading(true);

    try {
        const formData = new FormData();
        formData.append('question', input || "Analyze this file");
        formData.append('mode', mode); // Send selected mode
        if (selectedFile) {
            formData.append('file', selectedFile);
        }
        
        const token = session?.access_token;
        // Allow general mode to work without authentication, but require auth for database mode
        if (!token && mode === 'database') {
            // Fallback for demo/dev mode: Tell the user to connect instead of crashing
             setMessages(prev => [...prev, {
                role: 'ai',
                text: "⚠️ **Authentication Required**\n\nTo access real data, I need a secure connection to the database. Please sign in using the button in the sidebar (if available) or check your configuration."
            }]);
            return;
        }
        const headers = {};
        // Only include authorization header if we have a token
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        // Determine API URL: Prioritize Env Vars -> Dev Proxy -> Relative (Prod)
        const isDev = import.meta.env.DEV;
        const API_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_BACKEND_URL || (isDev ? 'http://localhost:8000' : '');
        
        const res = await fetch(`${API_URL}/modules/chat-with-data/analyze`, {
            method: 'POST',
            headers: headers,
            body: formData
        });

        if (!res.ok) {
            let errorMessage = `Server responded with status ${res.status}. `;

            try {
                const errorData = await res.json();
                errorMessage += errorData.detail || "Server error occurred";
            } catch {
                // If we can't parse the error response, use a generic message
                errorMessage += "Unable to parse server error response";
            }

            throw new Error(errorMessage);
        }

        // --- STREAMING RESPONSE HANDLING ---
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let aiResponse = "";
        
        // Add initial empty message
        setMessages(prev => [...prev, { role: 'ai', text: "", dataPreview: [] }]);
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const jsonStr = line.slice(6);
                        if (jsonStr === "[DONE]") break;
                        
                        const data = JSON.parse(jsonStr);
                        
                        if (data.chunk) {
                            aiResponse += data.chunk;
                            setMessages(prev => {
                                const newMsgs = [...prev];
                                newMsgs[newMsgs.length - 1].text = aiResponse;
                                return newMsgs;
                            });
                        }
                    } catch (e) {
                        console.error("Error parsing stream:", e);
                    }
                }
            }
        }

    } catch (error) {
        console.error("Chat error:", error);
        let errorMessage = "Network error: Unable to connect to the server. ";

        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            // Network error (server unreachable, DNS failure, etc.)
            errorMessage += "Please check your connection and try again.";
        } else {
            // Other types of errors
            errorMessage += error.message || "An unexpected error occurred.";
        }

        setMessages(prev => [...prev, { role: 'ai', text: `Error: ${errorMessage}` }]);
    } finally {
        setIsLoading(false);
        setSelectedFile(null);
        if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="h-full flex flex-col max-w-5xl mx-auto animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-display font-bold text-slate-900 flex items-center gap-2">
            <Bot className="text-brand-600" />
            Conversational Intelligence
        </h2>
        <div className="text-xs font-mono text-slate-400">
            Provider: Gemini Pro (Fallback: OpenRouter)
        </div>
      </div>
      
      <div id="chat-window" className="flex-1 bg-white rounded-2xl shadow-sm border border-slate-200 flex flex-col overflow-hidden h-[600px]">
        <div id="messages" className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar bg-slate-50/50">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] p-5 rounded-2xl shadow-sm ${msg.role === 'user' ? 'bg-brand-600 text-white' : 'bg-white border border-slate-200 text-slate-700'}`}>
                {msg.file && (
                    <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/20">
                        <FileText className="w-4 h-4" />
                        <span className="text-xs font-mono opacity-80">{msg.file}</span>
                    </div>
                )}
                <div className={`prose prose-sm max-w-none ${msg.role === 'user' ? 'prose-invert' : ''}`}>
                    <ReactMarkdown 
                        remarkPlugins={[remarkGfm]} 
                        rehypePlugins={[rehypeRaw]}
                        components={{
                            table: ({...props}) => <div className="overflow-x-auto my-4 border rounded-lg"><table className="w-full text-sm text-left" {...props} /></div>,
                            th: ({...props}) => <th className="bg-slate-100 px-4 py-2 font-semibold border-b" {...props} />,
                            td: ({...props}) => <td className="px-4 py-2 border-b last:border-0" {...props} />
                        }}
                    >
                        {msg.text}
                    </ReactMarkdown>
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
              <div className="flex justify-start">
                  <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-3">
                      <div className="w-2 h-2 bg-brand-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-brand-500 rounded-full animate-bounce delay-75"></div>
                      <div className="w-2 h-2 bg-brand-500 rounded-full animate-bounce delay-150"></div>
                  </div>
              </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="p-4 bg-white border-t border-slate-200">
          
          {/* Mode Toggle */}
          <div className="flex justify-center mb-3">
            <div className="bg-slate-100 p-1 rounded-lg flex items-center">
                <button
                    onClick={() => setMode('general')}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                        mode === 'general' 
                        ? 'bg-white text-brand-600 shadow-sm' 
                        : 'text-slate-500 hover:text-slate-700'
                    }`}
                >
                    <Sparkles className="w-3.5 h-3.5" />
                    General Chat
                </button>
                <button
                    onClick={() => setMode('database')}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                        mode === 'database' 
                        ? 'bg-white text-brand-600 shadow-sm' 
                        : 'text-slate-500 hover:text-slate-700'
                    }`}
                >
                    <Database className="w-3.5 h-3.5" />
                    KR Database Agent
                </button>
            </div>
          </div>

          {selectedFile && (
              <div className="mb-2 inline-flex items-center gap-2 px-3 py-1.5 bg-brand-50 text-brand-700 rounded-full text-xs font-medium border border-brand-100">
                  <FileText className="w-3 h-3" />
                  {selectedFile.name}
                  <button onClick={() => setSelectedFile(null)} className="hover:text-red-500 ml-1">×</button>
              </div>
          )}
          <div className="relative flex items-end gap-2">
            <input 
                type="file" 
                ref={fileInputRef}
                className="hidden" 
                onChange={handleFileSelect}
                accept=".csv,.txt,.md,.pdf,.xlsx,.xls,.docx,.json,.py,.js,.html,.css,.xml,.png,.jpg,.jpeg,.webp"
            />
            <button 
                onClick={() => fileInputRef.current?.click()}
                className="p-3 mb-1 text-slate-400 hover:text-brand-600 hover:bg-slate-50 rounded-xl transition-all"
                title="Upload File"
            >
                <Paperclip className="w-5 h-5" />
            </button>
            
            <textarea 
              ref={textareaRef}
              placeholder="Ask anything about your data..." 
              className="flex-1 px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500 focus:border-transparent outline-none transition-all resize-none max-h-32 min-h-[46px]"
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            
            <button 
              onClick={sendMessage}
              disabled={isLoading || (!input.trim() && !selectedFile)}
              className="p-3 mb-1 bg-brand-600 text-white rounded-xl font-bold hover:bg-brand-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-brand-500/30"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
