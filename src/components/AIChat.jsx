import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';

export default function AIChat({ onSendMessage, messages = [], loading = false }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !loading && (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <div className="w-16 h-16 rounded-2xl bg-brand-50 flex items-center justify-center mb-4">
              <Bot className="w-8 h-8 text-brand-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-1">FinGuard AI Assistant</h3>
            <p className="text-sm text-gray-500 max-w-sm">
              Ask me anything about your financial health, risk factors, or how to improve your financial wellness.
            </p>
            <div className="mt-6 flex flex-wrap gap-2 justify-center max-w-md">
              {['Why is my risk score high?', 'How can I reduce my debt?', 'What is affecting my health score?'].map((q) => (
                <button
                  key={q}
                  onClick={() => onSendMessage(q)}
                  className="px-3 py-1.5 text-xs text-brand-600 bg-brand-50 rounded-full hover:bg-brand-100 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex flex-wrap gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-brand-600" />
              </div>
            )}
            <div className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
              msg.role === 'user'
                ? 'bg-brand-600 text-white rounded-br-md'
                : 'bg-gray-100 text-gray-800 rounded-bl-md'
            }`}>
              {msg.content}
            </div>
            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4 text-white" />
              </div>
            )}
            {msg.role === 'assistant' && msg.suggested_questions?.length > 0 && (
              <div className="basis-full ml-11 -mt-1 flex flex-wrap gap-2">
                {msg.suggested_questions.map((question) => (
                  <button
                    key={question}
                    type="button"
                    onClick={() => onSendMessage(question)}
                    disabled={loading}
                    className="px-3 py-1.5 text-xs text-brand-700 bg-brand-50 border border-brand-100 rounded-full hover:bg-brand-100 disabled:opacity-50"
                  >
                    {question}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-brand-600" />
            </div>
            <div className="bg-gray-100 px-4 py-3 rounded-2xl rounded-bl-md">
              <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-100 bg-white">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your financial health..."
            className="input-field flex-1"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="btn-primary px-4 py-3 disabled:opacity-50"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
}
