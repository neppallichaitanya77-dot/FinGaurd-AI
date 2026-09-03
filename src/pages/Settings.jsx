import { useState } from 'react';
import { Settings as SettingsIcon, Bell, Shield, Eye, Bot, AlertTriangle, Trash2 } from 'lucide-react';

function Toggle({ checked, onChange, label, description }) {
  return (
    <div className="flex items-center justify-between py-3">
      <div>
        <p className="text-sm font-medium text-gray-900">{label}</p>
        {description && <p className="text-xs text-gray-400 mt-0.5">{description}</p>}
      </div>
      <button
        onClick={() => onChange(!checked)}
        className={`relative w-11 h-6 rounded-full transition-colors ${checked ? 'bg-brand-600' : 'bg-gray-300'}`}
      >
        <span className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${checked ? 'translate-x-5' : ''}`} />
      </button>
    </div>
  );
}

function SettingsSection({ icon: Icon, title, children }) {
  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Icon className="w-5 h-5 text-brand-600" />
        <h3 className="font-semibold text-gray-900">{title}</h3>
      </div>
      <div className="divide-y divide-gray-50">{children}</div>
    </div>
  );
}

const defaultSettings = {
  emailAlerts: true, pushNotifications: true, smsAlerts: false, weeklyReport: true,
  emiReminders: true, balanceWarnings: true, spendingAlerts: true, riskLevelChanges: true,
  anonymousAnalytics: false, personalizedRecs: true,
  conversationHistory: true, suggestedQuestions: true,
  twoFactorAuth: false,
};

export default function Settings() {
  const [settings, setSettings] = useState(() => {
    try { return JSON.parse(localStorage.getItem('finguard_settings')) || defaultSettings; } catch { return defaultSettings; }
  });
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const update = (key, value) => {
    const next = { ...settings, [key]: value };
    setSettings(next);
    localStorage.setItem('finguard_settings', JSON.stringify(next));
  };

  return (
    <div className="flex-1 p-4 md:p-6 lg:p-8 max-w-3xl">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-1">
          <SettingsIcon className="w-6 h-6 text-brand-600" />
          <h1 className="page-title">Settings</h1>
        </div>
        <p className="page-subtitle">Manage your preferences and account settings</p>
      </div>

      <div className="space-y-6">
        <SettingsSection icon={Bell} title="Notification Preferences">
          <Toggle checked={settings.emailAlerts} onChange={(v) => update('emailAlerts', v)} label="Email Alerts" description="Receive alerts via email" />
          <Toggle checked={settings.pushNotifications} onChange={(v) => update('pushNotifications', v)} label="Push Notifications" description="Receive browser push notifications" />
          <Toggle checked={settings.smsAlerts} onChange={(v) => update('smsAlerts', v)} label="SMS Alerts" description="Receive important alerts via SMS" />
          <Toggle checked={settings.weeklyReport} onChange={(v) => update('weeklyReport', v)} label="Weekly Financial Report" description="Get a weekly summary of your financial health" />
        </SettingsSection>

        <SettingsSection icon={AlertTriangle} title="Alert Preferences">
          <Toggle checked={settings.emiReminders} onChange={(v) => update('emiReminders', v)} label="EMI Reminders" description="Get reminded before upcoming EMI payments" />
          <Toggle checked={settings.balanceWarnings} onChange={(v) => update('balanceWarnings', v)} label="Balance Warnings" description="Alert when balance drops below threshold" />
          <Toggle checked={settings.spendingAlerts} onChange={(v) => update('spendingAlerts', v)} label="Spending Alerts" description="Notifications for unusual spending patterns" />
          <Toggle checked={settings.riskLevelChanges} onChange={(v) => update('riskLevelChanges', v)} label="Risk Level Changes" description="Get notified when your risk level changes" />
        </SettingsSection>

        <SettingsSection icon={Eye} title="Data & Privacy">
          <Toggle checked={settings.anonymousAnalytics} onChange={(v) => update('anonymousAnalytics', v)} label="Anonymous Analytics" description="Help improve FinGuard AI with anonymous usage data" />
          <Toggle checked={settings.personalizedRecs} onChange={(v) => update('personalizedRecs', v)} label="Personalized Recommendations" description="Receive AI-powered personalized financial guidance" />
        </SettingsSection>

        <SettingsSection icon={Bot} title="AI Assistant">
          <Toggle checked={settings.conversationHistory} onChange={(v) => update('conversationHistory', v)} label="Conversation History" description="Save AI assistant conversations for context" />
          <Toggle checked={settings.suggestedQuestions} onChange={(v) => update('suggestedQuestions', v)} label="Suggested Questions" description="Show relevant question suggestions in the AI assistant" />
        </SettingsSection>

        <SettingsSection icon={Shield} title="Account Security">
          <div className="py-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">Change Password</p>
                <p className="text-xs text-gray-400 mt-0.5">Update your account password</p>
              </div>
              <button className="btn-secondary text-sm py-2">Change</button>
            </div>
          </div>
          <Toggle checked={settings.twoFactorAuth} onChange={(v) => update('twoFactorAuth', v)} label="Two-Factor Authentication" description="Add an extra layer of security to your account" />
        </SettingsSection>

        <SettingsSection icon={Trash2} title="Danger Zone">
          <div className="py-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-red-600">Delete Account</p>
                <p className="text-xs text-gray-400 mt-0.5">Permanently delete your account and all data</p>
              </div>
              {!showDeleteConfirm ? (
                <button onClick={() => setShowDeleteConfirm(true)} className="px-4 py-2 text-sm font-medium text-red-600 border border-red-200 rounded-xl hover:bg-red-50 transition-colors">
                  Delete
                </button>
              ) : (
                <div className="flex gap-2">
                  <button className="px-4 py-2 text-sm font-medium bg-red-600 text-white rounded-xl hover:bg-red-700">Confirm</button>
                  <button onClick={() => setShowDeleteConfirm(false)} className="px-4 py-2 text-sm font-medium text-gray-600 border border-gray-200 rounded-xl hover:bg-gray-50">Cancel</button>
                </div>
              )}
            </div>
          </div>
        </SettingsSection>
      </div>
    </div>
  );
}
