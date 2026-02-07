import React, { useState, useEffect } from 'react';
import { Zap, LayoutDashboard, MessageSquare, BarChart3, Code2, LogIn, LogOut, User, X } from 'lucide-react';
import { supabase } from '../supabaseClient';
import Login from '../modules/Login';

export default function Sidebar({ activeModule, switchModule, role, isOpen, onClose }) {
  const [session, setSession] = useState(null);
  const [showLogin, setShowLogin] = useState(false);

  useEffect(() => {
    if (!supabase) return;
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setShowLogin(false); // Close login modal on success
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleLogout = async () => {
      if (!supabase) return;
      await supabase.auth.signOut();
  };

  if (showLogin && !session) {
      return (
          <div className="fixed inset-0 z-100 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center">
              <div className="relative">
                  <button 
                    onClick={() => setShowLogin(false)}
                    className="absolute -top-10 right-0 text-white hover:text-brand-400"
                  >
                      Cancel
                  </button>
                  <Login />
              </div>
          </div>
      );
  }

  return (
    <aside className={`
      fixed inset-y-0 left-0 z-50 w-72 bg-sidebar text-slate-300 flex flex-col h-screen transition-transform duration-300 transform 
      ${isOpen ? 'translate-x-0' : '-translate-x-full'} 
      md:translate-x-0 md:relative shrink-0
    `}>
      <div className="p-8 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-brand-500 rounded-xl flex items-center justify-center shadow-lg shadow-brand-500/20">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-display font-bold text-white tracking-tight">AI Hub</h1>
        </div>
        
        {/* Mobile Close Button */}
        <button onClick={onClose} className="md:hidden text-slate-400 hover:text-white p-1">
          <X className="w-6 h-6" />
        </button>
      </div>

      <nav className="flex-1 px-4 space-y-2 mt-4">
        <button
          onClick={() => switchModule('home')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
            activeModule === 'home'
              ? 'sidebar-active text-brand-500'
              : 'hover:bg-slate-800 hover:text-white'
          }`}
        >
          <LayoutDashboard className="w-5 h-5" />
          Dashboard
        </button>
        <button
          onClick={() => switchModule('chat')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
            activeModule === 'chat'
              ? 'sidebar-active text-brand-500'
              : 'hover:bg-slate-800 hover:text-white'
          }`}
        >
          <MessageSquare className="w-5 h-5" />
          Chat with Data
        </button>
        <button
          onClick={() => switchModule('reports')}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
            activeModule === 'reports'
              ? 'sidebar-active text-brand-500'
              : 'hover:bg-slate-800 hover:text-white'
          }`}
        >
          <BarChart3 className="w-5 h-5" />
          Analytics
        </button>
        
        {role === 'developer' && (
          <div className="animate-fade-in pt-4 border-t border-slate-800">
            <span className="px-4 text-[10px] uppercase tracking-widest text-slate-500 font-bold">Administration</span>
            <button
              onClick={() => switchModule('dev')}
              className={`w-full mt-2 flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                activeModule === 'dev'
                  ? 'sidebar-active text-brand-500'
                  : 'hover:bg-slate-800 hover:text-white'
              }`}
            >
              <Code2 className="w-5 h-5 text-amber-500" />
              Dev Center
            </button>
          </div>
        )}
      </nav>

      <div className="p-6 border-t border-slate-800 bg-slate-950/50">
        <div className="flex items-center justify-between mb-3">
            <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Account</label>
            {session && (
                 <span className="text-[10px] bg-brand-900 text-brand-300 px-2 py-0.5 rounded-full capitalize">
                     {role}
                 </span>
            )}
        </div>
        
        {session ? (
            <div className="bg-slate-900 rounded-lg p-3">
                <div className="flex items-center gap-3 mb-3">
                    <div className="w-8 h-8 rounded-full bg-brand-700 flex items-center justify-center text-white text-xs font-bold">
                        {session.user.email?.charAt(0).toUpperCase()}
                    </div>
                    <div className="overflow-hidden">
                        <div className="text-sm font-medium text-white truncate w-32">{session.user.email}</div>
                        <div className="text-xs text-slate-500 truncate">Online</div>
                    </div>
                </div>
                <button 
                    onClick={handleLogout}
                    className="w-full flex items-center justify-center gap-2 py-2 text-xs font-medium text-red-400 bg-red-950/20 hover:bg-red-950/40 rounded-md transition-colors border border-red-900/30"
                >
                    <LogOut className="w-3 h-3" />
                    Sign Out
                </button>
            </div>
        ) : (
            <button 
                onClick={() => setShowLogin(true)}
                className="w-full flex items-center justify-center gap-2 py-3 bg-brand-600 hover:bg-brand-700 text-white rounded-lg font-medium transition-colors shadow-lg shadow-brand-900/20"
            >
                <LogIn className="w-4 h-4" />
                Sign In
            </button>
        )}
      </div>
    </aside>
  );
}
