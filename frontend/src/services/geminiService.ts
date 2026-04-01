/**
 * Gemini AI Service - Client-side AI Processing
 * Handles OCR Extraction and Final Medical Agent Analysis
 */

const GEMINI_API_KEY = import.meta.env.VITE_GEMINI_API_KEY;
const MODEL_NAME = 'gemini-1.5-flash';
const GEMINI_URL = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL_NAME}:generateContent?key=${GEMINI_API_KEY}`;

export interface ExtractionResult {
  patientInfo: {
    age?: number;
    gender?: string;
    name?: string;
  };
  testResults: Array<{
    testName: string;
    value: string;
    unit: string;
    normalRange?: string;
    isAbnormal: boolean;
  }>;
  symptoms: string[];
  vitals: Record<string, string | number>;
  diagnosis?: string;
  reportDate?: string;
  confidence: number;
}

export interface AnalysisResult {
  assessmentId: string;
  prediction: {
    disease: string;
    probability: number;
    confidence: 'LOW' | 'MEDIUM' | 'HIGH';
  };
  explanation: {
    text: string;
    keyFactors: string[];
  };
  recommendations: {
    immediateSteps: string[];
    lifestyleChanges: string[];
    specialistsToConsult: string[];
    urgency: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  };
  disclaimer: string;
}

export class GeminiService {
  /**
   * Extract structured medical data from a base64 encoded file (PDF/Image)
   */
  async extractFromReport(base64Data: string, mimeType: string): Promise<ExtractionResult> {
    const systemPrompt = `You are a professional Medical Document Parser. 
Extract structured information from the provided medical report.
Return ONLY a valid JSON object with the following structure:
{
  "patientInfo": { "age": number, "gender": "string", "name": "string" },
  "testResults": [
    { "testName": "string", "value": "string", "unit": "string", "normalRange": "string", "isAbnormal": boolean }
  ],
  "symptoms": ["string"],
  "vitals": { "bloodPressure": "string", "heartRate": number, "temperature": number },
  "diagnosis": "string",
  "reportDate": "ISO string",
  "confidence": number (0-1)
}
If a value is missing, use null. Analyze abnormal values based on standard ranges.`;

    try {
      const response = await fetch(GEMINI_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [
            {
              parts: [
                { text: systemPrompt },
                {
                  inline_data: {
                    mime_type: mimeType,
                    data: base64Data
                  }
                }
              ]
            }
          ],
          generationConfig: {
            response_mime_type: "application/json",
          }
        })
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error?.message || 'Gemini API Error');
      }

      const result = await response.json();
      const text = result.candidates[0].content.parts[0].text;
      return JSON.parse(text) as ExtractionResult;
    } catch (error) {
      console.error('OCR Extraction Failed:', error);
      throw error;
    }
  }

  /**
   * Final AI Agent analysis combining OCR results and NN predictions
   */
  async analyzeHealthCase(ocrData: ExtractionResult, nnPredictions: any[]): Promise<AnalysisResult> {
    const systemPrompt = `You are a Senior Medical AI Specialist. 
Analyze the following patient data:
1. OCR EXTRACTION: ${JSON.stringify(ocrData)}
2. NN PREDICTIONS: ${JSON.stringify(nnPredictions)}

Your task is to synthesize these results. Discuss how the lab results in the OCR report support or contradict the NN prediction.
Return ONLY a valid JSON object:
{
  "assessmentId": "string",
  "prediction": { "disease": "string", "probability": number, "confidence": "LOW|MEDIUM|HIGH" },
  "explanation": { "text": "string", "keyFactors": ["string"] },
  "recommendations": {
    "immediateSteps": ["string"],
    "lifestyleChanges": ["string"],
    "specialistsToConsult": ["string"],
    "urgency": "LOW|MEDIUM|HIGH|CRITICAL"
  },
  "disclaimer": "This is an AI-generated assessment. Always consult a human doctor."
}`;

    try {
      const response = await fetch(GEMINI_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: systemPrompt }] }],
          generationConfig: { response_mime_type: "application/json" }
        })
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error?.message || 'Gemini API Error');
      }

      const result = await response.json();
      const text = result.candidates?.[0]?.content?.parts?.[0]?.text;
      if (!text) throw new Error('Empty response from AI Agent');

      return JSON.parse(text) as AnalysisResult;
    } catch (error) {
      console.error('Final Analysis Failed:', error);
      throw error;
    }
  }
}

export const geminiAI = new GeminiService();
