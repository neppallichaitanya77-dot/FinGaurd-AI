import { useState } from 'react';
import { FlaskConical, Play, Loader2, AlertTriangle, CheckCircle } from 'lucide-react';
import { scenarioAPI } from '../services/api';
import HealthScore from '../components/HealthScore';
import { formatCurrency, getRiskBadgeClass, getScoreColor } from '../utils/helpers';

const defaultScenario = {
  monthly_income: 45000,
  monthly_expenses: 32000,
  outstanding_debt: 120000,
  credit_utilization: 65,
  upcoming_emi: 8500,
  payment_delays: 1,
};

function calculateLocalRisk(data) {
  let riskScore = 0;
  const factors = [];

  const dti = ((data.monthly_expenses + data.upcoming_emi) / data.monthly_income) * 100;
  if (dti > 60) { riskScore += 25; factors.push({ name: 'High Debt-to-Income Ratio', value: `${dti.toFixed(0)}%`, impact: 'HIGH' }); }
  else if (dti > 40) { riskScore += 15; factors.push({ name: 'Elevated Debt-to-Income Ratio', value: `${dti.toFixed(0)}%`, impact: 'MEDIUM' }); }

  if (data.credit_utilization > 70) { riskScore += 25; factors.push({ name: 'High Credit Utilization', value: `${data.credit_utilization}%`, impact: 'HIGH' }); }
  else if (data.credit_utilization > 40) { riskScore += 12; factors.push({ name: 'Modererate Credit Utilization', value: `${data.credit_utilization}%`, impact: 'MEDIUM' }); }

  if (data.payment_delays > 3) { riskScore += 25; factors.push({ name: 'Frequent Payment Delays', value: `${data.payment_delays} delays`, impact: 'HIGH' }); }
  else if (data.payment_delays > 0) { riskScore += 10; factors.push({ name: 'Payment Delays Detected', value: `${data.payment_delays} delay(s)`, impact: 'MEDIUM' }); }

  const savingsRate = ((data.monthly_income - data.monthly_expenses) / data.monthly_income) * 100;
  if (savingsRate < 10) { riskScore += 15; factors.push({ name: 'Low Savings Rate', value: `${savingsRate.toFixed(0)}%`, impact: 'MEDIUM' }); }

  if (data.outstanding_debt > data.monthly_income * 24) { riskScore += 10; factors.push({ name: 'High Debt Burden', value: formatCurrency(data.outstanding_debt), impact: 'MEDIUM' }); }

  riskScore = Math.min(riskScore, 100);

  let riskLevel = 'LOW';
  if (riskScore > 60) riskLevel = 'HIGH';
  else if (riskScore > 30) riskLevel = 'MEDIUM';

  const healthScore = Math.max(100 - riskScore, 0);

  const recommendations = [];
  if (data.credit_utilization > 40) recommendations.push('Reduce credit utilization below 30%');
  if (dti > 40) recommendations.push('Work on reducing your debt-to-income ratio');
  if (data.payment_delays > 0) recommendations.push('Set up automatic payments to avoid future delays');
  if (savingsRate < 20) recommendations.push('Try to save at least 20% of your income');

  return { risk_score: riskScore, risk_level: riskLevel, health_score: healthScore, risk_factors: factors, recommendations };
}

export default function Scenarios() {
  const [scenario, setScenario] = useState(defaultScenario);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (field, value) => {
    setScenario((prev) => ({ ...prev, [field]: Number(value) }));
  };

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const res = await scenarioAPI.analyze(scenario);
      setResult(res.data?.data || res.data);
    } catch {
      setResult(calculateLocalRisk(scenario));
    } finally {
      setLoading(false);
    }
  };

  const sliders = [
    { key: 'monthly_income', label: 'Monthly Income', min: 5000, max: 200000, step: 1000, prefix: '₹' },
    { key: 'monthly_expenses', label: 'Monthly Expenses', min: 5000, max: 150000, step: 1000, prefix: '₹' },
    { key: 'outstanding_debt', label: 'Outstanding Debt', min: 0, max: 5000000, step: 5000, prefix: '₹' },
    { key: 'credit_utilization', label: 'Credit Utilization', min: 0, max: 100, step: 1, suffix: '%' },
    { key: 'upcoming_emi', label: 'Upcoming EMI', min: 0, max: 50000, step: 500, prefix: '₹' },
    { key: 'payment_delays', label: 'Payment Delays', min: 0, max: 10, step: 1 },
  ];

  return (
    <div className="flex-1 p-4 md:p-6 lg:p-8 max-w-5xl">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-1">
          <FlaskConical className="w-6 h-6 text-brand-600" />
          <h1 className="page-title">Risk Scenario Simulator</h1>
        </div>
        <p className="page-subtitle">Explore how different financial scenarios affect your risk assessment</p>
      </div>

      <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl text-sm text-amber-700 flex items-start gap-2">
        <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
        <div>
          <strong>Disclaimer:</strong> This simulator uses simulated data for demonstration purposes only. Results are approximations and should not be considered financial advice.
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4">Scenario Parameters</h3>
          <div className="space-y-5">
            {sliders.map(({ key, label, min, max, step, prefix, suffix }) => (
              <div key={key}>
                <div className="flex justify-between mb-1">
                  <label className="text-sm text-gray-600">{label}</label>
                  <span className="text-sm font-semibold text-gray-900">
                    {prefix}{scenario[key].toLocaleString('en-IN')}{suffix}
                  </span>
                </div>
                <input
                  type="range"
                  min={min}
                  max={max}
                  step={step}
                  value={scenario[key]}
                  onChange={(e) => handleChange(key, e.target.value)}
                  className="w-full h-2 bg-gray-200 rounded-full appearance-none cursor-pointer accent-brand-600"
                />
                <div className="flex justify-between mt-1">
                  <span className="text-[10px] text-gray-400">{prefix}{min.toLocaleString('en-IN')}{suffix}</span>
                  <span className="text-[10px] text-gray-400">{prefix}{max.toLocaleString('en-IN')}{suffix}</span>
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="btn-primary w-full mt-6 flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <><Play className="w-5 h-5" /> Analyze Scenario</>}
          </button>
        </div>

        <div>
          {result ? (
            <div className="space-y-4">
              <div className="card flex flex-col items-center">
                <HealthScore score={result.health_score || result.financial_health_score} status={result.risk_level ? `${result.risk_level} Risk` : ''} />
              </div>

              <div className="card">
                <h3 className="font-semibold text-gray-900 mb-3">Predicted Risk</h3>
                <div className="flex items-center gap-3 mb-4">
                  <span className={`px-4 py-1.5 rounded-full text-sm font-bold ${getRiskBadgeClass(result.risk_level)}`}>
                    {result.risk_level}
                  </span>
                  <span className="text-sm text-gray-500">Score: {result.risk_score}</span>
                </div>
              </div>

              {result.risk_factors?.length > 0 && (
                <div className="card">
                  <h3 className="font-semibold text-gray-900 mb-3">Major Risk Factors</h3>
                  <ul className="space-y-2">
                    {result.risk_factors.map((f, i) => (
                      <li key={i} className="flex items-center gap-2 text-sm text-gray-600">
                        <span className="w-1.5 h-1.5 bg-amber-500 rounded-full flex-shrink-0" />
                        {f.name} <span className="text-gray-400">({f.value})</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {result.recommendations?.length > 0 && (
                <div className="card">
                  <h3 className="font-semibold text-gray-900 mb-3">Recommendations</h3>
                  <ul className="space-y-2">
                    {result.recommendations.map((r, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                        <CheckCircle className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                        {typeof r === 'string' ? r : r.text || r.description}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="card flex flex-col items-center justify-center py-16">
              <FlaskConical className="w-12 h-12 text-gray-300 mb-3" />
              <p className="text-gray-500 text-center">Adjust the scenario parameters and click "Analyze Scenario" to see results</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
