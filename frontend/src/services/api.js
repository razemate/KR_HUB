const API_URL = import.meta.env.VITE_API_URL || '';

export const analyzeData = async (formData, token) => {
    const headers = {};
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // Use the modules prefix as defined in vercel.json rewrites
    const endpoint = API_URL ? `${API_URL}/api/chat-with-data/analyze` : '/api/chat-with-data/analyze';

    const response = await fetch(endpoint, {
        method: 'POST',
        headers: headers,
        body: formData
    });

    if (!response.ok) {
        let errorMessage = `Server responded with status ${response.status}. `;
        try {
            const errorData = await response.json();
            errorMessage += errorData.detail || "Server error occurred";
        } catch {
            errorMessage += "Unable to parse server error response";
        }
        throw new Error(errorMessage);
    }

    return response;
};
