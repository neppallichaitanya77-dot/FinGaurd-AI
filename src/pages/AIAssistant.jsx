import { useState, useEffect } from 'react';
import { Bot, Info } from 'lucide-react';
import { aiAPI } from '../services/api';
import AIChat from '../components/AIChat';

const DEMO_RESPONSES = {
  'Why is my risk score high?': 'Your risk score is elevated primarily due to high credit utilization (64%) and a declining balance trend over the past 30 days. Your upcoming EMI also adds to the financial pressure. Consider reducing discretionary spending and prioritizing debt repayment.',
  'How can I reduce my debt?': 'Here are some strategies: 1) Focus on paying off high-interest debt first, 2) Avoid taking on new debt, 3) Consider consolidating multiple debts, 4) Set up automatic payments to avoid missed EMIs, 5) Review your monthly budget for areas to cut.',
  'What is affecting my health score?': 'Your financial health score of 72 is affected by: positive consistent income, no recent missed payments, and good account diversification. However, high credit utilization (64%) and declining balance are pulling the score down.',
};

const DEMO_HISTORY = [];

export default function AIAssistant() {
  const [messages, setMessages] = useState(DEMO_HISTORY);
  const [loading, setLoading] = useState(false);
  const [isDemo, setIsDemo] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await aiAPI.getHistory();
      const history = Array.isArray(res.data) ? res.data : (res.data?.data || res.data?.messages || []);
      setMessages(history.length > 0 ? history : DEMO_HISTORY);
    } catch {
      setIsDemo(true);
    }
  };

  const handleSendMessage = async (message) => {
    const userMsg = { role: 'user', content: message };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await aiAPI.chat(message);
      const assistantMsg = {
        role: 'assistant',
        content: res.data?.data?.response || res.data?.response || res.data?.message || 'I can help you understand your financial health. Please ask a specific question.',
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      const fallback = DEMO_RESPONSES[message] || `Based on your current financial profile, I can see that your financial health score is 72 (Good). Your main areas to watch are credit utilization (currently at 64%) and your declining balance trend. I recommend reviewing your monthly expenses and considering strategies to reduce your credit utilization below 30%. Would you like specific guidance on any of these areas?`;
      setMessages((prev) => [...prev, { role: 'assistant', content: fallback }]);
      setIsDemo(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 p-4 md:p-6 lg:p-8 max-w-5xl">
      <div className="mb-4">
        <div className="flex items-center gap-3 mb-1">
          <Bot className="w-6 h-6 text-brand-600" />
          <h1 className="page-title">AI Assistant</h1>
        </div>
        <p className="page-subtitle">Ask questions about your financial health and get personalized guidance</p>
      </div>

      {isDemo && (
        <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-xl text-sm text-amber-700">
          <strong>Demo Mode:</strong> The AI assistant is using pre-built responses. Connect to the backend LLM service for real AI-powered conversations.
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
