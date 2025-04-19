import { useState, useEffect, useRef, useCallback } from 'react';
import { Clock, Database, Instagram, Terminal, AlertTriangle, CheckCircle, AlertCircle, XCircle } from 'lucide-react';
import Navbar from '../components/Navbar';
import { toast } from 'sonner';

// TypeScript interfaces
interface InstagramAccount {
  id?: number;
  username: string;
  status: 'active' | 'idle' | 'restricted' | 'banned';
  banstatus?: string;
  scraper: string | null;
  pendingSave?: boolean;
  pendingDelete?: boolean;
  password?: string;
  isNew?: boolean; // New flag to identify freshly added accounts
}

interface WebSocketMessage {
  query: string;
  data?: Record<string, unknown>; // Instead of any
  response?: Record<string, unknown>; // Instead of any
  status?: string;
  msg?: string,
}

// Constants
const WS_URL = 'ws://localhost:8080/api/ws';
const RECONNECT_INTERVAL = 3000; // 3 seconds

export default function SettingsPage() {
  // State for MongoDB toggle
  const [enableMongoDB, setEnableMongoDB] = useState<boolean>(false);
  
  // State for account rotation toggle
  const [enableRotation, setEnableRotation] = useState<boolean>(false);
  
  // State for WebSocket connection
  const [wsConnected, setWsConnected] = useState<boolean>(false);
  const [wsStatus, setWsStatus] = useState<string>('Connecting...');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef =  useRef<number | null>(null);
  if (reconnectTimeoutRef.current) {
    window.clearTimeout(reconnectTimeoutRef.current);
  }
  
  
  // Instagram accounts state
  const [instagramAccounts, setInstagramAccounts] = useState<InstagramAccount[]>([]);
  const [pendingChanges, setPendingChanges] = useState<{[key: number]: boolean}>({});
  
  // State for new account form
  const [newAccount, setNewAccount] = useState<{username: string, password: string, scraper: string | null}>({ 
    username: '', 
    password: '', 
    scraper: null 
  });
  
  // Terminal logs
  const [terminalLogs, setTerminalLogs] = useState<string[]>([
    '[INFO] Scraper initialized.',
    '[INFO] Connecting to WebSocket...'
  ]);
  
  // Add log to terminal
  const addLog = useCallback((log: string) => {
    setTerminalLogs(prev => [...prev, log]);
  }, []);

  // Load accounts via WebSocket
  const loadAccounts = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage = {
        query: 'load'
      };
      wsRef.current.send(JSON.stringify(message));
      addLog('[INFO] Requesting accounts from server...');
    } else {
      addLog('[ERROR] WebSocket not connected, cannot load accounts');
    }
  }, [addLog]);

  // Connect WebSocket function
  const connectWebSocket = useCallback(() => {
    // Clear any existing reconnect timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    setWsStatus('Connecting...');
    addLog('[INFO] Attempting to connect to WebSocket...');
    
    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;
      
      ws.onopen = () => {
        setWsConnected(true);
        setWsStatus('Connected');
        addLog('[INFO] WebSocket connected');
        
        // Load accounts on connection
        loadAccounts();
      };
      
      ws.onclose = (event) => {
        setWsConnected(false);
        setWsStatus(`Disconnected (Code: ${event.code})`);
        addLog(`[ERROR] WebSocket disconnected with code ${event.code}`);
        
        // Setup reconnection
        reconnectTimeoutRef.current = setTimeout(() => {
          addLog('[INFO] Attempting to reconnect...');
          connectWebSocket();
        }, RECONNECT_INTERVAL);
      };
      
      ws.onerror = (error) => {
        setWsConnected(false);
        setWsStatus('Connection Error');
        addLog('[ERROR] WebSocket connection error');
        console.error('WebSocket error:', error);
      };
      
      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          handleWebSocketMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
          addLog('[ERROR] Failed to parse WebSocket message');
        }
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      addLog('[ERROR] Failed to create WebSocket connection');
      
      // Setup reconnection
      reconnectTimeoutRef.current = setTimeout(() => {
        connectWebSocket();
      }, RECONNECT_INTERVAL);
    }
  }, [addLog, loadAccounts]);

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
    // Handle different message types
    switch (message.query) {
      case 'load':
        if (message.status === 'success' && message.response?.accounts) {
          // Process accounts and assign IDs if they don't have them
          
          const processedAccounts = message.response.accounts.map((account: InstagramAccount, index: number) => ({
            ...account,
            id: account.id || Date.now() + index,
            scraper: account.scraper || null
          }));
          console.log(processedAccounts)
          setInstagramAccounts(processedAccounts);
          addLog(`[INFO] Successfully loaded ${processedAccounts.length} accounts`);
        } 
        else if (message.status === 'error'){
          addLog(`[WARN] ${message.msg} `);
        }
        else {
          addLog('[ERROR] Failed to load accounts or no accounts received');
        }
        
        break;

        
        case 'save':
          if (message.status === 'success') {
            // Update the account to remove pending status and isNew flag
            setInstagramAccounts(accounts => 
              accounts.map(account => 
                account.id === message.data?.id 
                  ? { ...account, pendingSave: false, isNew: false } 
                  : account
              )
            );
            addLog(`[INFO] Account ${message.data?.username} saved successfully`);
          } 
          else if(message.status === 'process'){
            addLog(`[PROCESS] ${message.msg}`)
          }
          else if(message.status === 'error'){
            setInstagramAccounts(accounts => 
              accounts.map(account => 
                account.id === message.data?.id 
                  ? { ...account, pendingSave: false } 
                  : account
              )
            );
            addLog(`[ERROR] Failed to save account: ${message.msg}`);
          }
          else {
            // Mark the account as not pending
            setInstagramAccounts(accounts => 
              accounts.map(account => 
                account.id === message.data?.id 
                  ? { ...account, pendingSave: false } 
                  : account
              )
            );
            addLog(`[ERROR] Failed to save account: ${message.data?.username}`);
          }
          break;
        
      case 'delete':
        if (message.status === 'success') {
          // Remove the account from state
          setInstagramAccounts(accounts => 
            accounts.filter(account => account.id !== message.data?.id)
          );
          addLog(`[INFO] Account ${message.data?.username} deleted successfully`);
        } else {
          // Update the account to remove pending status
          setInstagramAccounts(accounts => 
            accounts.map(account => 
              account.id === message.data?.id 
                ? { ...account, pendingDelete: false } 
                : account
            )
          );
          addLog(`[ERROR] Failed to delete account: ${message.data?.username}`);
        }
        break;
        
      default:
        addLog(`[INFO] Received message: ${message.query}`);
    }
  }, [addLog]);

  // Initialize WebSocket connection
  useEffect(() => {
    connectWebSocket();
    
    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connectWebSocket]);
  
  // Add new Instagram account
  const addInstagramAccount = (e: React.FormEvent) => {
    e.preventDefault();
    if (newAccount.username && newAccount.password) {
      const newAccountObj: InstagramAccount = { 
        id: Date.now(), // Temporary ID
        username: newAccount.username,
        password: newAccount.password,
        status: 'idle', 
        scraper: null, // Start with no scraper selected
        isNew: true // Flag to identify newly added accounts
      };
      
      setInstagramAccounts(prev => [...prev, newAccountObj]);
      setNewAccount({ username: '', password: '' }); // Reset form
      addLog(`[INFO] New account ${newAccount.username} added (select scraper and save)`);
    }
  };
  
  // Save Instagram account to server
  const saveAccount = (account: InstagramAccount) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      // Mark account as pending save
      setInstagramAccounts(accounts => 
        accounts.map(acc => 
          acc.id === account.id 
            ? { ...acc, pendingSave: true } 
            : acc
        )
      );
      
      // Send save request, but strip out the isNew flag
      const { isNew, ...accountData } = account;
      const message: WebSocketMessage = {
        query: 'save',
        data: accountData
      };
      wsRef.current.send(JSON.stringify(message));
      addLog(`[INFO] Saving account ${account.username}...`);
    } else {
      addLog('[ERROR] WebSocket not connected, cannot save account');
    }
  };
  
  // Remove Instagram account
  const removeAccount = (account: InstagramAccount) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      // Mark account as pending delete
      setInstagramAccounts(accounts => 
        accounts.map(acc => 
          acc.id === account.id 
            ? { ...acc, pendingDelete: true } 
            : acc
        )
      );
      
      // Send delete request
      const message: WebSocketMessage = {
        query: 'delete',
        data: {
          id: account.id,
          username: account.username
        }
      };
      wsRef.current.send(JSON.stringify(message));
      addLog(`[INFO] Deleting account ${account.username}...`);
    } else {
      addLog('[ERROR] WebSocket not connected, cannot delete account');
    }
  };
  
  // Update scraper assignment
  const updateScraperAssignment = (id: number, scraper: string | null) => {
    setInstagramAccounts(accounts => 
      accounts.map(account => 
        account.id === id 
          ? { ...account, scraper } 
          : account
      )
    );
    
    // Mark as having pending changes
    setPendingChanges(prev => ({
      ...prev,
      [id]: true
    }));
  };
  
  // Save configurations
  const saveConfigurations = () => {
    addLog('[INFO] Saving global configurations...');
    // Implement actual save functionality
    // For now just simulate a success
    setTimeout(() => {
      addLog('[INFO] Global configurations saved successfully');
    }, 500);
  };

  // Save rotation settings
  const saveRotationSettings = () => {
    addLog('[INFO] Saving rotation settings...');
    // Implement actual save functionality
    // For now just simulate a success
    setTimeout(() => {
      addLog('[INFO] Rotation settings saved successfully');
    }, 500);
  };
  
  // Manual reconnect
  const handleManualReconnect = () => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    connectWebSocket();
  };

  // Get status badge component based on status
  const getStatusBadge = (status: string) => {
    const baseClasses = "px-2 py-1 rounded-full text-xs font-medium flex items-center";
    
    switch(status) {
      case 'active':
        return (
          <span className={`${baseClasses} bg-green-100 text-green-800`}>
            <CheckCircle className="w-3 h-3 mr-1" />
            In Use
          </span>
        );
      case 'idle':
        return (
          <span className={`${baseClasses} bg-blue-100 text-sky-800`}>
            <Clock className="w-3 h-3 mr-1" />
            Idle
          </span>
        );
      case 'cooldown':
        return (
          <span className={`${baseClasses} bg-blue-100 text-blue-800`}>
            <Clock className="w-3 h-3 mr-1" />
            cooldown
          </span>
        );
      case 'restricted':
        return (
          <span className={`${baseClasses} bg-yellow-100 text-yellow-800`}>
            <AlertTriangle className="w-3 h-3 mr-1" />
            Restricted
          </span>
        );
      case 'suspended':
        return (
          <span className={`${baseClasses} bg-red-100 text-red-800`}>
            <XCircle className="w-3 h-3 mr-1" />
            Suspended
          </span>
        );
      default:
        return (
          <span className={`${baseClasses} bg-gray-100 text-gray-800`}>
            <AlertCircle className="w-3 h-3 mr-1" />
            Unknown
          </span>
        );
    }
  };

  // Improved Toggle Component
  const Toggle = ({ enabled, onChange, label }: { enabled: boolean, onChange: () => void, label: string }) => {
    return (
      <label className="flex items-center cursor-pointer">
        <div className="relative">
          <input
            type="checkbox"
            className="sr-only"
            checked={enabled}
            onChange={onChange}
          />
          <div
            className={`block w-14 h-8 rounded-full transition-colors duration-200 ease-in-out ${
              enabled ? 'bg-indigo-600' : 'bg-gray-200'
            }`}
          ></div>
          <div
            className={`absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition-transform duration-200 ease-in-out ${
              enabled ? 'transform translate-x-6' : 'transform translate-x-0'
            } shadow-md`}
          ></div>
        </div>
        <span className="ml-3 text-gray-700">{label}</span>
      </label>
    );
  };

  return (
    <div className="min-h-screen text-gray-800 overflow-x-hidden animate-gradient-slow"
    style={{
      backgroundImage:
        "linear-gradient(-45deg, #fef6e4, #e0f7fa, #fdf0ec, #e6f2f8)",
      backgroundSize: "200% 200%",
      animation: "gradientMove 15s ease infinite",
    }}>
      {/* Sticky Navbar */}
      <Navbar/>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Settings</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Global Scraper Configurations */}
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center mb-4">
              <Database className="h-6 w-6 mr-2 text-indigo-600" />
              <h2 className="text-lg font-semibold text-gray-900">Global Scraper Configurations</h2>
            </div>
            
            <div className="mb-4">
              <Toggle 
                enabled={enableMongoDB} 
                onChange={() => setEnableMongoDB(!enableMongoDB)}
                label="Enable MongoDB"
              />
            </div>
            
            {enableMongoDB && (
              <div className="space-y-4 mb-4 pl-4 border-l-2 border-indigo-200">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Host
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="localhost"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Port
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="27017"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Username
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Password
                  </label>
                  <input
                    type="password"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Database Name
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="scraper_db"
                  />
                </div>
              </div>
            )}
            
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Timeout (milliseconds)
                </label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="30000"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Retry Count
                </label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="3"
                />
              </div>
            </div>
            
            <button
              type="button"
              onClick={saveConfigurations}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Save Configurations
            </button>
          </div>
          
          {/* Account Rotation Settings */}
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center mb-4">
              <Clock className="h-6 w-6 mr-2 text-indigo-600" />
              <h2 className="text-lg font-semibold text-gray-900">Account Rotation Settings</h2>
            </div>
            
            <div className="mb-4">
              <Toggle 
                enabled={enableRotation} 
                onChange={() => setEnableRotation(!enableRotation)}
                label="Enable Account Rotation"
              />
            </div>
            
            {enableRotation && (
              <div className="space-y-4 mb-4 pl-4 border-l-2 border-indigo-200">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Rotation Interval (seconds)
                  </label>
                  <input
                    type="number"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="300"
                  />
                </div>
              </div>
            )}
            
            <button
              type="button"
              onClick={saveRotationSettings}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Save Rotation Settings
            </button>
          </div>
        </div>
        
        {/* Instagram Account Management */}
        <div className="mt-6 bg-white rounded-xl shadow p-6">
          <div className="flex items-center mb-4">
            <Instagram className="h-6 w-6 mr-2 text-indigo-600" />
            <h2 className="text-lg font-semibold text-gray-900">Instagram Account Management</h2>
          </div>
          
          <form onSubmit={addInstagramAccount} className="mb-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Username
                </label>
                <input
                  type="text"
                  value={newAccount.username}
                  onChange={(e) => setNewAccount({...newAccount, username: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="instagram_username"
                  required
                />
              </div>
              
              <div className="md:col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  value={newAccount.password}
                  onChange={(e) => setNewAccount({...newAccount, password: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="••••••••"
                  required
                />
              </div>
              
              <div className="md:col-span-1 flex items-end">
                <button
                  type="submit"
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Add Account
                </button>
              </div>
            </div>
          </form>
          
          <div className="mb-4 flex justify-between items-center">
            <div className="text-sm text-gray-500">
              {instagramAccounts.length === 0 ? (
                <span>No accounts added yet</span>
              ) : (
                <span>Showing {instagramAccounts.length} account{instagramAccounts.length !== 1 ? 's' : ''}</span>
              )}
            </div>
            <button
              onClick={loadAccounts}
              className="px-3 py-1.5 text-sm bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              Refresh Accounts
            </button>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Username
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ban Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Scraper Assignment
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {instagramAccounts.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-4 text-center text-sm text-gray-500">
                      No accounts found. Add a new account or refresh the list.
                    </td>
                  </tr>
                ) : (
                  instagramAccounts.map((account) => (
                    <tr key={account.id} className={account.pendingSave || account.pendingDelete ? 'bg-gray-50' : ''}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {account.username}
                        {!account.pendingSave && !account.id && (
                          <button
                            onClick={() => saveAccount(account)}
                            className="mr-4 text-indigo-600 hover:text-indigo-900"
                          >
                            Save
                          </button>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {getStatusBadge(account.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {account.banstatus || 'Unknown'}
                      </td>
                      {/* For existing accounts loaded from server */}
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {account.isNew ? (
                          // For newly added accounts, allow scraper selection
                          <select
                            value={account.scraper || ''}
                            onChange={(e) => {
                              const updatedAccounts = instagramAccounts.map(acc => 
                                acc.id === account.id 
                                  ? { ...acc, scraper: e.target.value || null } 
                                  : acc
                              );
                              setInstagramAccounts(updatedAccounts);
                            }}
                            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                          >
                            <option value="">Select Scraper</option>
                            <option value="scraper1">Scraper 1 (Web Driver)</option>
                            <option value="scraper2">Scraper 2 (Mobile API)</option>
                          </select>
                        ) : (
                          // For existing accounts, display as read-only text
                          <span className="text-gray-500">
                            {account.scraper ? 
                              (account.scraper === 'scraper1' ? 'Scraper 1 (Web Driver)' : 'Scraper 2 (Mobile API)') : 
                              'Not Assigned'}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        {account.isNew && !account.pendingSave && account.scraper && (
                          <button
                            onClick={() => saveAccount(account)}
                            className="mr-4 text-indigo-600 hover:text-indigo-900"
                          >
                            Save
                          </button>
                        )}
                        
                        {!account.pendingDelete && (
                          <button
                            onClick={() => removeAccount(account)}
                            disabled={account.pendingSave}
                            className={`text-red-600 hover:text-red-900 ${account.pendingSave ? 'opacity-50 cursor-not-allowed' : ''}`}
                          >
                            Remove
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
        
        {/* Live Terminal View */}
        <div className="mt-6 bg-white rounded-xl shadow p-6">
          <div className="flex items-center mb-4">
            <Terminal className="h-6 w-6 mr-2 text-indigo-600" />
            <h2 className="text-lg font-semibold text-gray-900">Live Terminal View</h2>
            <div className="ml-auto flex items-center">
              <div className={`w-3 h-3 rounded-full mr-2 ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-500">{wsStatus}</span>
              {!wsConnected && (
                <button
                  onClick={handleManualReconnect}
                  className="ml-3 px-3 py-1 text-xs bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  Reconnect
                </button>
              )}
            </div>
          </div>
          
          <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm text-green-400 h-64 overflow-y-auto" id="terminal-log">
            {terminalLogs.map((log, index) => (
              <div key={index} className="mb-1">
                {log.includes('[ERROR]') ? (
                  <span className="text-red-400">{log}</span>
                ) : log.includes('[WARN]') ? (
                  <span className="text-yellow-400">{log}</span>
                ) : log.includes('[PROCESS]') ? (
                  <span className="text-cyan-400">{log}</span>
                ) : (
                  <span>{log}</span>
                )}
              </div>
            ))}
          </div>
          
          <div className="mt-3 flex justify-between">
            <button
              onClick={() => setTerminalLogs([])}
              className="px-3 py-1.5 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Clear Terminal
            </button>
            
            <div className="flex space-x-2">
              <button
                onClick={loadAccounts}
                className="px-3 py-1.5 text-sm bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                Refresh Data
              </button>
              
              <button
                onClick={() => {
                  addLog('[INFO] Auto-scrolling to bottom of terminal');
                  document.getElementById('terminal-log')?.scrollTo(0, document.getElementById('terminal-log')?.scrollHeight || 0);
                }}
                className="px-3 py-1.5 text-sm bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                Scroll to Bottom
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}