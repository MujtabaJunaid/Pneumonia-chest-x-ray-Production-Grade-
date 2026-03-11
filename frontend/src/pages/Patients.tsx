/**
 * Ù…Ø±ÛŒØ¶ÙˆÚº Ú©Ø§ ØµÙØ­Û
 * Patients Page Component
 */

import { useTranslation } from 'react-i18next';

export default function Patients() {
  const { t } = useTranslation();

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          {t('patient_info')}
        </h2>
        <p className="text-gray-600">
          ÛŒÛ ØµÙØ­Û Ù…Ø³ØªÙ‚Ø¨Ù„ Ù…ÛŒÚº ØªÙ…Ø§Ù… Ù…Ø±ÛŒØ¶ÙˆÚº Ú©ÛŒ Ù…Ø¹Ù„ÙˆÙ…Ø§Øª Ù…Ù†ÛŒØ¬ Ú©Ø±Û’ Ú¯Ø§Û”
        </p>
      </div>
    </div>
  );
}
