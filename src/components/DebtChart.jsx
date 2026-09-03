import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { formatDate, formatCurrency } from '../utils/helpers';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white px-3 py-2 rounded-lg shadow-lg border border-gray-100">
      <p className="text-xs text-gray-500">{formatDate(label)}</p>
      <p className="text-sm font-semibold text-orange-600">{formatCurrency(payload[0].value)}</p>
    </div>
  );
};

export default function DebtChart({ data = [], loading }) {
  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="h-6 bg-gray-100 rounded w-40 mb-4" />
        <div className="h-64 bg-gray-50 rounded-xl" />
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Debt Trend</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#94a3b8' }} tickLine={false} axisLine={false} tickFormatter={(v) => formatDate(v)} />
            <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} tickLine={false} axisLine={false} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k`} />
            <Tooltip content={<CustomTooltip />} />
            <Line type="monotone" dataKey="debt" stroke="#ea580c" strokeWidth={2.5} dot={false} activeDot={{ r: 5, fill: '#ea580c' }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
