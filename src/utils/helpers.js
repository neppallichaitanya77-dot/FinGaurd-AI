export const formatCurrency = (amount, currency = 'INR') => {
  if (amount === null || amount === undefined) return '₹0';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

export const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const formatDateTime = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const getRiskColor = (level) => {
  switch (level?.toLowerCase()) {
    case 'low':
      return 'text-emerald-600 bg-emerald-50 border-emerald-200';
    case 'medium':
      return 'text-amber-600 bg-amber-50 border-amber-200';
    case 'high':
      return 'text-red-600 bg-red-50 border-red-200';
    case 'critical':
      return 'text-red-700 bg-red-100 border-red-300';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
};

export const getRiskBadgeClass = (level) => {
  switch (level?.toLowerCase()) {
    case 'low':
      return 'bg-emerald-100 text-emerald-700';
    case 'medium':
      return 'bg-amber-100 text-amber-700';
    case 'high':
      return 'bg-red-100 text-red-700';
    case 'critical':
      return 'bg-red-200 text-red-800';
    default:
      return 'bg-gray-100 text-gray-700';
  }
};

export const getScoreColor = (score) => {
  if (score >= 80) return '#059669';
  if (score >= 60) return '#d97706';
  if (score >= 40) return '#ea580c';
  return '#dc2626';
};

export const getScoreLabel = (score) => {
  if (score >= 80) return 'Excellent';
  if (score >= 70) return 'Good';
  if (score >= 60) return 'Fair';
  if (score >= 40) return 'Needs Attention';
  return 'Concerning';
};

export const getSeverityIcon = (severity) => {
  switch (severity?.toLowerCase()) {
    case 'high':
    case 'critical':
      return '⚠️';
    case 'medium':
      return '⚡';
    case 'low':
      return 'ℹ️';
    default:
      return '📌';
  }
};

export const getSeverityClass = (severity) => {
  switch (severity?.toLowerCase()) {
    case 'high':
    case 'critical':
      return 'bg-red-50 border-red-200 text-red-800';
    case 'medium':
      return 'bg-amber-50 border-amber-200 text-amber-800';
    case 'low':
      return 'bg-blue-50 border-blue-200 text-blue-800';
    default:
      return 'bg-gray-50 border-gray-200 text-gray-800';
  }
};
