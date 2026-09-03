import { useState, useEffect } from 'react';
import { Bot, Info, RotateCcw } from 'lucide-react';
import { aiAPI } from '../services/api';
import AIChat from '../components/AIChat';

export default function AIAssistant() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await aiAPI.getHistory();
      const history = Array.isArray(res.data) ? res.data : (res.data?.data || res.data?.messages || []);
      setMessages(history);
      setConversationId(history.at(-1)?.conversation_id || null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to load conversation history. You can still start a new conversation.');
    }
  };

  const handleSendMessage = async (message) => {
    if (!message?.trim() || loading) return;
    const userMsg = { role: 'user', content: message };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    setError('');

    try {
      const res = await aiAPI.chat(message, conversationId, suggestedQuestions);
      const data = res.data?.data || res.data;
      const assistantMsg = {
        role: 'assistant',
        content: data.answer || data.response || data.message,
        suggested_questions: data.suggested_questions || [],
      };
      setConversationId(data.conversation_id || conversationId);
      setSuggestedQuestions(data.suggested_questions || []);
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setError(err.response?.data?.detail || 'I\'m unable to process that request right now. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const startNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    setSuggestedQuestions([]);
    setError('');
  };

  return (
    <div className="flex-1 p-4 md:p-6 lg:p-8 max-w-5xl">
      <div className="mb-4">
        <div className="flex items-center gap-3 mb-1">
          <Bot className="w-6 h-6 text-brand-600" />
          <h1 className="page-title">AI Assistant</h1>
        </div>
        <div className="flex items-center justify-between gap-4">
          <p className="page-subtitle">Ask questions about your financial health and get personalized guidance</p>
          <button type="button" onClick={startNewConversation} className="btn-secondary flex items-center gap-2 text-sm">
            <RotateCcw className="w-4 h-4" /> New conversation
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700" role="alert">
          {error}
        </div>
      )}

      <div className="card overflow-hidden" style={{ height: 'calc(100vh - 280px)', minHeight: '400px' }}>
        <AIChat messages={messages} onSendMessage={handleSendMessage} loading={loading} />
      </div>

      <div className="mt-4 flex items-center gap-2 text-xs text-gray-400">
        <Info className="w-4 h-4" />
        <p>FinGuard AI provides supportive guidance, not financial advice. Always consult a licensed financial advisor for major decisions.</p>
      </div>
    </div>
  );
}
