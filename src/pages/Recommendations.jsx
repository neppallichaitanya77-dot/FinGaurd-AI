import { useState, useEffect } from 'react';
import { Lightbulb } from 'lucide-react';
import { recommendationsAPI } from '../services/api';
import RecommendationCard from '../components/RecommendationCard';
import LoadingSpinner from '../components/LoadingSpinner';

const DEMO_RECS = [
  { id: 1, title: 'Reduce Credit Utilization', description: 'Your current utilization is 64%, which is above the recommended 30%. Review discretionary spending and consider prioritizing high-cost debt repayment.', priority: 'high', category: 'Debt Management', status: 'pending' },
  { id: 2, title: 'Upcoming EMI Planning', description: 'Your next EMI of ₹8,500 may place pressure on your balance. Review your upcoming cash flow and plan accordingly.', priority: 'high', category: 'Cash Flow', status: 'pending' },
  { id: 3, title: 'Budget Planning', description: 'Your monthly expenses increased compared with the previous month. Creating a detailed budget can help manage spending more effectively.', priority: 'medium', category: 'Budgeting', status: 'pending' },
  { id: 4, title: 'Build Emergency Fund', description: 'Building an emergency fund equivalent to 3-6 months of expenses can provide a financial safety net for unexpected situations.', priority: 'medium', category: 'Savings', status: 'pending' },
  { id: 5, title: 'Review Subscription Services', description: 'Review recurring subscriptions and services to identify potential savings opportunities.', priority: 'low', category: 'Expense Optimization', status: 'pending' },
  { id: 6, title: 'Set Financial Goals', description: 'Define short-term and long-term financial goals to create a roadmap for your financial wellness journey.', priority: 'low', category: 'Planning', status: 'pending' },
];

const filters = ['All', 'High Priority', 'Medium Priority', 'Low Priority'];

export default function Recommendations() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState('All');

  useEffect(() => { fetchRecs(); }, []);

  const fetchRecs = async () => {
    try {
      const res = await recommendationsAPI.getRecommendations();
      setRecommendations(res.data?.data || res.data?.recommendations || res.data);
    } catch {
      setRecommendations(DEMO_RECS);
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (id) => {
    try { await recommendationsAPI.acceptRecommendation(id); } catch {}
    setRecommendations((prev) => prev.map((r) => r.id === id ? { ...r, status: 'accepted' } : r));
  };

  const handleDismiss = async (id) => {
    try { await recommendationsAPI.dismissRecommendation(id); } catch {}
    setRecommendations((prev) => prev.map((r) => r.id === id ? { ...r, status: 'dismissed' } : r));
  };

  const filtered = recommendations.filter((r) => {
    if (activeFilter === 'All') return true;
    if (activeFilter === 'High Priority') return r.priority === 'high';
    if (activeFilter === 'Medium Priority') return r.priority === 'medium';
    if (activeFilter === 'Low Priority') return r.priority === 'low';
    return true;
  });

  return (
    <div className="flex-1 p-4 md:p-6 lg:p-8 max-w-5xl">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-1">
          <Lightbulb className="w-6 h-6 text-amber-500" />
          <h1 className="page-title">Personalized Financial Guidance</h1>
        </div>
        <p className="page-subtitle">Supportive suggestions to improve your financial wellness</p>
      </div>

      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {filters.map((f) => (
          <button
            key={f}
            onClick={() => setActiveFilter(f)}
            className={`px-4 py-2 text-sm font-medium rounded-xl whitespace-nowrap transition-colors ${
              activeFilter === f ? 'bg-brand-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingSpinner text="Loading recommendations..." />
      ) : filtered.length === 0 ? (
        <div className="card text-center py-12">
          <Lightbulb className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No recommendations match your filter</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((rec) => (
            <RecommendationCard key={rec.id} recommendation={rec} onAccept={handleAccept} onDismiss={handleDismiss} />
          ))}
        </div>
      )}

      <div className="mt-8 p-4 bg-brand-50 rounded-xl border border-brand-100">
        <p className="text-sm text-brand-700 text-center">
          All recommendations are supportive guidance. You are always in control of which actions to take.
        </p>
      </div>
    </div>
  );
}
