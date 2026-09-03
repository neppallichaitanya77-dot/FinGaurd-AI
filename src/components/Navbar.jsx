import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Bell, LogOut, User, ChevronDown, Shield, Menu, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar({ notificationCount = 0 }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const userName = user?.name || user?.email || 'User';
  const userInitial = userName.charAt(0).toUpperCase();

  return (
    <nav className="bg-white border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <Link to="/dashboard" className="flex items-center gap-2">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-600 to-fintech-teal flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900 leading-tight">FinGuard AI</h1>
                <p className="text-[10px] text-gray-400 leading-tight hidden sm:block">Financial Wellness Dashboard</p>
              </div>
            </Link>
          </div>

          <div className="hidden md:flex items-center gap-4">
            <Link
              to="/alerts"
              className="relative p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-xl transition-colors"
            >
              <Bell className="w-5 h-5" />
              {notificationCount > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                  {notificationCount > 9 ? '9+' : notificationCount}
                </span>
              )}
            </Link>

            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-gray-50 transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center text-sm font-semibold">
                  {userInitial}
                </div>
                <span className="text-sm font-medium text-gray-700 hidden sm:block">{userName}</span>
                <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`} />
              </button>

              {dropdownOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-100 py-2 z-50">
                  <Link
                    to="/profile"
                    className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50"
                    onClick={() => setDropdownOpen(false)}
                  >
                    <User className="w-4 h-4" />
                    Profile
                  </Link>
                  <Link
                    to="/settings"
                    className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50"
                    onClick={() => setDropdownOpen(false)}
                  >
                    <ChevronDown className="w-4 h-4" />
                    Settings
                  </Link>
                  <hr className="my-2 border-gray-100" />
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 w-full"
                  >
                    <LogOut className="w-4 h-4" />
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>

          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 text-gray-500 hover:bg-gray-50 rounded-xl"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-100 bg-white px-4 py-3 space-y-2">
          <Link to="/dashboard" className="block px-4 py-2.5 rounded-xl text-sm text-gray-700 hover:bg-gray-50" onClick={() => setMobileMenuOpen(false)}>Dashboard</Link>
          <Link to="/financial-health" className="block px-4 py-2.5 rounded-xl text-sm text-gray-700 hover:bg-gray-50" onClick={() => setMobileMenuOpen(false)}>Financial Health</Link>
          <Link to="/alerts" className="block px-4 py-2.5 rounded-xl text-sm text-gray-700 hover:bg-gray-50" onClick={() => setMobileMenuOpen(false)}>Alerts</Link>
          <Link to="/ai-assistant" className="block px-4 py-2.5 rounded-xl text-sm text-gray-700 hover:bg-gray-50" onClick={() => setMobileMenuOpen(false)}>AI Assistant</Link>
          <Link to="/recommendations" className="block px-4 py-2.5 rounded-xl text-sm text-gray-700 hover:bg-gray-50" onClick={() => setMobileMenuOpen(false)}>Recommendations</Link>
          <Link to="/transactions" className="block px-4 py-2.5 rounded-xl text-sm text-gray-700 hover:bg-gray-50" onClick={() => setMobileMenuOpen(false)}>Transactions</Link>
          <Link to="/loans" className="block px-4 py-2.5 rounded-xl text-sm text-gray-700 hover:bg-gray-50" onClick={() => setMobileMenuOpen(false)}>Loans</Link>
          <Link to="/scenarios" className="block px-4 py-2.5 rounded-xl text-sm text-gray-700 hover:bg-gray-50" onClick={() => setMobileMenuOpen(false)}>Scenarios</Link>
          <hr className="border-gray-100" />
          <button onClick={handleLogout} className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm text-red-600 hover:bg-red-50 w-full">
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </div>
      )}
    </nav>
  );
}
