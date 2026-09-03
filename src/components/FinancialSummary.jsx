import { Wallet, TrendingUp, TrendingDown, CreditCard, Percent, CalendarClock } from 'lucide-react';
import { formatCurrency } from '../utils/helpers';

const cards = [
  { key: 'balance', label: 'Total Balance', icon: Wallet, color: 'text-brand-600 bg-brand-50', format: 'currency' },
  { key: 'income', label: 'Monthly Income', icon: TrendingUp, color: 'text-emerald-600 bg-emerald-50', format: 'currency' },
  { key: 'expenses', label: 'Monthly Expenses', icon: TrendingDown, color: 'text-amber-600 bg-amber-50', format: 'currency' },
  { key: 'debt', label: 'Outstanding Debt', icon: CreditCard, color: 'text-orange-600 bg-orange-50', format: 'currency' },
  { key: 'utilization', label: 'Credit Utilization', icon: Percent, color: 'text-purple-600 bg-purple-50', format: 'percent' },
  { key: 'emi', label: 'Upcoming EMI', icon: CalendarClock, color: 'text-red-600 bg-red-50', format: 'currency' },
];

export default function FinancialSummary({ data = {}, loading = false }) {
  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="card animate-pulse">
            <div className="h-10 w-10 bg-gray-100 rounded-xl mb-3" />
            <div className="h-3 bg-gray-100 rounded w-24 mb-2" />
            <div className="h-6 bg-gray-100 rounded w-20" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      {cards.map(({ key, label, icon: Icon, color, format }) => (
        <div key={key} className="card">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${color}`}>
            <Icon className="w-5 h-5" />
          </div>
          <p className="text-sm text-gray-500">{label}</p>
          <div className="mt-1">
            {format === 'percent' ? (
              <div>
                <span className="text-xl font-bold text-gray-900">{data[key] || 0}%</span>
                <div className="mt-2 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      (data[key] || 0) > 70 ? 'bg-red-500' : (data[key] || 0) > 40 ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.min(data[key] || 0, 100)}%` }}
                  />
                </div>
              </div>
            ) : (
              <span className="text-xl font-bold text-gray-900">{formatCurrency(data[key])}</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
