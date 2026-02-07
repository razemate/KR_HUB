import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Home from './modules/Home';
import Chat from './modules/Chat';
import Reports from './modules/Reports';
import DevCenter from './modules/DevCenter';
import Login from './modules/Login';
import { supabase } from './supabaseClient';

function App() {
  const [session, setSession] = useState(null);
  const [role, setRole] = useState('user');
  const [activeModule, setActiveModule] = useState('home');

  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const fetchUserRole = async (userId) => {
      if (!supabase) return;
      try {
          const { data, error } = await supabase
              .from('profiles')
              .select('role')
              .eq('id', userId)
              .single();
          
          if (data && data.role) {
              setRole(data.role);
          } else if (error && error.code === 'PGRST116') {
              // Profile doesn't exist? Create one default to 'user'
               // Or just keep default 'user'
          }
      } catch (e) {
          console.error("Error fetching role:", e);
      }
  };

  useEffect(() => {
    if (!supabase) return;
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session) fetchUserRole(session.user.id);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      if (session) {
          fetchUserRole(session.user.id);
      } else {
          setRole('user'); // Reset role on logout
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const switchModule = (moduleId) => {
    setActiveModule(moduleId);
    setIsSidebarOpen(false); // Close sidebar on mobile when switching
  };

  const getModuleTitle = (id) => {
    const titles = {
      home: 'Smart Workspace',
      chat: 'Chat with Data',
      reports: 'Analytics & Reports',
      dev: 'Developer Control Center'
    };
    return titles[id] || 'Workspace';
  };

  const renderModule = () => {
    switch (activeModule) {
      case 'home':
        return <Home switchModule={switchModule} />;
      case 'chat':
        return <Chat session={session} />; // Pass session to Chat
      case 'reports':
        return <Reports />;
      case 'dev':
        // Double check role here to prevent access
        return role === 'developer' ? <DevCenter /> : <Home switchModule={switchModule} />;
      default:
        return <Home switchModule={switchModule} />;
    }
  };

  return (
    <div className="h-screen flex overflow-hidden bg-surface font-sans text-slate-600">
      {/* Mobile Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      <Sidebar 
        activeModule={activeModule} 
        switchModule={switchModule} 
        role={role} 
        setRole={setRole} 
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />
      
      <main className="flex-1 flex flex-col min-w-0 bg-surface relative">
        <Header 
          title={getModuleTitle(activeModule)} 
          role={role} 
          toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        />
        
        <div id="module-content" className="flex-1 overflow-y-auto custom-scrollbar p-4 md:p-8">
          {renderModule()}
        </div>
      </main>
    </div>
  );
}

export default App;
