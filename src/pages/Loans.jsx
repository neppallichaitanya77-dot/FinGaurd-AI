import { useState, useEffect } from 'react';
import { Landmark, Calendar, Clock, TrendingDown } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { loansAPI } from '../services/api';
import { formatCurrency, formatDate } from '../utils/helpers';
import LoadingSpinner from '../components/LoadingSpinner';

const DEMO_LOANS = [
  {
    id: 1,
    name: 'Home Loan',
    outstanding: 850000,
    interest_rate: 8.5,
    emi: 8500,
    next_payment: '2026-09-15',
    remaining_tenure: 120,
    total_tenure: 240,
    payments: Array.from({ length: 12 }, (_, i) => ({
      month: `M${i + 1}`,
      principal: 3200 + i * 50,
      interest: 5300 - i * 30,
    })),
  },
  {
    id: 2,
    name: 'Personal Loan',
    outstanding: 125000,
    interest_rate: 12.0,
    emi: 4200,
    next_payment: '2026-09-20',
    remaining_tenure: 32,
    total_tenure: 48,
    payments: Array.from({ length: 12 }, (_, i) => ({
      month: `M${i + 1}`,
      principal: 2800 + i * 40,
      interest: 1400 - i * 35,
    })),
  },
  {
    id: 3,
    name: 'Car Loan',
    outstanding: 275000,
    interest_rate: 9.0,
    emi: 6800,
    next_payment: '2026-09-10',
    remaining_tenure: 48,
    total_tenure: 60,
    payments: Array.from({ length: 12 }, (_, i) => ({
      month: `M${i + 1}`,
      principal: 4100 + i * 30,
      interest: 2700 - i * 40,
    })),
  },
];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white px-3 py-2 rounded-lg shadow-lg border border-gray-100">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="text-xs font-medium" style={{ color: p.fill }}>
          {p.name}: {formatCurrency(p.value)}
        </p>
      ))}
    </div>
  );
};

export default function Loans() {
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLoan, setSelectedLoan] = useState(null);

  useEffect(() => { fetchLoans(); }, []);

  const fetchLoans = async () => {
    try {
      const res = await loansAPI.getLoans();
      const data = res.data?.data || res.data?.loans || res.data;
      setLoans(data);
      if (data.length > 0) setSelectedLoan(data[0].id);
    } catch {
      setLoans(DEMO_LOANS);
      setSelectedLoan(DEMO_LOANS[0].id);
    } finally {
      setLoading(false);
    }
  };

  const currentLoan = loans.find((l) => l.id === selectedLoan);

  if (loading) return <div className="flex-1 p-8"><LoadingSpinner text="Loading loans..." /></div>;

  return (
    <div className="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-1">
          <Landmark className="w-6 h-6 text-brand-600" />
          <h1 className="page-title">Loans & EMI</h1>
        </div>
        <p className="page-subtitle">Track your active loans and repayment progress</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {loans.map((loan) => (
          <button
            key={loan.id}
            onClick={() => setSelectedLoan(loan.id)}
            className={`card text-left transition-all ${selectedLoan === loan.id ? 'ring-2 ring-brand-500 border-brand-200' : ''}`}
          >
            <h3 className="font-semibold text-gray-900 mb-2">{loan.name}</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Outstanding</span>
                <span className="font-medium text-gray-900">{formatCurrency(loan.outstanding ?? loan.outstanding_amount)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Interest Rate</span>
                <span className="font-medium text-gray-900">{loan.interest_rate}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Monthly EMI</span>
                <span className="font-semibold text-brand-600">{formatCurrency(loan.emi ?? loan.monthly_emi)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Next Payment</span>
                <span className="font-medium text-gray-900">{formatDate(loan.next_payment ?? loan.next_payment_date)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Remaining</span>
                <span className="font-medium text-gray-900">{loan.remaining_tenure} months</span>
              </div>
            </div>
            <div className="mt-3 h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-brand-500 rounded-full transition-all"
                style={{ width: `${((loan.total_tenure - loan.remaining_tenure) / loan.total_tenure) * 100}%` }}
              />
            </div>
            <p className="text-xs text-gray-400 mt-1 text-right">
              {Math.round(((loan.total_tenure - loan.remaining_tenure) / loan.total_tenure) * 100)}% paid
            </p>
          </button>
        ))}
      </div>

      {currentLoan && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Repayment Timeline — {currentLoan.name}
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={currentLoan.payments} barGap={2}>
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#94a3b8' }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} tickLine={false} axisLine={false} tickFormatter={(v) => `₹${(v/1000).toFixed(1)}k`} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="principal" name="Principal" fill="#1a6af5" stackId="a" radius={[0, 0, 0, 0]} />
                <Bar dataKey="interest" name="Interest" fill="#d97706" stackId="a" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-6 mt-4">
            <span className="flex items-center gap-2 text-xs text-gray-500">
              <span className="w-3 h-3 rounded-sm bg-brand-600" /> Principal
            </span>
            <span className="flex items-center gap-2 text-xs text-gray-500">
              <span className="w-3 h-3 rounded-sm bg-amber-500" /> Interest
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
