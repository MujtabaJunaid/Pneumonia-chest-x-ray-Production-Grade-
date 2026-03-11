/**
 * Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒÙˆÚº Ú©Ø§ ØµÙØ­Û
 * Predictions Page Component
 */

import { useTranslation } from 'react-i18next';

export default function Predictions() {
  const { t } = useTranslation();

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          {t('result')}
        </h2>
        <p className="text-gray-600">
          ÛŒÛ ØµÙØ­Û Ù…Ø³ØªÙ‚Ø¨Ù„ Ù…ÛŒÚº ØªÙ…Ø§Ù… Ù¾ÛŒØ´Ù†Ú¯ÙˆØ¦ÛŒÙˆÚº Ú©ÛŒ Ø³Ø§Ø¨Ù‚Û ØªØ§Ø±ÛŒØ® Ø¯Ú©Ú¾Ø§Ø¦Û’ Ú¯Ø§Û”
        </p>
      </div>
    </div>
  );
}
