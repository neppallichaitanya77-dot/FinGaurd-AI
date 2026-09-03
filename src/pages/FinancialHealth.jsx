import { useState, useEffect } from 'react';
import { HeartPulse, TrendingUp, TrendingDown, AlertCircle, CheckCircle } from 'lucide-react';
import { financialHealthAPI } from '../services/api';
import { formatCurrency } from '../utils/helpers';
import HealthScore from '../components/HealthScore';
import BalanceChart from '../components/BalanceChart';
import ExpenseChart from '../components/ExpenseChart';
import DebtChart from '../components/DebtChart';
import LoadingSpinner from '../components/LoadingSpinner';

const DEMO_DATA = {
  health_score: 72,
  health_status: 'Good',
  balance: 85400,
  income: 45000,
  expenses: 31500,
  debt: 125000,
  credit_utilization: 64,
  upcoming_emi: 8500,
  positive_factors: [
    'Consistent monthly income',
    'No missed payments in the last 6 months',
    'Diversified expense categories',
  ],
  concerns: [
    'Credit utilization is above the recommended 30% threshold',
    'Monthly expenses are trending upward',
    'Balance has been declining over the past 30 days',
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

export default function FinancialHealth() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30d');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const res = await financialHealthAPI.getHealth();
      setData(res.data?.data || res.data);
    } catch {
      setData(DEMO_DATA);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="flex-1 p-8"><LoadingSpinner text="Loading financial health..." /></div>;
  const d = data || DEMO_DATA;

  return (
    <div className="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-1">
          <HeartPulse className="w-6 h-6 text-brand-600" />
          <h1 className="page-title">Financial Health</h1>
        </div>
        <p className="page-subtitle">A comprehensive view of your financial wellness</p>
      </div>

      <div className="card mb-6 flex justify-center">
        <HealthScore score={d.health_score ?? d.financial_health_score} status={d.health_status ?? d.financial_health_status} />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
        {[
          { label: 'Balance', value: formatCurrency(d.balance), color: 'text-brand-600' },
          { label: 'Income', value: formatCurrency(d.income), color: 'text-emerald-600' },
          { label: 'Expenses', value: formatCurrency(d.expenses), color: 'text-amber-600' },
          { label: 'Debt', value: formatCurrency(d.debt), color: 'text-red-600' },
          { label: 'Utilization', value: `${d.credit_utilization}%`, color: 'text-purple-600' },
          { label: 'EMI', value: formatCurrency(d.upcoming_emi), color: 'text-orange-600' },
        ].map((item) => (
          <div key={item.label} className="card text-center">
            <p className="text-xs text-gray-400 uppercase tracking-wide">{item.label}</p>
            <p className={`text-lg font-bold mt-1 ${item.color}`}>{item.value}</p>
          </div>
        ))}
      </div>

      <div className="mb-6">
        <BalanceChart data={d.balance_chart} timeRange={timeRange} onTimeRangeChange={setTimeRange} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <ExpenseChart data={d.expense_chart} />
        <DebtChart data={d.debt_chart} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle className="w-5 h-5 text-emerald-500" />
            <h3 className="font-semibold text-gray-900">Positive Factors</h3>
          </div>
          <ul className="space-y-2">
            {(d.positive_factors ?? d.key_positive_factors)?.map((f, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-1.5 flex-shrink-0" />
                {f}
              </li>
            ))}
          </ul>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="w-5 h-5 text-amber-500" />
            <h3 className="font-semibold text-gray-900">Areas of Concern</h3>
          </div>
          <ul className="space-y-2">
            {(d.concerns ?? d.key_concerns)?.map((c, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                <span className="w-1.5 h-1.5 bg-amber-500 rounded-full mt-1.5 flex-shrink-0" />
                {c}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
