import { Lightbulb, Check, X, ChevronRight } from 'lucide-react';

export default function RecommendationCard({ recommendation, onAccept, onDismiss }) {
  const getPriorityBadge = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-700';
      case 'medium': return 'bg-amber-100 text-amber-700';
      case 'low': return 'bg-emerald-100 text-emerald-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="card group">
      <div className="flex items-start gap-4">
        <div className="w-10 h-10 rounded-xl bg-brand-50 flex items-center justify-center flex-shrink-0">
          <Lightbulb className="w-5 h-5 text-brand-600" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-semibold text-gray-900 text-sm">{recommendation.title}</h4>
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${getPriorityBadge(recommendation.priority)}`}>
              {recommendation.priority?.toUpperCase()}
            </span>
          </div>
          <p className="text-sm text-gray-500 mb-3">{recommendation.description}</p>
          {recommendation.category && (
            <span className="text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded-md">
              {recommendation.category}
            </span>
          )}
        </div>
      </div>
      {recommendation.status === 'pending' && (
        <div className="flex gap-2 mt-4 pt-4 border-t border-gray-50">
          {onAccept && (
            <button
              onClick={() => onAccept(recommendation.id)}
              className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium bg-brand-50 text-brand-700 rounded-xl hover:bg-brand-100 transition-colors"
            >
              <Check className="w-4 h-4" /> Review Options
            </button>
          )}
          {onDismiss && (
            <button
              onClick={() => onDismiss(recommendation.id)}
              className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 rounded-xl transition-colors"
            >
              <X className="w-4 h-4" /> Not Now
            </button>
          )}
        </div>
      )}
      {recommendation.status === 'accepted' && (
        <div className="mt-4 pt-4 border-t border-gray-50">
          <span className="text-xs text-emerald-600 font-medium flex items-center gap-1">
            <Check className="w-3 h-3" /> Reviewed
          </span>
        </div>
      )}
    </div>
  );
}
