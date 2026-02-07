import React from 'react';
import { Key } from 'lucide-react';

export default function DevCenter() {
  const models = []; // Mocks removed
  
  return (
    <div className="animate-fade-in max-w-6xl mx-auto pb-20">
      <div className="mb-10">
        <h2 className="text-3xl font-display font-bold text-slate-900 mb-2">Developer Center</h2>
        <p className="text-slate-500">Manage global AI infrastructure, models, and security keys.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          {/* Model Management */}
          <section className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
            <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
              <h3 className="font-bold text-slate-800">Global AI Models</h3>
              <button className="text-brand-600 text-xs font-bold hover:underline">+ Add Model</button>
            </div>
            <div className="p-6 text-center text-slate-500 text-sm">
              No models configured.
            </div>
          </section>

          {/* Usage Logs */}
          <section className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
            <div className="p-6 border-b border-slate-100 bg-slate-50/50">
              <h3 className="font-bold text-slate-800">Live API Traffic</h3>
            </div>
            <div className="p-6 text-center text-slate-500 text-sm">
               No recent traffic.
            </div>
          </section>
        </div>

        <div className="space-y-6">
          {/* Security / BYOK */}
          <section className="bg-slate-900 rounded-2xl p-6 text-white shadow-xl shadow-slate-900/20">
            <h3 className="font-bold mb-4 flex items-center gap-2">
              <Key className="w-5 h-5 text-amber-500" />
              BYOK Settings
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-[10px] uppercase font-bold text-slate-500 mb-1.5">OpenAI API Key</label>
                <input type="password" value="sk-••••••••••••••••" readOnly className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-brand-500" />
              </div>
              <div>
                <label className="block text-[10px] uppercase font-bold text-slate-500 mb-1.5">Anthropic Key</label>
                <input type="password" value="sk-ant-••••••••••••" readOnly className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-brand-500" />
              </div>
              <button className="w-full bg-brand-600 py-2.5 rounded-lg text-sm font-bold hover:bg-brand-500 transition-colors">Update Vault</button>
            </div>
          </section>

          <section className="bg-white rounded-2xl p-6 border border-slate-200">
            <h3 className="font-bold text-slate-800 mb-4">Environment Status</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-500">Production API</span>
                <span className="text-xs font-bold text-green-500">Stable</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-500">Edge Runtime</span>
                <span className="text-xs font-bold text-green-500">Connected</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-500">Database Proxy</span>
                <span className="text-xs font-bold text-amber-500">Slow (2s)</span>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
