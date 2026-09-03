import { getRiskBadgeClass } from '../utils/helpers';

export default function RiskCard({ riskScore = 0, riskLevel = 'LOW', riskFactors = [], loading = false }) {
  if (loading) {
    return (
      <div className="card animate-pulse">
        <div className="h-6 bg-gray-100 rounded w-40 mb-4" />
        <div className="h-10 bg-gray-100 rounded w-24 mb-4" />
        <div className="space-y-3">
          <div className="h-4 bg-gray-100 rounded w-full" />
          <div className="h-4 bg-gray-100 rounded w-3/4" />
        </div>
      </div>
    );
  }

  const getImpactBadge = (impact) => {
    switch (impact?.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-700';
      case 'medium': return 'bg-amber-100 text-amber-700';
      case 'low': return 'bg-emerald-100 text-emerald-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Risk Level</h3>
      <div className="flex items-center gap-3 mb-4">
        <span className={`px-4 py-1.5 rounded-full text-sm font-bold ${getRiskBadgeClass(riskLevel)}`}>
          {riskLevel}
        </span>
        <span className="text-sm text-gray-500">Risk Score: {riskScore}</span>
      </div>
      {riskFactors.length > 0 && (
        <div>
          <p className="text-sm font-medium text-gray-700 mb-3">Main Factors:</p>
          <div className="space-y-2">
            {riskFactors.map((factor, i) => (
              <div key={i} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg">
                <div>
                  <span className="text-sm text-gray-700">{factor.name}</span>
                  {factor.value && <span className="text-xs text-gray-400 ml-2">({factor.value})</span>}
                </div>
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${getImpactBadge(factor.impact)}`}>
                  {factor.impact}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
