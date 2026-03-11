/**
 * i18next Ú©ÛŒ ØªØ±ØªÛŒØ¨
 * i18next Configuration for English and Urdu
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import enTranslations from './locales/en.json';
import urTranslations from './locales/ur.json';

// Ø§Ø±Ø¯Ùˆ Ú©Ùˆ Ù†Ù…ÙˆÙ†Û’ Ú©Û’ Ø·ÙˆØ± Ù¾Ø± ØªØ±ØªÛŒØ¨ Ø¯ÛŒÚº
const resources = {
  en: {
    translation: enTranslations,
  },
  ur: {
    translation: urTranslations,
  },
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en', // ÚˆÛŒÙØ§Ù„Ù¹ Ø²Ø¨Ø§Ù†
    fallbackLng: 'en',
    
    interpolation: {
      escapeValue: false, // React Ø§Ù¾Ù†Û’ Ø¢Ù¾ Ú©Ùˆ Ø¨Ú†Ø§ØªØ§ ÛÛ’ XSS Ø³Û’
    },
    
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
  });

export default i18n;
