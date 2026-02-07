import React from 'react';
import { MessageSquare, BarChart3, Plus } from 'lucide-react';

export default function Home({ switchModule }) {
  const reports = [
    { id: 1, title: 'Q3 Market Sentiment', date: 'Oct 12, 2023', status: 'Complete', score: 94 },
    { id: 2, title: 'Competitor Feature Matrix', date: 'Oct 14, 2023', status: 'Processing', score: 0 },
    { id: 3, title: 'User Retention Analysis', date: 'Oct 15, 2023', status: 'Complete', score: 88 }
  ];

  return (
    <div className="max-w-6xl mx-auto animate-fade-in">
      <div className="mb-10">
        <h1 className="text-4xl font-display font-bold text-slate-900 mb-2">Welcome back, John</h1>
        <p className="text-slate-500">Here's what's happening across your AI workspace today.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <button onClick={() => switchModule('chat')} className="group p-6 glass-card rounded-2xl text-left transition-all hover:shadow-xl hover:-translate-y-1">
          <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center mb-4 group-hover:bg-blue-600 group-hover:text-white transition-colors">
            <MessageSquare className="w-6 h-6" />
          </div>
          <h3 className="font-semibold text-slate-900 mb-1">Start New Chat</h3>
          <p className="text-xs text-slate-500">Query your datasets using natural language models.</p>
        </button>
        <button onClick={() => switchModule('reports')} className="group p-6 glass-card rounded-2xl text-left transition-all hover:shadow-xl hover:-translate-y-1">
          <div className="w-12 h-12 bg-purple-50 text-purple-600 rounded-xl flex items-center justify-center mb-4 group-hover:bg-purple-600 group-hover:text-white transition-colors">
            <BarChart3 className="w-6 h-6" />
          </div>
          <h3 className="font-semibold text-slate-900 mb-1">Generate Report</h3>
          <p className="text-xs text-slate-500">Create beautiful visual analytics from raw data.</p>
        </button>
        <div className="p-6 glass-card rounded-2xl border-dashed border-2 border-slate-200 flex flex-col items-center justify-center text-center">
          <div className="w-10 h-10 bg-slate-100 text-slate-400 rounded-full flex items-center justify-center mb-2">
            <Plus className="w-5 h-5" />
          </div>
          <span className="text-xs font-medium text-slate-400">Add custom module</span>
        </div>
      </div>

      <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center gap-2">
        <span className="text-brand-500">⚡</span>
        Recent Activity
      </h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {reports.map(r => (
          <div key={r.id} className="flex items-center justify-between p-4 bg-white rounded-xl border border-slate-100 hover:border-brand-200 hover:shadow-sm transition-all group cursor-pointer">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg bg-slate-50 flex items-center justify-center text-slate-400">
                <BarChart3 className="w-5 h-5" />
              </div>
              <div>
                <h4 className="font-medium text-slate-800">{r.title}</h4>
                <p className="text-[11px] text-slate-400 font-medium uppercase tracking-tighter">{r.date}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className={`text-xs font-bold ${r.status === 'Complete' ? 'text-green-500' : 'text-amber-500'} bg-opacity-10 px-2 py-1 rounded`}>{r.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
