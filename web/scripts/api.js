export const API_URL = import.meta.env.PROD ? "https://edu-graph-api-575953891979.europe-west3.run.app" : "http://localhost:8080"

export const CLASSIFY_URL = `${API_URL}/classify`
export const ONTOLOGY_URL = `${API_URL}/ontology`
