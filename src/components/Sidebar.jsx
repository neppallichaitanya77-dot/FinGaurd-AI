import { NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, HeartPulse, AlertTriangle, Bot, Lightbulb, ArrowLeftRight, Landmark, FlaskConical, User, Settings } from 'lucide-react';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/financial-health', label: 'Financial Health', icon: HeartPulse },
  { to: '/alerts', label: 'Alerts', icon: AlertTriangle },
  { to: '/ai-assistant', label: 'AI Assistant', icon: Bot },
  { to: '/recommendations', label: 'Recommendations', icon: Lightbulb },
  { to: '/transactions', label: 'Transactions', icon: ArrowLeftRight },
  { to: '/loans', label: 'Loans', icon: Landmark },
  { to: '/scenarios', label: 'Scenarios', icon: FlaskConical },
];

const bottomItems = [
  { to: '/profile', label: 'Profile', icon: User },
  { to: '/settings', label: 'Settings', icon: Settings },
];

function SidebarLink({ to, icon: Icon, label }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-colors ${
          isActive
            ? 'bg-brand-50 text-brand-700 border border-brand-100'
            : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
        }`
      }
    >
      <Icon className="w-5 h-5 flex-shrink-0" />
      <span>{label}</span>
    </NavLink>
  );
}

export default function Sidebar() {
  return (
    <aside className="hidden lg:flex flex-col w-64 bg-white border-r border-gray-100 h-[calc(100vh-4rem)] sticky top-16 p-4 overflow-y-auto">
      <div className="flex flex-col gap-1 flex-1">
        {navItems.map((item) => (
          <SidebarLink key={item.to} {...item} />
        ))}
      </div>

      <div className="mt-auto pt-4 border-t border-gray-100">
        <div className="px-4 py-3 bg-gradient-to-r from-brand-50 to-emerald-50 rounded-xl mb-3">
          <p className="text-[11px] text-gray-500 italic text-center">
            "Prevention, not punishment."
          </p>
        </div>
        {bottomItems.map((item) => (
          <SidebarLink key={item.to} {...item} />
        ))}
      </div>
    </aside>
  );
}
