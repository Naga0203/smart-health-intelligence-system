// ============================================================================
// AI Health Intelligence Platform - Type Definitions (JSDoc)
// ============================================================================

/**
 * @typedef {Object} User
 * @property {string} uid
 * @property {string} email
 * @property {string|null} displayName
 * @property {string|null} photoURL
 */

/**
 * @typedef {Object} AuthState
 * @property {User|null} user
 * @property {string|null} token
 * @property {boolean} loading
 * @property {string|null} error
 */

/**
 * @typedef {Object} UserProfile
 * @property {string} uid
 * @property {string} email
 * @property {string} [display_name]
 * @property {string} [photo_url]
 * @property {boolean} email_verified
 * @property {string} created_at
 * @property {string} updated_at
 * @property {string} last_login
 * @property {string} [phone_number]
 * @property {string} [date_of_birth]
 * @property {'male'|'female'|'other'|'prefer_not_to_say'} [gender]
 * @property {Object} [address]
 * @property {Object} [emergency_contact]
 * @property {string[]} [medical_history]
 * @property {string[]} [allergies]
 * @property {string[]} [current_medications]
 */

/**
 * @typedef {Object} UserStatistics
 * @property {number} total_assessments
 * @property {Object} assessments_by_confidence
 * @property {number} assessments_by_confidence.LOW
 * @property {number} assessments_by_confidence.MEDIUM
 * @property {number} assessments_by_confidence.HIGH
 * @property {Array<{disease: string, count: number}>} most_common_diseases
 * @property {string|null} last_assessment_date
 * @property {number} account_age_days
 */

/**
 * @typedef {Object} SymptomDuration
 * @property {number} value
 * @property {'hours'|'days'|'weeks'|'months'} unit
 */

/**
 * @typedef {Object} SymptomInput
 * @property {string} name
 * @property {number} severity - Range 1-10
 * @property {SymptomDuration} duration
 */

/**
 * @typedef {Object} DemographicData
 * @property {number} age
 * @property {'male'|'female'|'other'} gender
 * @property {string[]} [medical_history]
 */

/**
 * @typedef {Object} VitalsData
 * @property {number} [temperature]
 * @property {number} [blood_pressure_systolic]
 * @property {number} [blood_pressure_diastolic]
 * @property {number} [heart_rate]
 * @property {number} [respiratory_rate]
 */

/**
 * @typedef {Object} AssessmentRequest
 * @property {string[]} symptoms
 * @property {number} age
 * @property {'male'|'female'|'other'} gender
 * @property {Object} [additional_info]
 */

/**
 * @typedef {Object} RiskDriver
 * @property {string} factor
 * @property {number} contribution - Percentage contribution
 * @property {string} description
 */

/**
 * @typedef {Object} RiskAssessment
 * @property {string} id
 * @property {string} status
 * @property {'LOW'|'MEDIUM'|'HIGH'} confidence
 * @property {number} confidenceScore - Range 0-100
 * @property {string} message
 * @property {string} [user_id]
 * @property {string} assessment_id
 * @property {string} condition - Primary condition/disease
 * @property {'low'|'medium'|'elevated'|'high'} riskLevel
 * @property {number} probability - Range 0-100
 * @property {string} interpretation
 * @property {RiskDriver[]} riskDrivers
 * @property {number} dataQualityScore - Range 0-100
 * @property {string} timestamp
 * @property {Object} prediction
 * @property {string} prediction.disease
 * @property {number} prediction.probability
 * @property {number} prediction.probability_percent
 * @property {'LOW'|'MEDIUM'|'HIGH'} prediction.confidence
 * @property {string} [prediction.model_version]
 * @property {Object} [extraction]
 * @property {number} [extraction.confidence]
 * @property {string} [extraction.method]
 * @property {string[]} [extraction.extracted_features]
 * @property {Object} [explanation]
 * @property {string} [explanation.text]
 * @property {string} [explanation.generated_by]
 * @property {'LOW'|'MEDIUM'|'HIGH'} [explanation.confidence]
 * @property {Object} [recommendations]
 * @property {string[]} [recommendations.items]
 * @property {'low'|'medium'|'high'} [recommendations.urgency]
 * @property {'LOW'|'MEDIUM'|'HIGH'} [recommendations.confidence]
 * @property {TreatmentInfo} [treatment_info]
 * @property {string[]} [risk_factors]
 * @property {string} disclaimer
 * @property {Object} metadata
 * @property {number} [metadata.processing_time_seconds]
 * @property {string} metadata.timestamp
 * @property {Object} [metadata.storage_ids]
 * @property {string} [metadata.pipeline_version]
 */

/**
 * @typedef {Object} TreatmentDetail
 * @property {string} category
 * @property {string[]} recommendations
 * @property {string} notes
 * @property {string} [approach]
 * @property {string} [focus]
 * @property {string} [disclaimer]
 */

/**
 * @typedef {Object} TreatmentInfo
 * @property {TreatmentDetail[]} [allopathy]
 * @property {TreatmentDetail[]} [ayurveda]
 * @property {TreatmentDetail[]} [homeopathy]
 * @property {TreatmentDetail[]} [lifestyle]
 */

/**
 * @typedef {Object} Assessment
 * @property {string} id
 * @property {string} date
 * @property {string} condition
 * @property {string} riskLevel
 * @property {string} confidence
 * @property {number} probability
 */

/**
 * @typedef {Object} AssessmentHistoryItem
 * @property {string} id
 * @property {string} created_at
 * @property {string} disease
 * @property {number} probability
 * @property {'LOW'|'MEDIUM'|'HIGH'} confidence
 * @property {string[]} symptoms
 * @property {string} status
 */

/**
 * @typedef {Object} AssessmentHistory
 * @property {number} total
 * @property {number} page
 * @property {number} page_size
 * @property {AssessmentHistoryItem[]} assessments
 */

/**
 * @typedef {Object} SystemStatus
 * @property {'operational'|'degraded'|'error'} status
 * @property {string} version
 * @property {Object} components
 * @property {Object} [components.orchestrator]
 * @property {string} [components.orchestrator.status]
 * @property {string} [components.orchestrator.version]
 * @property {Object} [components.predictor]
 * @property {string} [components.predictor.status]
 * @property {number} [components.predictor.models_loaded]
 * @property {Object} [components.database]
 * @property {string} [components.database.status]
 * @property {string} [components.database.type]
 * @property {Object} [components.gemini_ai]
 * @property {string} [components.gemini_ai.status]
 * @property {string} timestamp
 */

/**
 * @typedef {Object} ModelInfo
 * @property {boolean} model_loaded
 * @property {string} model_type
 * @property {number} num_features
 * @property {number} num_diseases
 * @property {string} [device]
 */

/**
 * @typedef {Object} Disease
 * @property {string} name
 * @property {string} [category]
 * @property {string[]} [symptoms]
 */

/**
 * @typedef {Object} DiseasesResponse
 * @property {number} total
 * @property {string[]} diseases
 */

/**
 * @typedef {Object} Prediction
 * @property {string} disease
 * @property {number} probability
 * @property {number} rank
 */

/**
 * @typedef {Object} Notification
 * @property {string} id
 * @property {'info'|'warning'|'error'|'success'} type
 * @property {string} message
 * @property {boolean} dismissible
 * @property {string} timestamp
 */

/**
 * @typedef {Object} APIError
 * @property {string} error
 * @property {string} message
 * @property {*} [details]
 * @property {number} status_code
 * @property {number} [wait_seconds]
 */

/**
 * @template T
 * @typedef {Object} PaginatedResponse
 * @property {number} count
 * @property {string|null} next
 * @property {string|null} previous
 * @property {T[]} results
 */

export {};
