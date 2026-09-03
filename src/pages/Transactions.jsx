import { useState, useEffect } from 'react';
import { ArrowLeftRight, Search, ChevronUp, ChevronDown, ChevronLeft, ChevronRight } from 'lucide-react';
import { transactionsAPI } from '../services/api';
import { formatCurrency, formatDate } from '../utils/helpers';
import LoadingSpinner from '../components/LoadingSpinner';

const DEMO_TRANSACTIONS = [
  { id: 1, date: '2026-09-01', description: 'Salary Credit', category: 'Income', amount: 45000, type: 'credit', balance: 85400 },
  { id: 2, date: '2026-08-30', description: 'Grocery Store', category: 'Groceries', amount: -3200, type: 'debit', balance: 40400 },
  { id: 3, date: '2026-08-29', description: 'Electricity Bill', category: 'Utilities', amount: -1800, type: 'debit', balance: 43600 },
  { id: 4, date: '2026-08-28', description: 'Restaurant', category: 'Food & Dining', amount: -2400, type: 'debit', balance: 45400 },
  { id: 5, date: '2026-08-27', description: 'Freelance Payment', category: 'Income', amount: 12000, type: 'credit', balance: 47800 },
  { id: 6, date: '2026-08-26', description: 'Online Shopping', category: 'Shopping', amount: -4500, type: 'debit', balance: 35800 },
  { id: 7, date: '2026-08-25', description: 'Netflix Subscription', category: 'Entertainment', amount: -649, type: 'debit', balance: 40300 },
  { id: 8, date: '2026-08-24', description: 'Petrol', category: 'Transport', amount: -2200, type: 'debit', balance: 40949 },
  { id: 9, date: '2026-08-23', description: 'Medical Expense', category: 'Healthcare', amount: -1500, type: 'debit', balance: 43149 },
  { id: 10, date: '2026-08-22', description: 'ATM Withdrawal', category: 'Cash', amount: -5000, type: 'debit', balance: 44649 },
  { id: 11, date: '2026-08-21', description: 'Insurance Premium', category: 'Insurance', amount: -3500, type: 'debit', balance: 49649 },
  { id: 12, date: '2026-08-20', description: 'Mobile Recharge', category: 'Utilities', amount: -599, type: 'debit', balance: 53149 },
];

const itemsPerPage = 8;

export default function Transactions() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('All');
  const [sortField, setSortField] = useState('date');
  const [sortDir, setSortDir] = useState('desc');
  const [page, setPage] = useState(1);

  useEffect(() => { fetchTransactions(); }, []);

  const fetchTransactions = async () => {
    try {
      const res = await transactionsAPI.getTransactions();
      setTransactions(res.data?.data || res.data?.transactions || res.data);
    } catch {
      setTransactions(DEMO_TRANSACTIONS);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field) => {
    if (sortField === field) setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    else { setSortField(field); setSortDir('desc'); }
  };

  const SortIcon = ({ field }) => {
    if (sortField !== field) return <ChevronUp className="w-3 h-3 text-gray-300" />;
    return sortDir === 'asc' ? <ChevronUp className="w-3 h-3 text-brand-600" /> : <ChevronDown className="w-3 h-3 text-brand-600" />;
  };

  const filtered = transactions
    .filter((t) => {
      if (search && !t.description.toLowerCase().includes(search.toLowerCase()) && !t.category.toLowerCase().includes(search.toLowerCase())) return false;
      if (typeFilter === 'Income' && t.type !== 'credit') return false;
      if (typeFilter === 'Expense' && t.type !== 'debit') return false;
      return true;
    })
    .sort((a, b) => {
      let cmp = 0;
      if (sortField === 'date') cmp = new Date(a.date) - new Date(b.date);
      else if (sortField === 'amount') cmp = a.amount - b.amount;
      else if (sortField === 'description') cmp = a.description.localeCompare(b.description);
      else if (sortField === 'balance') cmp = a.balance - b.balance;
      return sortDir === 'asc' ? cmp : -cmp;
    });

  const totalPages = Math.ceil(filtered.length / itemsPerPage);
  const paginated = filtered.slice((page - 1) * itemsPerPage, page * itemsPerPage);

  return (
    <div className="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-1">
          <ArrowLeftRight className="w-6 h-6 text-brand-600" />
          <h1 className="page-title">Transactions</h1>
        </div>
        <p className="page-subtitle">View and manage your transaction history</p>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder="Search transactions..."
            className="input-field pl-11"
          />
        </div>
        <select
          value={typeFilter}
          onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
          className="input-field w-auto"
        >
          <option>All</option>
          <option>Income</option>
          <option>Expense</option>
        </select>
      </div>

      {loading ? (
        <LoadingSpinner text="Loading transactions..." />
      ) : (
        <>
          <div className="card overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  {[
                    { key: 'date', label: 'Date' },
                    { key: 'description', label: 'Description' },
                    { key: 'category', label: 'Category' },
                    { key: 'amount', label: 'Amount' },
                    { key: 'balance', label: 'Balance' },
                  ].map(({ key, label }) => (
                    <th
                      key={key}
                      onClick={() => handleSort(key)}
                      className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wide cursor-pointer hover:text-gray-700"
                    >
                      <span className="flex items-center gap-1">
                        {label} <SortIcon field={key} />
                      </span>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {paginated.map((t) => (
                  <tr key={t.id} className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors">
                    <td className="py-3 px-4 text-gray-500">{formatDate(t.date)}</td>
                    <td className="py-3 px-4 font-medium text-gray-900">{t.description}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-1 text-xs rounded-md bg-gray-100 text-gray-600">{t.category}</span>
                    </td>
                    <td className={`py-3 px-4 font-semibold ${t.amount >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                      {t.amount >= 0 ? '+' : ''}{formatCurrency(Math.abs(t.amount))}
                    </td>
                    <td className="py-3 px-4 text-gray-700">{formatCurrency(t.balance)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4">
              <p className="text-sm text-gray-500">
                Showing {((page - 1) * itemsPerPage) + 1}-{Math.min(page * itemsPerPage, filtered.length)} of {filtered.length}
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-30"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page === totalPages}
                  className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-30"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
