import React from 'react';
import { Plus, BarChart2 } from 'lucide-react';

export default function Reports() {
  const reports = [
    { id: 1, title: 'Q3 Market Sentiment', date: 'Oct 12, 2023', status: 'Complete', score: 94 },
    { id: 2, title: 'Competitor Feature Matrix', date: 'Oct 14, 2023', status: 'Processing', score: 0 },
    { id: 3, title: 'User Retention Analysis', date: 'Oct 15, 2023', status: 'Complete', score: 88 }
  ];

  return (
    <div className="animate-fade-in max-w-6xl mx-auto">
      <div className="flex items-end justify-between mb-10">
        <div>
          <h2 className="text-3xl font-display font-bold text-slate-900 mb-2">Reports & Analytics</h2>
          <p className="text-slate-500">Automated insight generation from connected sources.</p>
        </div>
        <button className="bg-brand-600 text-white px-6 py-2.5 rounded-xl font-bold hover:shadow-lg hover:shadow-brand-500/20 transition-all flex items-center gap-2">
          <Plus className="w-5 h-5" />
          New Report
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {reports.map(r => (
          <div key={r.id} className="bg-white rounded-2xl border border-slate-200 p-6 hover:shadow-xl transition-all group">
            <div className="flex justify-between items-start mb-6">
              <div className="w-12 h-12 rounded-xl bg-brand-50 flex items-center justify-center text-brand-600">
                <BarChart2 className="w-6 h-6" />
              </div>
              <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider ${r.status === 'Complete' ? 'bg-green-50 text-green-600' : 'bg-amber-50 text-amber-600'}`}>{r.status}</span>
            </div>
            <h3 className="text-lg font-bold text-slate-800 mb-1">{r.title}</h3>
            <p className="text-xs text-slate-400 mb-6">Generated on {r.date}</p>
            
            <div className="space-y-3">
              <div className="flex justify-between text-xs font-medium">
                <span className="text-slate-500">Confidence Score</span>
                <span className="text-slate-900">{r.score}%</span>
              </div>
              <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                <div className="h-full bg-brand-500 rounded-full" style={{ width: `${r.score}%` }}></div>
              </div>
            </div>

            <div className="mt-8 pt-6 border-t border-slate-100 flex gap-2">
              <button className="flex-1 py-2 text-xs font-bold text-slate-600 bg-slate-50 hover:bg-slate-100 rounded-lg transition-colors">Download</button>
              <button className="flex-1 py-2 text-xs font-bold text-brand-600 bg-brand-50 hover:bg-brand-100 rounded-lg transition-colors">View Detail</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
