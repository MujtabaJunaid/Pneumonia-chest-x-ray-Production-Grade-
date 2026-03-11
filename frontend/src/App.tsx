/**

 * Main Application Component
 */

import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import Dashboard from './pages/Dashboard';
import { checkHealth } from './api/client';

export default function App() {
  const { t, i18n } = useTranslation();
  const isUrdu = i18n.language === 'ur';
  const [isConnected, setIsConnected] = useState(false);

  // Check backend health on mount and every 30 seconds
  useEffect(() => {
    const checkBackend = async () => {
      const connected = await checkHealth();
      setIsConnected(connected);
    };

    checkBackend();
    // Recheck every 30 seconds
    const interval = setInterval(checkBackend, 30000);
    return () => clearInterval(interval);
  }, []);

  // Toggle language
  const toggleLanguage = () => {
    const newLang = i18n.language === 'en' ? 'ur' : 'en';
    i18n.changeLanguage(newLang);
    localStorage.setItem('language', newLang);
    document.documentElement.dir = newLang === 'ur' ? 'rtl' : 'ltr';
  };

  return (
    <div className={`min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 ${isUrdu ? 'rtl' : 'ltr'}`}>
      {/* Navigation bar */}
      <nav className="bg-white shadow-md border-b-4 border-blue-600">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            {/* Logo and title */}
            <div className="flex items-center gap-3">
              <div className="text-3xl">ðŸ¥</div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {t('app_title')}
                </h1>
                <p className="text-xs text-gray-500">
                  {t('app_subtitle')}
                </p>
              </div>
            </div>

            {/* Right side: status and language */}
            <div className="flex items-center gap-4">
              {/* Health status */}
              <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-50">
                <div
                  className={`w-2 h-2 rounded-full ${
                    isConnected ? 'bg-green-500' : 'bg-red-500'
                  } animate-pulse`}
                ></div>
                <span className="text-sm font-semibold text-gray-700">
                  {isConnected
                    ? t('connected')
                    : t('disconnected')}
                </span>
              </div>

              {/* Language button */}
              <button
                onClick={toggleLanguage}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold flex items-center gap-2"
              >
                <span>{isUrdu ? 'ðŸ‡¬ðŸ‡§' : 'ðŸ‡µðŸ‡°'}</span>
                {isUrdu ? 'English' : 'Ø§Ø±Ø¯Ùˆ'}
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Ù…Ø±Ú©Ø²ÛŒ Ù…ÙˆØ§Ø¯ */}
      <main className="py-12">
        <Dashboard />
      </main>

      {/* ÙÙˆÙ¹Ø± */}
      <footer className="bg-gray-900 text-gray-300 py-8 mt-16">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p className="text-sm">
            {isUrdu
              ? 'Â© 2026 Ù†Ù…ÙˆÙ†ÛŒØ§ Ø§Û’ Ø¢Ø¦ÛŒ ÚˆÛŒÙ¹ÛŒÚ©Ù¹Ø±Û” ØªÙ…Ø§Ù… Ø­Ù‚ÙˆÙ‚ Ù…Ø­ÙÙˆØ¸ ÛÛŒÚºÛ”'
              : 'Â© 2026 Pneumonia AI Detector. All rights reserved.'}
          </p>
          <p className="text-xs text-gray-500 mt-2">
            {isUrdu
              ? 'ØµØ±Ù Ø·Ø¨ÛŒ Ù…Ø´Ø§ÙˆØ±Øª Ú©Û’ Ù„ÛŒÛ’Û” Ù„Ø§Ø²Ù…Ø§Ù‹ ÚˆØ§Ú©Ù¹Ø± Ú©ÛŒ ØªØ§Ø¦ÛŒØ¯ Ø­Ø§ØµÙ„ Ú©Ø±ÛŒÚºÛ”'
              : 'For educational purposes only. Always consult a medical professional.'}
          </p>
        </div>
      </footer>
    </div>
  );
}
