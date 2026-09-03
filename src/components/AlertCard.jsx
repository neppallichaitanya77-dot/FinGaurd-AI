import { getSeverityClass, getSeverityIcon, formatDate } from '../utils/helpers';

export default function AlertCard({ alert, onRead, onDismiss }) {
  const severityClass = getSeverityClass(alert.severity);

  return (
    <div className={`border rounded-xl p-5 transition-all hover:shadow-md ${severityClass} ${alert.status === 'read' ? 'opacity-60' : ''}`}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">{getSeverityIcon(alert.severity)}</span>
            <h4 className="font-semibold text-sm">{alert.title}</h4>
            {alert.status !== 'read' && (
              <span className="w-2 h-2 bg-current rounded-full animate-pulse" />
            )}
          </div>
          <p className="text-sm opacity-80 mb-3">{alert.description}</p>
          {alert.recommended_action && (
            <div className="bg-white/50 rounded-lg px-3 py-2 mb-3">
              <p className="text-xs font-medium opacity-70">Recommended Action</p>
              <p className="text-sm">{alert.recommended_action}</p>
            </div>
          )}
          <p className="text-xs opacity-60">{formatDate(alert.created_at)}</p>
        </div>
      </div>
      <div className="flex gap-2 mt-4">
        {alert.status !== 'read' && onRead && (
          <button
            onClick={() => onRead(alert.id)}
            className="px-4 py-1.5 text-xs font-medium bg-white/60 rounded-lg hover:bg-white/80 transition-colors"
          >
            Mark as Read
          </button>
        )}
        {onDismiss && (
          <button
            onClick={() => onDismiss(alert.id)}
            className="px-4 py-1.5 text-xs font-medium bg-white/40 rounded-lg hover:bg-white/60 transition-colors"
          >
            Dismiss
          </button>
        )}
      </div>
    </div>
  );
}
