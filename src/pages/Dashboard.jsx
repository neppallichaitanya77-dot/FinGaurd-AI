import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, ArrowRight, TrendingUp, TrendingDown } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { dashboardAPI } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import HealthScore from '../components/HealthScore';
import RiskCard from '../components/RiskCard';
import FinancialSummary from '../components/FinancialSummary';
import BalanceChart from '../components/BalanceChart';
import ExpenseChart from '../components/ExpenseChart';
import DebtChart from '../components/DebtChart';
import AlertCard from '../components/AlertCard';
import RecommendationCard from '../components/RecommendationCard';

const DEMO_DATA = {
  health_score: 72,
  health_status: 'Good',
  risk_score: 45,
  risk_level: 'MEDIUM',
  risk_factors: [
    { name: 'Credit utilization increased', value: '64%', impact: 'HIGH' },
    { name: 'Account balance declining', value: 'Last 30 days', impact: 'MEDIUM' },
    { name: 'Upcoming EMI', value: '₹8,500', impact: 'MEDIUM' },
  ],
  balance: 85400,
  income: 45000,
  expenses: 31500,
  debt: 125000,
  credit_utilization: 64,
  upcoming_emi: 8500,
  alerts: [
    { id: 1, title: 'Upcoming EMI Pressure', description: 'Your upcoming EMI may reduce your available balance significantly. Would you like to review your options?', severity: 'medium', created_at: '2026-09-01', status: 'unread', recommended_action: 'Review your cash flow and available balance before the payment date.' },
    { id: 2, title: 'Increasing Credit Utilization', description: 'Your credit utilization has increased over the past month. Consider reviewing your spending patterns.', severity: 'high', created_at: '2026-08-28', status: 'unread', recommended_action: 'Aim to keep utilization below 30% for optimal financial health.' },
  ],
  recommendations: [
    { id: 1, title: 'Reduce Credit Utilization', description: 'Your current utilization is relatively high. Consider reviewing discretionary spending and prioritizing high-cost debt.', priority: 'high', category: 'Debt Management', status: 'pending' },
    { id: 2, title: 'Budget Planning', description: 'Your monthly expenses increased compared with the previous month. Creating a budget can help manage spending.', priority: 'medium', category: 'Budgeting', status: 'pending' },
    { id: 3, title: 'Emergency Fund', description: 'Building an emergency fund can provide a safety net for unexpected expenses.', priority: 'low', category: 'Savings', status: 'pending' },
  ],
  balance_chart: Array.from({ length: 30 }, (_, i) => ({
    date: `2026-08-${String(i + 1).padStart(2, '0')}`,
    balance: 95000 - i * 350 + Math.floor(Math.random() * 5000),
  })),
  expense_chart: [
    { month: 'Apr', income: 45000, expenses: 28000 },
    { month: 'May', income: 45000, expenses: 30200 },
    { month: 'Jun', income: 45000, expenses: 29500 },
    { month: 'Jul', income: 45000, expenses: 31000 },
    { month: 'Aug', income: 45000, expenses: 31500 },
  ],
  debt_chart: Array.from({ length: 30 }, (_, i) => ({
    date: `2026-08-${String(i + 1).padStart(2, '0')}`,
    debt: 120000 + i * 170 + Math.floor(Math.random() * 2000),
  })),
};

export default function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isDemo, setIsDemo] = useState(false);
  const [timeRange, setTimeRange] = useState('30d');

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    setLoading(true);
    try {
      const response = await dashboardAPI.getSummary();
      setData(response.data?.data || response.data);
    } catch (err) {
      console.error('Dashboard API error:', err);
      setData(DEMO_DATA);
      setIsDemo(true);
      setError('Unable to connect to server. Showing demo data.');
    } finally {
      setLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[60vh]">
        <LoadingSpinner size="lg" text="Loading your dashboard..." />
      </div>
    );
  }

  const dashboardData = data || DEMO_DATA;

  return (
    <div className="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl">
      {isDemo && (
        <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl text-sm text-amber-700">
          <strong>Demo Mode:</strong> {error} The data shown is simulated for demonstration purposes.
        </div>
      )}

      <div className="mb-8">
        <h1 className="page-title">
          {getGreeting()}, {user?.name || 'there'}
        </h1>
        <p className="page-subtitle">Here's your financial wellness overview</p>
      </div>

      {dashboardData.risk_level === 'HIGH' && (
        <div className="mb-6 p-4 bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-xl">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-amber-800 text-sm">We noticed a possible financial pressure.</h3>
              <p className="text-sm text-amber-700 mt-1">
                Your balance is decreasing while credit utilization is increasing, and an EMI is approaching.
                Would you like to review your options?
              </p>
              <div className="flex gap-2 mt-3">
                <Link to="/recommendations" className="px-4 py-1.5 text-xs font-medium bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors">
                  Review Options
                </Link>
                <button className="px-4 py-1.5 text-xs font-medium text-amber-700 hover:bg-amber-100 rounded-lg transition-colors">
                  Not Now
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-1 card flex items-center justify-center">
          <HealthScore score={dashboardData.health_score} status={dashboardData.health_status} />
        </div>
        <div className="lg:col-span-2">
          <RiskCard
            riskScore={dashboardData.risk_score}
            riskLevel={dashboardData.risk_level}
            riskFactors={dashboardData.risk_factors}
          />
        </div>
      </div>

      <div className="mb-6">
        <FinancialSummary
          data={{
            balance: dashboardData.balance,
            income: dashboardData.income,
            expenses: dashboardData.expenses,
            debt: dashboardData.debt,
            utilization: dashboardData.credit_utilization,
            emi: dashboardData.upcoming_emi,
          }}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <BalanceChart data={dashboardData.balance_chart} timeRange={timeRange} onTimeRangeChange={setTimeRange} />
        <ExpenseChart data={dashboardData.expense_chart} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <DebtChart data={dashboardData.debt_chart} />

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Recent Alerts</h3>
            <Link to="/alerts" className="text-sm text-brand-600 hover:text-brand-700 flex items-center gap-1">
              View all <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
          <div className="space-y-3">
            {dashboardData.alerts?.slice(0, 3).map((alert) => (
              <AlertCard key={alert.id} alert={alert} />
            ))}
            {(!dashboardData.alerts || dashboardData.alerts.length === 0) && (
              <p className="text-sm text-gray-400 text-center py-6">No alerts at this time</p>
            )}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Recommendations</h3>
          <Link to="/recommendations" className="text-sm text-brand-600 hover:text-brand-700 flex items-center gap-1">
            View all <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {dashboardData.recommendations?.slice(0, 3).map((rec) => (
            <RecommendationCard key={rec.id} recommendation={rec} />
          ))}
          {(!dashboardData.recommendations || dashboardData.recommendations.length === 0) && (
            <p className="text-sm text-gray-400 text-center py-6 col-span-3">No recommendations at this time</p>
          )}
        </div>
      </div>
    </div>
  );
}
