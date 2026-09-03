import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { formatDate } from '../utils/helpers';

const timeRanges = [
  { value: '7d', label: '7 Days' },
  { value: '30d', label: '30 Days' },
  { value: '3m', label: '3 Months' },
  { value: '6m', label: '6 Months' },
];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white px-3 py-2 rounded-lg shadow-lg border border-gray-100">
      <p className="text-xs text-gray-500">{formatDate(label)}</p>
      <p className="text-sm font-semibold text-brand-700">₹{payload[0].value?.toLocaleString('en-IN')}</p>
    </div>
  );
};

export default function BalanceChart({ data = [], timeRange = '30d', onTimeRangeChange, loading }) {
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
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Balance Trend</h3>
        <div className="flex gap-1 bg-gray-50 p-1 rounded-lg">
          {timeRanges.map((r) => (
            <button
              key={r.value}
              onClick={() => onTimeRangeChange?.(r.value)}
              className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                timeRange === r.value
                  ? 'bg-white text-brand-700 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="balanceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#1a6af5" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#1a6af5" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#94a3b8' }} tickLine={false} axisLine={false} tickFormatter={(v) => formatDate(v)} />
            <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} tickLine={false} axisLine={false} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k`} />
            <Tooltip content={<CustomTooltip />} />
            <Area type="monotone" dataKey="balance" stroke="#1a6af5" fill="url(#balanceGradient)" strokeWidth={2.5} dot={false} activeDot={{ r: 5, fill: '#1a6af5' }} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
