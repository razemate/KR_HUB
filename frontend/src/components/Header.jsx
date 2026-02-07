import React from 'react';
import { Bell, Menu } from 'lucide-react';

export default function Header({ title, role, toggleSidebar }) {
  return (
    <header className="h-16 border-b border-slate-200 flex items-center justify-between px-4 md:px-8 bg-white/80 backdrop-blur-md sticky top-0 z-40">
      <div className="flex items-center gap-4">
        <button onClick={() => (typeof toggleSidebar === 'function' ? toggleSidebar() : (typeof window !== 'undefined' && window.dispatchEvent(new CustomEvent('toggleSidebar'))))} className="md:hidden p-2 mr-2 text-slate-600 hover:text-slate-800">
          <Menu className="w-6 h-6" />
        </button>
        <h2 className="text-lg font-semibold text-slate-800">{title}</h2>
        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${
            role === 'developer' 
            ? 'bg-amber-50 text-amber-600 border-amber-200' 
            : 'bg-slate-100 text-slate-500 border-slate-200'
        }`}>
          {role === 'developer' ? 'Developer Mode' : 'User Mode'}
        </span>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 border border-slate-200">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
          <span className="text-xs font-medium text-slate-600">All Systems Operational</span>
        </div>
        <button className="p-2 text-slate-400 hover:text-slate-600 transition-colors">
          <Bell className="w-6 h-6" />
        </button>
        <div className="w-8 h-8 rounded-full bg-brand-600 text-white flex items-center justify-center font-bold text-xs ring-2 ring-brand-50 shadow-sm">
          JD
        </div>
      </div>
    </header>
  );
}
