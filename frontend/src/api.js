/**
 * Clean native fetch API client for PromptShield X Backend.
 */

const API_BASE = "http://127.0.0.1:8000";

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const defaultHeaders = {
    "Content-Type": "application/json",
  };

  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    });

    if (!res.ok) {
      let errDetail = `Server error (${res.status})`;
      try {
        const errJson = await res.json();
        errDetail = errJson.detail || errDetail;
      } catch (e) {
        // fallback to status text
      }
      throw new Error(errDetail);
    }

    return await res.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

export const api = {
  checkHealth: () => request("/health"),

  inspectContent: ({ task, content, sourceType = "User Prompt", forceDegraded = false }) =>
    request("/inspect", {
      method: "POST",
      body: JSON.stringify({
        task,
        content,
        source_type: sourceType,
        force_detector_degraded: forceDegraded,
      }),
    }),

  getPolicies: () => request("/policies"),

  updatePolicies: (settings, version = "v2.1") =>
    request("/policies", {
      method: "PUT",
      body: JSON.stringify({ version, settings }),
    }),

  getHistory: ({ limit = 50, search = "", decision = "" } = {}) => {
    const params = new URLSearchParams();
    if (limit) params.set("limit", limit.toString());
    if (search) params.set("search", search);
    if (decision && decision !== "ALL") params.set("decision", decision);
    return request(`/history?${params.toString()}`);
  },

  getInspectionDetails: (id) => request(`/inspections/${id}`),

  getReviews: () => request("/reviews"),

  submitReview: ({ inspectionId, action, reviewer = "security_lead", notes = "" }) =>
    request("/review", {
      method: "POST",
      body: JSON.stringify({
        inspection_id: inspectionId,
        reviewer,
        action,
        notes,
      }),
    }),

  runAssistant: ({ inspectionId, task }) =>
    request("/assistant/run", {
      method: "POST",
      body: JSON.stringify({
        inspection_id: inspectionId,
        task,
      }),
    }),

  checkAction: ({ toolName, toolArgs, inspectionId = null, authorizedTask = "", targetDestination = null }) =>
    request("/actions/check", {
      method: "POST",
      body: JSON.stringify({
        tool_name: toolName,
        tool_args: toolArgs,
        inspection_id: inspectionId,
        authorized_task: authorizedTask,
        target_destination: targetDestination,
      }),
    }),

  getLatestEvaluation: () => request("/evaluation/latest"),
};
