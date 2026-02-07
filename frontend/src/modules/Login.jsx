import React, { useState } from 'react';
import { supabase } from '../supabaseClient';
import { Bot, Lock, Mail } from 'lucide-react';

export default function Login() {
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
        if (!supabase) throw new Error('Missing Supabase configuration');
        const { error } = await supabase.auth.signInWithPassword({
            email,
            password,
        });
        if (error) throw error;
    } catch (error) {
        setError(error.message);
    } finally {
        setLoading(false);
    }
  };

  const handleSignUp = async (e) => {
      e.preventDefault();
      setLoading(true);
      setError(null);
      
      try {
          if (!supabase) throw new Error('Missing Supabase configuration');
          const { error } = await supabase.auth.signUp({
              email,
              password,
          });
          if (error) throw error;
          setMessage("Check your email for the confirmation link!");
      } catch (error) {
          setError(error.message);
      } finally {
          setLoading(false);
      }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 font-sans">
      <div className="bg-white p-8 rounded-2xl shadow-xl border border-slate-100 max-w-md w-full">
        <div className="text-center mb-8">
            <div className="w-16 h-16 bg-brand-50 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-brand-100">
                <Bot className="w-8 h-8 text-brand-600" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900 font-display">Welcome to KR HUB</h1>
            <p className="text-slate-500 mt-2">Sign in to access your AI Workspace</p>
        </div>

        {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-4 border border-red-100">
                {error}
            </div>
        )}
        
        {message && (
            <div className="bg-green-50 text-green-600 p-3 rounded-lg text-sm mb-4 border border-green-100">
                {message}
            </div>
        )}

        <form className="space-y-4">
            <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
                <div className="relative">
                    <Mail className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                    <input 
                        type="email" 
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500 outline-none transition-all"
                        placeholder="you@example.com"
                        required
                    />
                </div>
            </div>
            
            <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
                <div className="relative">
                    <Lock className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                    <input 
                        type="password" 
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500 outline-none transition-all"
                        placeholder="••••••••"
                        required
                    />
                </div>
            </div>

            <button 
                onClick={handleLogin}
                disabled={loading}
                className="w-full py-3 bg-brand-600 hover:bg-brand-700 text-white font-bold rounded-xl transition-colors shadow-lg shadow-brand-500/30 disabled:opacity-50"
            >
                {loading ? 'Processing...' : 'Sign In'}
            </button>
            
            <div className="text-center mt-4">
                <span className="text-slate-500 text-sm">Don't have an account? </span>
                <button onClick={handleSignUp} className="text-brand-600 font-semibold text-sm hover:underline">
                    Sign Up
                </button>
            </div>
        </form>
      </div>
    </div>
  );
}
