import axios from "axios";

const API_BASE_URL = "/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor to attach JWT token to every protected request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for unified error formatting
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Token expired or unauthorized
      if (localStorage.getItem("token")) {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        if (window.location.pathname !== "/login" && window.location.pathname !== "/signup") {
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

// Types matching Flask response payloads
export interface User {
  id: number;
  name: string;
  email: string;
  created_at: string;
}

export interface DiagnosticCentre {
  id: number;
  name: string;
  location: string;
  created_at: string;
  tests?: DiagnosticTest[];
}

export interface DiagnosticTest {
  id: number;
  centre_id: number;
  name: string;
  description: string | null;
  price: string;
  created_at: string;
}

export interface Booking {
  id: number;
  user_id: number;
  test_id: number;
  centre_id: number;
  appointment_datetime: string;
  amount: string;
  status: "PENDING" | "CONFIRMED" | "CANCELLED" | "FAILED";
  created_at: string;
  updated_at: string;
}

export interface Payment {
  id: number;
  booking_id: number;
  external_payment_id: string;
  amount: string;
  status: "PENDING" | "SUCCESS" | "FAILED";
  created_at: string;
  updated_at: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  meta?: {
    page: number;
    per_page: number;
    total: number;
    total_pages: number;
  };
  error?: {
    code: string;
    message: string;
  };
}

// API Service Methods
export const authApi = {
  signup: async (data: { name: string; email: string; password: string }) => {
    const res = await api.post<ApiResponse<User>>("/auth/signup", data);
    return res.data;
  },
  login: async (data: { email: string; password: string }) => {
    const res = await api.post<ApiResponse<{ access_token: string; user: User }>>("/auth/login", data);
    return res.data;
  },
  me: async () => {
    const res = await api.get<ApiResponse<User>>("/auth/me");
    return res.data;
  },
};

export const centresApi = {
  list: async (page = 1, perPage = 50) => {
    const res = await api.get<ApiResponse<DiagnosticCentre[]>>(`/centres?page=${page}&per_page=${perPage}`);
    return res.data;
  },
  get: async (id: number) => {
    const res = await api.get<ApiResponse<DiagnosticCentre>>(`/centres/${id}`);
    return res.data;
  },
  listTests: async (centreId: number) => {
    const res = await api.get<ApiResponse<DiagnosticTest[]>>(`/centres/${centreId}/tests`);
    return res.data;
  },
};

export const testsApi = {
  get: async (id: number) => {
    const res = await api.get<ApiResponse<DiagnosticTest>>(`/tests/${id}`);
    return res.data;
  },
};

export const bookingsApi = {
  create: async (data: { test_id: number; centre_id: number; appointment_datetime: string }) => {
    const res = await api.post<ApiResponse<Booking>>("/bookings", data);
    return res.data;
  },
  list: async (page = 1, perPage = 50) => {
    const res = await api.get<ApiResponse<Booking[]>>(`/bookings?page=${page}&per_page=${perPage}`);
    return res.data;
  },
  get: async (id: number) => {
    const res = await api.get<ApiResponse<Booking>>(`/bookings/${id}`);
    return res.data;
  },
  cancel: async (id: number) => {
    const res = await api.post<ApiResponse<Booking>>(`/bookings/${id}/cancel`);
    return res.data;
  },
};

export const paymentsApi = {
  create: async (data: { booking_id: number; simulate_result?: "SUCCESS" | "FAILED" }) => {
    const res = await api.post<ApiResponse<{ payment: Payment; booking_status: string }>>("/payments", data);
    return res.data;
  },
};
