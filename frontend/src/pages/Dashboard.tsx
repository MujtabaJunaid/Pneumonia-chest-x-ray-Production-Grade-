/**
 * ÚˆÛŒØ´ Ø¨ÙˆØ±Úˆ ØµÙØ­Û
 * Dashboard Component - Main Analysis Interface
 */

import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { uploadPrediction, PredictionResponse, ApiError } from '../api/client';

export default function Dashboard() {
  const { t, i18n } = useTranslation();
  const isUrdu = i18n.language === 'ur';

  // States
  const [patientId, setPatientId] = useState<string>('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [fileName, setFileName] = useState<string>('');

  // ØªØ¨Ø¯ÛŒÙ„ Ú©Ø±ÛŒÚº document Ú©ÛŒ Ø³Ù…Øª (RTL/LTR)
  useEffect(() => {
    document.documentElement.dir = isUrdu ? 'rtl' : 'ltr';
  }, [isUrdu]);

  // ÙØ§Ø¦Ù„ Ù…Ù†ØªØ®Ø¨ ÛÙˆÙ†Û’ Ù¾Ø±
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];

    if (!selectedFile) {
      setFile(null);
      setFileName('');
      return;
    }

    // ÙØ§Ø¦Ù„ Ú©ÛŒ Ù‚Ø³Ù… Ú©ÛŒ Ø¬Ø§Ù†Ú† Ú©Ø±ÛŒÚº
    const validTypes = ['image/png', 'image/jpeg', 'application/dicom'];
    const isValidType =
      validTypes.includes(selectedFile.type) ||
      selectedFile.name.toLowerCase().endsWith('.dcm') ||
      selectedFile.name.toLowerCase().endsWith('.png') ||
      selectedFile.name.toLowerCase().endsWith('.jpg') ||
      selectedFile.name.toLowerCase().endsWith('.jpeg');

    if (!isValidType) {
      setError(t('invalid_file'));
      setFile(null);
      setFileName('');
      return;
    }

    setFile(selectedFile);
    setFileName(selectedFile.name);
    setError(null);
    console.log(`âœ… ÙØ§Ø¦Ù„ Ù…Ù†ØªØ®Ø¨: ${selectedFile.name}`);
  };

  // ÚˆØ±ÛŒÚ¯ Ø§ÙˆØ± ÚˆØ±Ø§Ù¾ ÛÛŒÙ†ÚˆÙ„Ø±
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();

    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles.length > 0) {
      const droppedFile = droppedFiles[0];
      setFile(droppedFile);
      setFileName(droppedFile.name);
      setError(null);
      console.log(`âœ… ÚˆØ±Ø§Ù¾ Ú©ÛŒ Ú¯Ø¦ÛŒ ÙØ§Ø¦Ù„: ${droppedFile.name}`);
    }
  };

  // ÙØ§Ø±Ù… Ø¬Ù…Ø¹ Ú©Ø±ÛŒÚº
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);

    // ØªØµØ¯ÛŒÙ‚ Ú©Ø±ÛŒÚº
    if (!patientId.trim()) {
      setError(t('patient_id_required'));
      return;
    }

    if (!file) {
      setError(t('file_required'));
      return;
    }

    setLoading(true);
    console.log('ðŸ”¬ ØªØ¬Ø²ÛŒÛ Ø´Ø±ÙˆØ¹...');

    try {
      const response = await uploadPrediction(parseInt(patientId), file);
      setResult(response);
      console.log('âœ… ØªØ¬Ø²ÛŒÛ Ù…Ú©Ù…Ù„:', response);
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.details || apiError.message);
      console.error('âŒ ØªØ¬Ø²ÛŒÛ Ù…ÛŒÚº Ø®Ø±Ø§Ø¨ÛŒ:', apiError);
    } finally {
      setLoading(false);
    }
  };

  // Ù†ÛŒØ§ ØªØ¬Ø²ÛŒÛ Ø´Ø±ÙˆØ¹ Ú©Ø±ÛŒÚº
  const handleNewAnalysis = () => {
    setPatientId('');
    setFile(null);
    setFileName('');
    setError(null);
    setResult(null);
    console.log('ðŸ”„ Ù†ÛŒØ§ ØªØ¬Ø²ÛŒÛ');
  };

  return (
    <div className={`min-h-screen ${isUrdu ? 'rtl' : 'ltr'}`}>
      {/* Ø§Ú¯Ø± Ù†ØªÛŒØ¬Û Ù…ÙˆØ¬ÙˆØ¯ ÛÛ’ ØªÙˆ Ù†ØªØ§Ø¦Ø¬ Ú©Ø§Ø±Úˆ Ø¯Ú©Ú¾Ø§Ø¦ÛŒÚº */}
      {result && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <ResultsCard result={result} onNewAnalysis={handleNewAnalysis} />
        </div>
      )}

      {/* Ù…Ø±Ú©Ø²ÛŒ ÙØ§Ø±Ù… */}
      <div className="max-w-2xl mx-auto p-6">
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
          {/* ÛÛŒÚˆØ± */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {t('app_title')}
            </h1>
            <p className="text-gray-600">{t('app_subtitle')}</p>
          </div>

          {/* Ø®Ø±Ø§Ø¨ÛŒ Ú©Ø§ Ù¾ÛŒØºØ§Ù… */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded">
              <p className="text-red-700 font-semibold flex items-center gap-2">
                <span className="text-xl">âš ï¸</span>
                {error}
              </p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Ù…Ø±ÛŒØ¶ ID */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {t('patient_id')} *
              </label>
              <input
                type="number"
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
                placeholder={t('patient_id_placeholder')}
                disabled={loading}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 transition disabled:bg-gray-100"
              />
            </div>

            {/* ÙØ§Ø¦Ù„ Ø§Ù¾ Ù„ÙˆÚˆ - ÚˆØ±ÛŒÚ¯ Ø§ÙˆØ± ÚˆØ±Ø§Ù¾ */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {t('upload_image')} *
              </label>
              <div
                onDragOver={handleDragOver}
                onDrop={handleDrop}
                className="relative border-3 border-dashed border-blue-300 rounded-lg p-8 text-center hover:border-blue-500 hover:bg-blue-50 transition cursor-pointer bg-blue-50"
              >
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept=".png,.jpg,.jpeg,.dcm,image/png,image/jpeg,application/dicom"
                  disabled={loading}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />

                <div className="pointer-events-none">
                  {fileName ? (
                    <div>
                      <p className="text-2xl mb-2">ðŸ“·</p>
                      <p className="text-green-600 font-semibold">{fileName}</p>
                      <p className="text-sm text-gray-500 mt-2">
                        {t('drag_drop')}
                      </p>
                    </div>
                  ) : (
                    <div>
                      <p className="text-3xl mb-2">ðŸ“</p>
                      <p className="text-gray-700 font-semibold mb-1">
                        {t('upload_prompt')}
                      </p>
                      <p className="text-sm text-gray-500">{t('drag_drop')}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Ø¨Ù¹Ù† */}
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={loading || !patientId || !file}
                className={`flex-1 py-3 px-6 rounded-lg font-semibold transition flex items-center justify-center gap-2 ${
                  loading || !patientId || !file
                    ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95'
                }`}
              >
                {loading ? (
                  <>
                    <span className="animate-spin">âš™ï¸</span>
                    {t('loading')}
                  </>
                ) : (
                  <>
                    <span>ðŸ”¬</span>
                    {t('analyze_btn')}
                  </>
                )}
              </button>

              {file && (
                <button
                  type="button"
                  onClick={() => {
                    setFile(null);
                    setFileName('');
                  }}
                  disabled={loading}
                  className="px-6 py-3 border-2 border-red-300 text-red-600 rounded-lg font-semibold hover:bg-red-50 transition disabled:opacity-50"
                >
                  {t('cancel_btn')}
                </button>
              )}
            </div>
          </form>

          {/* ØªÙ„Ù…ÙŠØ­Ø§Øª */}
          <div className="mt-8 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
            <p className="text-sm text-gray-700">
              <span className="font-semibold">ðŸ’¡ Ù¹Ù¾:</span> ÛŒÙ‚ÛŒÙ†ÛŒ Ø¨Ù†Ø§Ø¦ÛŒÚº Ú©Û X-Ray
              ÙˆØ§Ø¶Ø­ Ø§ÙˆØ± ØµØ­ÛŒØ­ Ø·Ø±ÛŒÙ‚Û’ Ø³Û’ Ù„ÛŒØ§ Ú¯ÛŒØ§ ÛÛ’ Ø¨ÛØªØ±ÛŒÙ† Ù†ØªØ§Ø¦Ø¬ Ú©Û’ Ù„ÛŒÛ’Û”
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Ù†ØªØ§Ø¦Ø¬ Ú©Ø§Ø±Úˆ
 * Results Card Component
 */
interface ResultsCardProps {
  result: PredictionResponse;
  onNewAnalysis: () => void;
}

function ResultsCard({ result, onNewAnalysis }: ResultsCardProps) {
  const { t, i18n } = useTranslation();
  const isUrdu = i18n.language === 'ur';
  const isNormal = result.class_index === 0;

  return (
    <div className={`bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full ${isUrdu ? 'rtl' : 'ltr'}`}>
      {/* ÛÛŒÚˆØ± */}
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {t('success')}
        </h2>
        <p className="text-gray-600">{t('analysis_result')}</p>
      </div>

      {/* Ù†ØªÛŒØ¬Û - Ø±Ù†Ú¯ÛŒÙ† */}
      <div
        className={`p-6 rounded-xl mb-6 text-center ${
          isNormal
            ? 'bg-green-50 border-2 border-green-300'
            : 'bg-red-50 border-2 border-red-300'
        }`}
      >
        <p className="text-lg font-semibold mb-2">
          {isNormal ? 'âœ…' : 'âš ï¸'}
        </p>
        <p
          className={`text-3xl font-bold ${
            isNormal ? 'text-green-600' : 'text-red-600'
          }`}
        >
          {result.status_message}
        </p>
      </div>

      {/* ØªÙØµÛŒÙ„Ø§Øª */}
      <div className="space-y-4 mb-6">
        {/* Ø§Ø¹ØªÙ…Ø§Ø¯ */}
        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
          <span className="text-gray-700 font-semibold">{t('confidence')}:</span>
          <span className={`text-xl font-bold ${
            isNormal ? 'text-green-600' : 'text-red-600'
          }`}>
            {result.confidence_score.toFixed(2)}%
          </span>
        </div>

        {/* ÙˆÙ‚Øª */}
        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
          <span className="text-gray-700 font-semibold">
            {t('inference_time')}:
          </span>
          <span className="text-lg font-semibold text-blue-600">
            {result.inference_time_ms} {t('inference_time_unit')}
          </span>
        </div>

        {/* ID */}
        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
          <span className="text-gray-700 font-semibold">
            {t('patient_id')}:
          </span>
          <span className="text-lg font-semibold text-gray-700">
            #{result.patient_id}
          </span>
        </div>

        {/* Prediction ID */}
        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg text-sm">
          <span className="text-gray-600">Analysis ID:</span>
          <span className="text-gray-600">#{result.prediction_id}</span>
        </div>
      </div>

      {/* Ø¨Ù¹Ù† */}
      <button
        onClick={onNewAnalysis}
        className="w-full py-3 px-6 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition active:scale-95"
      >
        {t('new_analysis')}
      </button>
    </div>
  );
}
