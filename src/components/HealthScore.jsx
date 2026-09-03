import { useEffect, useState } from 'react';

export default function HealthScore({ score = 0, status = '', loading = false }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    if (loading) return;
    let start = 0;
    const end = score;
    const duration = 1200;
    const increment = end / (duration / 16);
    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setAnimatedScore(end);
        clearInterval(timer);
      } else {
        setAnimatedScore(Math.floor(start));
      }
    }, 16);
    return () => clearInterval(timer);
  }, [score, loading]);

  const getColor = (s) => {
    if (s >= 80) return { stroke: '#059669', bg: '#ecfdf5', text: 'text-emerald-600' };
    if (s >= 60) return { stroke: '#d97706', bg: '#fffbeb', text: 'text-amber-600' };
    if (s >= 40) return { stroke: '#ea580c', bg: '#fff7ed', text: 'text-orange-600' };
    return { stroke: '#dc2626', bg: '#fef2f2', text: 'text-red-600' };
  };

  const colors = getColor(score);
  const circumference = 2 * Math.PI * 80;
  const offset = circumference - (animatedScore / 100) * circumference;

  const getMessage = (s) => {
    if (s >= 80) return 'Your financial position is strong. Keep up the good habits!';
    if (s >= 70) return 'Your financial position is currently stable, but some indicators require attention.';
    if (s >= 60) return 'Your finances are fair. Consider reviewing your spending patterns.';
    if (s >= 40) return 'Your financial health needs attention. Review the recommendations below.';
    return 'Your financial situation requires immediate attention. Please review your options.';
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-8">
        <div className="w-48 h-48 rounded-full border-4 border-gray-100 animate-pulse" />
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-48 h-48">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 180 180">
          <circle cx="90" cy="90" r="80" fill="none" stroke="#f1f5f9" strokeWidth="12" />
          <circle
            cx="90"
            cy="90"
            r="80"
            fill="none"
            stroke={colors.stroke}
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-300"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-bold text-gray-900">{animatedScore}</span>
          <span className="text-sm text-gray-400">/ 100</span>
        </div>
      </div>
      <div className="mt-4 text-center">
        <span className={`inline-block px-4 py-1.5 rounded-full text-sm font-semibold ${colors.text}`} style={{ background: colors.bg }}>
          {status || (score >= 80 ? 'Excellent' : score >= 70 ? 'Good' : score >= 60 ? 'Fair' : score >= 40 ? 'Needs Attention' : 'Concerning')}
        </span>
        <p className="mt-3 text-sm text-gray-500 max-w-xs">{getMessage(score)}</p>
      </div>
    </div>
  );
}
