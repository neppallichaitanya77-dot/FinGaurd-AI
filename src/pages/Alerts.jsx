import { useState, useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';
import { alertsAPI } from '../services/api';
import AlertCard from '../components/AlertCard';
import LoadingSpinner from '../components/LoadingSpinner';

const DEMO_ALERTS = [
  { id: 1, title: 'Upcoming EMI Pressure', description: 'Your upcoming EMI of ₹8,500 may reduce your available balance significantly. Would you like to review your options?', severity: 'medium', created_at: '2026-09-01', status: 'unread', recommended_action: 'Review your cash flow and available balance before the payment date.' },
  { id: 2, title: 'High Credit Utilization', description: 'Your credit utilization has increased to 64%. This is above the recommended 30% threshold and may affect your financial health.', severity: 'high', created_at: '2026-08-28', status: 'unread', recommended_action: 'Consider reducing discretionary spending or prioritizing debt repayment.' },
  { id: 3, title: 'Declining Account Balance', description: 'Your account balance has been declining over the past 30 days. This trend may impact your ability to cover upcoming expenses.', severity: 'medium', created_at: '2026-08-25', status: 'read', recommended_action: 'Review your income and expense patterns to identify areas for adjustment.' },
  { id: 4, title: 'Increasing Monthly Expenses', description: 'Your expenses this month are higher than your 3-month average. Consider reviewing your spending categories.', severity: 'low', created_at: '2026-08-20', status: 'read', recommended_action: 'Track your spending by category to identify non-essential expenses.' },
  { id: 5, title: 'Unusual Spending Pattern', description: 'We detected an unusual spending pattern in the last week. This may be normal but worth reviewing.', severity: 'low', created_at: '2026-08-18', status: 'read', recommended_action: 'Review recent transactions to ensure all charges are expected.' },
];

const filters = ['All', 'Unread', 'High', 'Medium', 'Low'];

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState('All');

  useEffect(() => { fetchAlerts(); }, []);

  const fetchAlerts = async () => {
    try {
      const res = await alertsAPI.getAlerts();
      setAlerts(res.data?.data || res.data?.alerts || res.data);
    } catch {
      setAlerts(DEMO_ALERTS);
    } finally {
      setLoading(false);
    }
  };

  const handleRead = async (id) => {
    try { await alertsAPI.markAsRead(id); } catch {}
    setAlerts((prev) => prev.map((a) => a.id === id ? { ...a, status: 'read' } : a));
  };

  const handleDismiss = async (id) => {
    try { await alertsAPI.dismissAlert(id); } catch {}
    setAlerts((prev) => prev.filter((a) => a.id !== id));
  };

  const filtered = alerts.filter((a) => {
    if (activeFilter === 'All') return true;
    if (activeFilter === 'Unread') return a.status !== 'read';
    return a.severity?.toLowerCase() === activeFilter.toLowerCase();
  });

  return (
    <div className="flex-1 p-4 md:p-6 lg:p-8 max-w-5xl">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-1">
          <AlertTriangle className="w-6 h-6 text-amber-500" />
          <h1 className="page-title">Early Warning Alerts</h1>
        </div>
        <p className="page-subtitle">Stay informed about your financial indicators</p>
      </div>

      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {filters.map((f) => (
          <button
            key={f}
            onClick={() => setActiveFilter(f)}
            className={`px-4 py-2 text-sm font-medium rounded-xl whitespace-nowrap transition-colors ${
              activeFilter === f
                ? 'bg-brand-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {f}
            {f === 'Unread' && ` (${alerts.filter((a) => a.status !== 'read').length})`}
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingSpinner text="Loading alerts..." />
      ) : filtered.length === 0 ? (
        <div className="card text-center py-12">
          <AlertTriangle className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No alerts match your filter</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filtered.map((alert) => (
            <AlertCard key={alert.id} alert={alert} onRead={handleRead} onDismiss={handleDismiss} />
          ))}
        </div>
      )}
    </div>
  );
}
